#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filemanager.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # サーバー起動コマンドの場合、マスター画面のURLも表示する
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        print("\nDjango server is starting...")
        # オリジナルのrunserverコマンドを実行
        execute_from_command_line(sys.argv)
        # サーバー起動後に追加メッセージを表示
        print("\nMaster management page is available at:")
        print("http://127.0.0.1:8000/files/master/")
        print("\nQuit the server with CTRL-BREAK.")
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
