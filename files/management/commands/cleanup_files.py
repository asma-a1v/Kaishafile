import os
import logging
import time
import threading
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from files.models import DownloadableFile

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'ダウンロード済みファイルを削除します（翌日0:00に実行）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='デーモンモードで実行し、毎日0時に自動的にファイルクリーンアップを実行します',
        )

    def handle(self, *args, **options):
        """
        前日以前にダウンロードされたファイルを削除する処理
        """
        # デーモンモードの場合は別スレッドで定期的に実行
        if options.get('daemon', False):
            self.stdout.write('デーモンモードで起動しました。毎日0時に実行します。')
            self.run_as_daemon()
            return
            
        # 通常の処理
        # 現在日付の取得
        now = timezone.now()
        yesterday = now.date() - timedelta(days=1)
        yesterday_datetime = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
        
        # 前日以前にダウンロードされたファイルのみ対象とする
        old_files = DownloadableFile.objects.filter(
            is_downloaded=True,
            last_downloaded_at__lt=yesterday_datetime
        )
        
        # ダウンロード済みの古いファイルが見つからない場合
        if not old_files.exists():
            self.stdout.write('削除対象のファイルはありません')
            return
        
        self.stdout.write(f'{old_files.count()}件のダウンロード済みファイルを削除します')
        
        # ファイル削除処理
        deleted_count = 0
        for file_record in old_files:
            try:
                # ファイルが存在するか確認
                if os.path.exists(file_record.filepath):
                    # 物理ファイルの削除
                    os.remove(file_record.filepath)
                
                # データベース記録の削除
                file_record.delete()
                deleted_count += 1
                
                self.stdout.write(f'ファイル削除: {file_record.filename}')
                logger.info(f'ファイル自動削除: {file_record.filename}, パス: {file_record.filepath}')
                
            except Exception as e:
                error_msg = f'ファイル削除中にエラーが発生しました: {file_record.filename}, エラー: {str(e)}'
                self.stderr.write(error_msg)
                logger.error(error_msg)
        
        self.stdout.write(f'{deleted_count}件のファイルを削除しました') 

    def run_as_daemon(self):
        """デーモンモードで毎日0時にファイルクリーンアップを実行する"""
        
        def scheduler():
            while True:
                try:
                    # 現在時刻を取得
                    now = timezone.now()
                    
                    # 次の0時までの秒数を計算
                    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                    seconds_until_midnight = (tomorrow - now).total_seconds()
                    
                    self.stdout.write(f'{now.strftime("%Y-%m-%d %H:%M:%S")} - 次回のファイルクリーンアップは{tomorrow.strftime("%Y-%m-%d %H:%M:%S")}に実行されます（あと{seconds_until_midnight:.0f}秒）')
                    
                    # 次の0時までスリープ
                    time.sleep(seconds_until_midnight)
                    
                    # 0時になったらクリーンアップを実行
                    self.stdout.write(f'{timezone.now().strftime("%Y-%m-%d %H:%M:%S")} - ファイルクリーンアップを実行します')
                    self.handle(daemon=False)
                    
                except Exception as e:
                    logger.error(f'デーモン実行中にエラーが発生しました: {str(e)}')
                    # エラーが発生しても続行（1時間後に再試行）
                    time.sleep(3600)
        
        # 別スレッドで実行
        thread = threading.Thread(target=scheduler, daemon=True)
        thread.start()
        
        # メインスレッドは終了しないように待機
        try:
            while thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write('プロセスが終了されました') 