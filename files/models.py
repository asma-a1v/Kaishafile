from django.db import models
from django.utils import timezone
import os
import uuid
import logging
from django.conf import settings
import datetime

logger = logging.getLogger(__name__)

class FileRecord(models.Model):
    """アップロードされたファイルの記録 - アップロード専用"""
    file = models.FileField(upload_to='uploads/')
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    employee_code = models.CharField(max_length=50)
    
    def __str__(self):
        return self.original_filename
    
    def delete(self, *args, **kwargs):
        """ファイルレコード削除時に物理ファイルも削除"""
        try:
            os.remove(self.file.path)
            logger.info(f"アップロードファイル削除: {self.original_filename}, パス: {self.file.path}")
        except Exception as e:
            logger.error(f"アップロードファイル削除エラー: {self.original_filename}, エラー: {str(e)}")
        super().delete(*args, **kwargs)


class DownloadableFile(models.Model):
    """ダウンロード可能なファイル - 特定ディレクトリから読み込み"""
    filename = models.CharField(max_length=255)
    filepath = models.CharField(max_length=512)
    file_size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField()
    is_downloaded = models.BooleanField(default=False)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.filename
    
    @classmethod
    def scan_directory(cls):
        """指定されたディレクトリからファイルをスキャンして登録"""
        download_dir = os.path.join(settings.MEDIA_ROOT, 'downloads')
        
        # ディレクトリが存在しない場合は作成
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            logger.info(f"ダウンロードディレクトリを作成しました: {download_dir}")
        
        # 現在のDBに登録されているファイルのパスリスト
        db_files = {f.filepath: f for f in cls.objects.all()}
        
        # ディレクトリ内のファイルをスキャン
        disk_files = set()
        for filename in os.listdir(download_dir):
            filepath = os.path.join(download_dir, filename)
            
            # ディレクトリはスキップ
            if os.path.isdir(filepath):
                continue
                
            disk_files.add(filepath)
            
            # ファイル情報を取得
            file_stat = os.stat(filepath)
            file_size = file_stat.st_size
            last_modified = timezone.make_aware(datetime.datetime.fromtimestamp(file_stat.st_mtime))
            
            # DBに登録されていないファイルは新規作成
            if filepath not in db_files:
                cls.objects.create(
                    filename=filename,
                    filepath=filepath,
                    file_size=file_size,
                    last_modified=last_modified,
                    is_downloaded=False
                )
                logger.info(f"新規ファイルを登録: {filename}")
            else:
                # 更新日時が変わっていれば更新
                db_file = db_files[filepath]
                if db_file.last_modified != last_modified or db_file.file_size != file_size:
                    db_file.last_modified = last_modified
                    db_file.file_size = file_size
                    db_file.save()
                    logger.info(f"ファイル情報を更新: {filename}")
        
        # ディスク上に存在しないファイルの記録を削除
        for filepath, db_file in db_files.items():
            if filepath not in disk_files:
                db_file.delete()
                logger.info(f"存在しないファイル記録を削除: {db_file.filename}")
        
        return len(disk_files)


class DownloadRecord(models.Model):
    """ファイルのダウンロード記録"""
    file = models.ForeignKey(DownloadableFile, on_delete=models.CASCADE, related_name='downloads')
    employee_code = models.CharField(max_length=50, null=True, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file.filename} - {self.downloaded_at} - {self.employee_code}"
