# Kaishafile - 社内ファイル管理システム

Kaishafileは、社内でのファイル共有を簡単かつ効率的に行うためのDjangoベースのウェブアプリケーションです。ファイルのアップロードとダウンロードを管理し、操作履歴を記録します。

## 主な機能

### ファイルアップロード

- 複数ファイルの一括アップロード
- ドラッグ＆ドロップによるアップロード
- アップロード履歴の記録
- 従業員コードによるトラッキング

### ファイルダウンロード

- 利用可能なファイルの一覧表示
- ファイルのダウンロード
- ダウンロード履歴の記録
- 従業員コードによるトラッキング

### その他

- 操作ログの記録
- レスポンシブデザイン（PC・タブレット・スマートフォン対応）
- 直感的なユーザーインターフェース

## 技術スタック

- **バックエンド**: Django 5.1.6
- **フロントエンド**: Bootstrap 5
- **データベース**: SQLite（デフォルト）
- **その他**:
  - django-crispy-forms
  - crispy-bootstrap5
  - python-dotenv

## セットアップ方法

### 前提条件

- Python 3.8以上

### インストール手順

1. リポジトリをクローン

   ```
   git clone https://github.com/yourusername/Kaishafile.git
   cd Kaishafile
   ```
2. 仮想環境の作成と有効化

   ```
   python -m venv venv
   .\venv\Scripts\Activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```
3. 依存パッケージのインストール

   ```
   python.exe -m pip install --upgrade pip && pip install -r requirements.txt
   ```
4. データベースのマイグレーション

   ```
   python manage.py migrate
   ```
5. 開発サーバーの起動

   ```
   python manage.py runserver
   ```

   ```
   .\venv\Scripts\Activate && python manage.py runserver
   ```
6. ブラウザで以下のURLにアクセス

   ```
   http://127.0.0.1:8000/
   ```

## 使用方法

### ファイルのアップロード

1. 「アップロード」メニューを選択
2. 従業員コードを入力
3. ファイルを選択またはドラッグ＆ドロップ
4. 「アップロード」ボタンをクリック

### ファイルのダウンロード

1. 「ダウンロード」メニューを選択
2. ダウンロードしたいファイルを選択
3. 従業員コードを入力
4. 「ダウンロード」ボタンをクリック

### マスター管理ページの利用

1. サイドバーの「マスター管理」をクリック
2. 次の情報を確認できます：
   - ダウンロードフォルダーのファイル一覧
   - アップロードされたファイルの一覧
   - メインログ（システム全体のログ）
   - ダウンロードログ
   - アップロードログ
3. 各情報はタブで切り替えることができます
4. 30秒ごとに自動更新されます

## ディレクトリ構造

```
Kaishafile/
├── filemanager/        # メインプロジェクト設定
├── files/              # ファイル管理アプリケーション
│   ├── migrations/     # データベースマイグレーション
│   ├── templates/      # HTMLテンプレート
│   ├── admin.py        # 管理画面設定
│   ├── forms.py        # フォーム定義
│   ├── models.py       # データモデル
│   ├── urls.py         # URLルーティング
│   └── views.py        # ビュー関数
├── media/              # アップロードされたファイル
├── static/             # 静的ファイル（CSS、JS等）
├── logs/               # ログファイル
├── download_files/     # ダウンロード用ファイル
├── manage.py           # Djangoコマンドライン
└── requirements.txt    # 依存パッケージリスト
```

## 管理者向け情報

### 管理者アカウントの作成

```
python manage.py createsuperuser
```

### 管理画面へのアクセス

```
http://127.0.0.1:8000/admin/
```

### ファイルクリーンアップ

古いファイルを定期的に削除するには、以下のバッチファイルを実行します：

```
cleanup_files.bat
```

### ログファイル管理

システムは以下の3つのログファイルを使用します：

- `filemanager.log` - システム全体のログ
- `download.log` - ダウンロード操作のみのログ
- `upload.log` - アップロード操作のみのログ

これらのログファイルのサイズが70MBを超えた場合に古いログを削除して50MBにするには、以下のバッチファイルを実行します：

```
cleanup_logs.bat
```

特定のログファイルのみを管理する場合は、以下のコマンドを使用します：

```
python manage.py cleanup_logs --main    # メインログのみ
python manage.py cleanup_logs --download    # ダウンロードログのみ
python manage.py cleanup_logs --upload    # アップロードログのみ
python manage.py cleanup_logs --all    # すべてのログ
```

## ライセンス

このプロジェクトは社内利用を目的としており、無断での外部配布や商用利用は禁止されています。

## 開発者向け情報

### 開発環境のセットアップ

```
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
.\venv\Scripts\Activate  # Windows
source venv/bin/activate  # macOS/Linux

# 依存パッケージのインストール
pip install -r requirements.txt
```

### テスト実行

```
python manage.py test
```
