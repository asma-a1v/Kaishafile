@echo off
cd /d %~dp0
echo ログファイル管理処理を開始します - %date% %time%
python manage.py cleanup_logs --all
echo 処理が完了しました - %date% %time% 