import os
import logging
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'ログファイルのサイズが70MBを超えた場合に古いログを削除して50MBにします'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='全てのログファイルをクリーンアップします',
        )
        parser.add_argument(
            '--download',
            action='store_true',
            help='ダウンロードログをクリーンアップします',
        )
        parser.add_argument(
            '--upload',
            action='store_true',
            help='アップロードログをクリーンアップします',
        )
        parser.add_argument(
            '--main',
            action='store_true',
            help='メインログをクリーンアップします',
        )

    def handle(self, *args, **options):
        """
        ログファイルのサイズをチェックし、70MBを超えた場合に古いログを削除して50MBにする処理
        """
        max_size_mb = 70  # 70MB
        target_size_mb = 50  # 50MB
        max_size_bytes = max_size_mb * 1024 * 1024
        target_size_bytes = target_size_mb * 1024 * 1024
        
        # 引数に応じて処理対象のログファイルを決定
        log_files = []
        
        if options['all'] or options['main'] or not (options['download'] or options['upload']):
            log_files.append(settings.LOGGING['handlers']['file']['filename'])
            
        if options['all'] or options['download']:
            log_files.append(settings.LOGGING['handlers']['download_file']['filename'])
            
        if options['all'] or options['upload']:
            log_files.append(settings.LOGGING['handlers']['upload_file']['filename'])
        
        # 各ログファイルを処理
        for log_file_path in log_files:
            self.cleanup_log_file(log_file_path, max_size_bytes, target_size_bytes)
    
    def cleanup_log_file(self, log_file_path, max_size_bytes, target_size_bytes):
        """単一のログファイルをクリーンアップする"""
        # ファイル名から種類を判断
        log_type = os.path.basename(log_file_path).split('.')[0]
        if log_type == 'filemanager':
            log_type = 'メイン'
        
        # ログファイルが存在するか確認
        if not os.path.exists(log_file_path):
            self.stdout.write(f'{log_type}ログファイルが見つかりません: {log_file_path}')
            return
        
        # ファイルサイズを取得
        file_size = os.path.getsize(log_file_path)
        
        # サイズが上限を超えていない場合は何もしない
        if file_size <= max_size_bytes:
            self.stdout.write(f'{log_type}ログファイルのサイズは{file_size / (1024 * 1024):.2f}MBで、上限の70MB以下です')
            return
        
        self.stdout.write(f'{log_type}ログファイルのサイズが{file_size / (1024 * 1024):.2f}MBで上限の70MBを超えています')
        
        try:
            # ファイルの内容を読み込む
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 削除すべき容量を計算
            bytes_to_remove = file_size - target_size_bytes
            
            # 削除する行数を計算（古い行から削除）
            bytes_removed = 0
            lines_to_keep = []
            
            # 新しいログから順に追加していき、目標サイズに達したら終了
            for line in reversed(lines):
                line_size = len(line.encode('utf-8'))
                if bytes_removed + line_size <= bytes_to_remove:
                    bytes_removed += line_size
                else:
                    lines_to_keep.append(line)
            
            # 順序を元に戻す
            lines_to_keep.reverse()
            
            # 削除した行数を計算
            removed_lines = len(lines) - len(lines_to_keep)
            
            # 新しいログメッセージを先頭に追加
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
            log_message = f"INFO {timestamp} cleanup_logs {log_type}ログファイルから古い{removed_lines}行（約{bytes_removed / (1024 * 1024):.2f}MB）を削除しました。\n"
            lines_to_keep.insert(0, log_message)
            
            # ファイルを書き直す
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines_to_keep)
            
            self.stdout.write(f'{log_type}ログファイルから古い{removed_lines}行（約{bytes_removed / (1024 * 1024):.2f}MB）を削除しました')
            logger.info(f'{log_type}ログファイルから古い{removed_lines}行（約{bytes_removed / (1024 * 1024):.2f}MB）を削除しました')
            
        except Exception as e:
            error_msg = f'{log_type}ログファイル処理中にエラーが発生しました: {str(e)}'
            self.stderr.write(error_msg)
            logger.error(error_msg) 