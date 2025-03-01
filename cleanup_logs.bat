@echo off
cd /d %~dp0
echo ログファイル管理処理を開始します - %date% %time%
python manage.py cleanup_logs --all
echo 処理が完了しました - %date% %time% 

REM ※注意: このバッチファイルは手動実行用です。
REM Djangoサーバー起動時に自動クリーンアップ機能が有効になっている場合は、
REM settings.pyのAUTO_CLEANUP_ENABLED=Trueにより自動的に実行されます。 