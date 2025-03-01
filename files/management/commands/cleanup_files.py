import os
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from files.models import DownloadableFile

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'ダウンロード済みファイルを削除します（翌日0:00に実行）'

    def handle(self, *args, **options):
        """
        前日以前にダウンロードされたファイルを削除する処理
        """
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