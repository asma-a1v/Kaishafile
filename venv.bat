@echo off
echo Pythonの仮想環境を起動しています...

REM 仮想環境が存在するか確認
if not exist venv (
    echo 仮想環墳が存在しません。作成します。
    python -m venv venv
    echo 仮想環境を作成しました。
    call venv\Scripts\activate
    echo 仮想環境が有効になりました。
    python -m pip install --upgrade pip
    echo pipをアップデートしました。
    pip install -r requirements.txt
    echo 必要なライブラリをインストールしました。
) else (
    echo 仮想環墳が存在します。
    call venv\Scripts\activate
    echo 仮想環境が有効になりました。
)

echo 仮想環境が有効になりました。
echo 終了するには "deactivate" と入力してください。

echo ================================================
echo >python manage.py migrate
echo >python manage.py runserver
echo http://127.0.0.1:8000/files/master/
echo ================================================

REM コマンドプロンプトを維持
cmd /k
