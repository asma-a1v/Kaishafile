@echo off
cd /d %~dp0
echo ファイル自動削除処理を開始します - %date% %time%
python manage.py cleanup_files
echo 処理が完了しました - %date% %time% 