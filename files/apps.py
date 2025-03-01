from django.apps import AppConfig
import os
import sys
from django.conf import settings
import threading


class FilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'files'
    
    def ready(self):
        """
        Djangoの起動時に実行される関数
        管理コマンドのデーモン機能を自動的に開始する
        """
        # マイグレーション実行時やコマンド実行時には自動起動しない
        if 'runserver' not in sys.argv and 'uvicorn' not in sys.argv:
            return

        # 自動起動フラグが設定されていない場合は起動しない
        auto_cleanup = getattr(settings, 'AUTO_CLEANUP_ENABLED', False)
        if not auto_cleanup:
            return
            
        # 二重起動を防ぐ（開発サーバーはreloadにより2回呼ばれる）
        if os.environ.get('CLEANUP_DAEMON_STARTED') == 'true':
            return
        os.environ['CLEANUP_DAEMON_STARTED'] = 'true'
        
        # デーモンを別スレッドで起動
        def start_daemons():
            from django.core.management import call_command
            
            # ログクリーンアップデーモン起動
            log_cleanup_interval = getattr(settings, 'LOG_CLEANUP_INTERVAL', 3600)  # デフォルト1時間
            try:
                call_command('cleanup_logs', daemon=True, interval=log_cleanup_interval)
                print(f"ログクリーンアップデーモンを起動しました（間隔: {log_cleanup_interval}秒）")
            except Exception as e:
                print(f"ログクリーンアップデーモンの起動に失敗しました: {str(e)}")
            
            # ファイルクリーンアップデーモン起動
            try:
                call_command('cleanup_files', daemon=True)
                print("ファイルクリーンアップデーモンを起動しました（毎日0時に実行）")
            except Exception as e:
                print(f"ファイルクリーンアップデーモンの起動に失敗しました: {str(e)}")
        
        # 別スレッドで起動して、Djangoの起動を遅延させないようにする
        thread = threading.Thread(target=start_daemons)
        thread.daemon = True
        thread.start()
