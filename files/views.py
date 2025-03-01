from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.exceptions import SuspiciousFileOperation
from django.views.generic import TemplateView

import os
import json
import logging
from datetime import datetime, timedelta

from .models import FileRecord, DownloadRecord, DownloadableFile
from .forms import FileUploadForm

logger = logging.getLogger(__name__)
download_logger = logging.getLogger('download')
upload_logger = logging.getLogger('upload')

class HomeView(TemplateView):
    """ホームページ（サイドバーのみ）"""
    template_name = 'files/home.html'


def download_view(request):
    """ダウンロード画面"""
    # ダウンロードディレクトリからファイルをスキャン・更新
    DownloadableFile.scan_directory()
    
    # ダウンロード可能なファイルを取得
    files = DownloadableFile.objects.all().order_by('-last_modified')
    
    return render(request, 'files/download.html', {
        'files': files,
        'active_menu': 'download'
    })


def upload_view(request):
    """アップロード画面"""
    form = FileUploadForm()
    return render(request, 'files/upload.html', {
        'form': form,
        'active_menu': 'upload'
    })


def download_file(request, file_id):
    """ファイルダウンロード処理"""
    downloadable_file = get_object_or_404(DownloadableFile, id=file_id)
    
    # 社員コードのチェック
    employee_code = request.GET.get('employee_code')
    if not employee_code:
        logger.warning(f"社員コードなしでのダウンロード試行: {downloadable_file.filename}")
        download_logger.warning(f"社員コードなしでのダウンロード試行: {downloadable_file.filename}")
        return HttpResponse("社員コードを入力してください。", status=400)
    
    try:
        # ファイルが存在するか確認
        if not os.path.exists(downloadable_file.filepath):
            logger.error(f"ダウンロードファイルが見つかりません: {downloadable_file.filepath}")
            download_logger.error(f"ダウンロードファイルが見つかりません: {downloadable_file.filepath}")
            return HttpResponse("ファイルが見つかりません。", status=404)
            
        # ダウンロード記録
        download_record = DownloadRecord.objects.create(
            file=downloadable_file,
        )
        download_record.employee_code = employee_code
        download_record.save()
        
        # ダウンロード状態を更新
        downloadable_file.is_downloaded = True
        downloadable_file.last_downloaded_at = timezone.now()
        downloadable_file.save()
        
        logger.info(f"ファイルダウンロード: {downloadable_file.filename}, ID: {file_id}, 社員コード: {employee_code}")
        download_logger.info(f"ファイルダウンロード: {downloadable_file.filename}, ID: {file_id}, 社員コード: {employee_code}")
        
        # ファイルをレスポンスとして返す
        response = FileResponse(open(downloadable_file.filepath, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{downloadable_file.filename}"'
        return response
    except Exception as e:
        logger.error(f"ダウンロードエラー: {downloadable_file.filename}, エラー: {str(e)}")
        download_logger.error(f"ダウンロードエラー: {downloadable_file.filename}, エラー: {str(e)}")
        return HttpResponse("ファイルのダウンロード中にエラーが発生しました。", status=500)


@csrf_exempt
@require_POST
def upload_file(request):
    """AJAX ファイルアップロード処理"""
    try:
        # POSTデータの取得
        employee_code = request.POST.get('employee_code')
        uploaded_file = request.FILES.get('file')
        
        if not employee_code or not uploaded_file:
            return JsonResponse({
                'status': 'error',
                'message': '社員コードとファイルが必要です'
            }, status=400)
        
        # ファイルサイズのチェック（3GB上限）
        max_size = 3 * 1024 * 1024 * 1024  # 3GB in bytes
        if uploaded_file.size > max_size:
            return JsonResponse({
                'status': 'error',
                'message': 'ファイルサイズが上限（3GB）を超えています'
            }, status=400)
        
        with transaction.atomic():
            # ファイルの保存
            file_record = FileRecord.objects.create(
                file=uploaded_file,
                original_filename=uploaded_file.name,
                file_size=uploaded_file.size,
                employee_code=employee_code
            )
            
            logger.info(f"ファイルアップロード成功: {uploaded_file.name}, サイズ: {uploaded_file.size} bytes, 社員コード: {employee_code}")
            upload_logger.info(f"ファイルアップロード成功: {uploaded_file.name}, サイズ: {uploaded_file.size} bytes, 社員コード: {employee_code}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'ファイルが正常にアップロードされました',
                'file_id': file_record.id,
                'filename': file_record.original_filename,
                'file_size': file_record.file_size,
                'uploaded_at': file_record.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
    except SuspiciousFileOperation as e:
        logger.error(f"不正なファイル操作: {str(e)}")
        upload_logger.error(f"不正なファイル操作: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': '不正なファイル操作です'
        }, status=400)
    except Exception as e:
        logger.error(f"アップロードエラー: {str(e)}")
        upload_logger.error(f"アップロードエラー: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'ファイルのアップロード中にエラーが発生しました: {str(e)}'
        }, status=500)


def get_files_list(request):
    """AJAX 更新ファイルリスト取得"""
    try:
        # ダウンロードディレクトリからファイルをスキャン・更新
        DownloadableFile.scan_directory()
        
        files = DownloadableFile.objects.all().order_by('-last_modified')
        
        data = [{
            'id': file.id,
            'filename': file.filename,
            'file_size': file.file_size,
            'last_modified': file.last_modified.strftime('%Y-%m-%d %H:%M:%S'),
            'is_downloaded': file.is_downloaded,
            'last_downloaded_at': file.last_downloaded_at.strftime('%Y-%m-%d %H:%M:%S') if file.last_downloaded_at else None,
        } for file in files]
        
        return JsonResponse({
            'status': 'success',
            'files': data
        })
    except Exception as e:
        logger.error(f"ファイルリスト取得エラー: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'ファイルリストの取得中にエラーが発生しました'
        }, status=500)


def get_uploaded_files_list(request):
    """AJAX アップロードファイルリスト取得"""
    try:
        files = FileRecord.objects.all().order_by('-uploaded_at')
        
        data = [{
            'id': file.id,
            'filename': file.original_filename,
            'file_size': file.file_size,
            'uploaded_at': file.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            'employee_code': file.employee_code,
        } for file in files]
        
        return JsonResponse({
            'status': 'success',
            'files': data
        })
    except Exception as e:
        logger.error(f"アップロードファイルリスト取得エラー: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'アップロードファイルリストの取得中にエラーが発生しました'
        }, status=500)


def master_view(request):
    """マスター管理画面
    以下を表示:
    - ダウンロードフォルダの一覧
    - アップロードフォルダの一覧
    - 全ログ、アップロードログ、ダウンロードログ
    """
    # ダウンロードファイル一覧を実際のフォルダから取得
    download_files = []
    download_dir = settings.DOWNLOAD_DIR
    
    if os.path.exists(download_dir):
        for filename in os.listdir(download_dir):
            filepath = os.path.join(download_dir, filename)
            if os.path.isfile(filepath):
                file_stat = os.stat(filepath)
                file_size = file_stat.st_size
                last_modified = timezone.make_aware(datetime.fromtimestamp(file_stat.st_mtime))
                
                # データベースからダウンロード情報を検索（ファイルパスで一致するものを探す）
                db_file = DownloadableFile.objects.filter(filepath=filepath).first()
                
                is_downloaded = False
                last_downloaded_at = None
                id = None
                
                if db_file:
                    is_downloaded = db_file.is_downloaded
                    last_downloaded_at = db_file.last_downloaded_at
                    id = db_file.id
                else:
                    id = 0  # データベースに未登録の場合
                
                download_files.append({
                    'id': id,
                    'filename': filename,
                    'filepath': filepath,
                    'file_size': file_size,
                    'last_modified': last_modified,
                    'is_downloaded': is_downloaded,
                    'last_downloaded_at': last_downloaded_at
                })
    
    # 最終更新日時の降順でソート
    download_files.sort(key=lambda x: x['last_modified'], reverse=True)
    
    # アップロードファイル一覧を実際のフォルダから取得
    upload_files = []
    upload_dir = settings.UPLOAD_DIR
    
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            filepath = os.path.join(upload_dir, filename)
            if os.path.isfile(filepath):
                file_stat = os.stat(filepath)
                file_size = file_stat.st_size
                uploaded_at = timezone.make_aware(datetime.fromtimestamp(file_stat.st_mtime))
                
                # データベースからアップロード情報を検索
                db_file = FileRecord.objects.filter(file__endswith=filename).first()
                
                employee_code = ""
                original_filename = filename
                id = None
                
                if db_file:
                    employee_code = db_file.employee_code
                    original_filename = db_file.original_filename
                    id = db_file.id
                else:
                    id = 0  # データベースに未登録の場合
                
                upload_files.append({
                    'id': id,
                    'original_filename': original_filename,
                    'filepath': filepath,
                    'file_size': file_size,
                    'uploaded_at': uploaded_at,
                    'employee_code': employee_code
                })
    
    # アップロード日時の降順でソート
    upload_files.sort(key=lambda x: x['uploaded_at'], reverse=True)
    
    # ログファイルのパスを取得
    log_files = {
        'main': settings.LOGGING['handlers']['file']['filename'],
        'download': settings.LOGGING['handlers']['download_file']['filename'],
        'upload': settings.LOGGING['handlers']['upload_file']['filename']
    }
    
    # ログの内容を取得（最新の100行）
    logs = {}
    for log_type, log_path in log_files.items():
        try:
            if os.path.exists(log_path):
                # 複数のエンコーディングを試して正しく読み込む
                encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp']
                lines = []
                
                for encoding in encodings:
                    try:
                        with open(log_path, 'r', encoding=encoding) as f:
                            lines = f.readlines()
                        # 正常に読み込めたらループを抜ける
                        break
                    except UnicodeDecodeError:
                        # このエンコーディングでは読めなかった場合、次のエンコーディングを試す
                        continue
                
                # どのエンコーディングでも読めなかった場合
                if not lines:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                
                logs[log_type] = lines[-100:] if len(lines) > 100 else lines
            else:
                logs[log_type] = [f"{log_type}ログファイルが見つかりません: {log_path}"]
        except Exception as e:
            logs[log_type] = [f"{log_type}ログファイルの読み込みエラー: {str(e)}"]
    
    # レスポンスのコンテキスト
    context = {
        'download_files': download_files,
        'upload_files': upload_files,
        'logs': logs,
        'active_menu': 'master'
    }
    
    return render(request, 'files/master.html', context)


def get_logs(request):
    """AJAX ログデータ取得API およびファイル一覧"""
    try:
        # ログファイルのパスを取得
        log_files = {
            'main': settings.LOGGING['handlers']['file']['filename'],
            'download': settings.LOGGING['handlers']['download_file']['filename'],
            'upload': settings.LOGGING['handlers']['upload_file']['filename']
        }
        
        # ログの内容を取得（最新の100行）
        logs = {}
        for log_type, log_path in log_files.items():
            try:
                if os.path.exists(log_path):
                    # 複数のエンコーディングを試して正しく読み込む
                    encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp']
                    lines = []
                    
                    for encoding in encodings:
                        try:
                            with open(log_path, 'r', encoding=encoding) as f:
                                lines = f.readlines()
                            # 正常に読み込めたらループを抜ける
                            break
                        except UnicodeDecodeError:
                            # このエンコーディングでは読めなかった場合、次のエンコーディングを試す
                            continue
                    
                    # どのエンコーディングでも読めなかった場合
                    if not lines:
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                    
                    logs[log_type] = lines[-100:] if len(lines) > 100 else lines
                else:
                    logs[log_type] = [f"{log_type}ログファイルが見つかりません: {log_path}"]
            except Exception as e:
                logs[log_type] = [f"{log_type}ログファイルの読み込みエラー: {str(e)}"]
        
        # ログデータをJSON形式で返す
        log_data = {}
        for log_type, lines in logs.items():
            log_data[log_type] = []
            for line in lines:
                # ログの種類を判定
                log_class = "log-line-info"
                if "ERROR" in line:
                    log_class = "log-line-error"
                elif "WARNING" in line:
                    log_class = "log-line-warning"
                
                log_data[log_type].append({
                    'text': line,
                    'class': log_class
                })
        
        # ファイル一覧情報も取得する
        # ダウンロードファイル一覧を実際のフォルダから取得
        download_files = []
        download_dir = settings.DOWNLOAD_DIR
        
        if os.path.exists(download_dir):
            for filename in os.listdir(download_dir):
                filepath = os.path.join(download_dir, filename)
                if os.path.isfile(filepath):
                    file_stat = os.stat(filepath)
                    file_size = file_stat.st_size
                    last_modified = timezone.make_aware(datetime.fromtimestamp(file_stat.st_mtime))
                    
                    # データベースからダウンロード情報を検索（ファイルパスで一致するものを探す）
                    db_file = DownloadableFile.objects.filter(filepath=filepath).first()
                    
                    is_downloaded = False
                    last_downloaded_at = None
                    id = None
                    
                    if db_file:
                        is_downloaded = db_file.is_downloaded
                        last_downloaded_at = db_file.last_downloaded_at
                        id = db_file.id
                    else:
                        id = 0  # データベースに未登録の場合
                    
                    download_files.append({
                        'id': id,
                        'filename': filename,
                        'file_size': file_size,
                        'last_modified': last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                        'is_downloaded': is_downloaded,
                        'last_downloaded_at': last_downloaded_at.strftime('%Y-%m-%d %H:%M:%S') if last_downloaded_at else None
                    })
        
        # 最終更新日時の降順でソート
        download_files.sort(key=lambda x: x['last_modified'], reverse=True)
        
        # アップロードファイル一覧を実際のフォルダから取得
        upload_files = []
        upload_dir = settings.UPLOAD_DIR
        
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                filepath = os.path.join(upload_dir, filename)
                if os.path.isfile(filepath):
                    file_stat = os.stat(filepath)
                    file_size = file_stat.st_size
                    uploaded_at = timezone.make_aware(datetime.fromtimestamp(file_stat.st_mtime))
                    
                    # データベースからアップロード情報を検索
                    db_file = FileRecord.objects.filter(file__endswith=filename).first()
                    
                    employee_code = ""
                    original_filename = filename
                    id = None
                    
                    if db_file:
                        employee_code = db_file.employee_code
                        original_filename = db_file.original_filename
                        id = db_file.id
                    else:
                        id = 0  # データベースに未登録の場合
                    
                    upload_files.append({
                        'id': id,
                        'original_filename': original_filename,
                        'file_size': file_size,
                        'uploaded_at': uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'employee_code': employee_code
                    })
        
        # アップロード日時の降順でソート
        upload_files.sort(key=lambda x: x['uploaded_at'], reverse=True)
        
        return JsonResponse({
            'status': 'success',
            'logs': log_data,
            'download_files': download_files,
            'upload_files': upload_files
        })
    except Exception as e:
        logger.error(f"データ取得エラー: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'データの取得中にエラーが発生しました',
            'error': str(e)
        }, status=500)
