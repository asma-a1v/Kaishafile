# Kaishafile - システム宛ファイル共有システム

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

### 自動メンテナンス機能

- ログファイルの自動クリーンアップ（サイズが70MBを超えた場合に50MBに削減）
- ダウンロード済みファイルの自動削除（前日以前にダウンロードされたファイル）
- Djangoサーバー起動時に自動的に実行

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
http://127.0.0.1:8000/files/master/
```

### ファイルクリーンアップ

古いファイルを定期的に削除する方法は2つあります：

#### 1. 自動クリーンアップ（推奨）

Djangoサーバー起動時に自動的にクリーンアップデーモンが起動し、毎日0時に前日以前にダウンロードされたファイルを削除します。この機能はデフォルトで有効になっています。

設定ファイル（`filemanager/settings.py`）で設定を変更できます：

```python
# 自動クリーンアップ機能の設定
AUTO_CLEANUP_ENABLED = True  # 自動クリーンアップを有効にするフラグ
```

#### 2. 手動クリーンアップ

自動クリーンアップが無効になっている場合や、すぐにクリーンアップを実行したい場合は、以下のバッチファイルを実行します：

```
cleanup_files.bat
```

または直接コマンドを実行することもできます：

```
python manage.py cleanup_files
```

### ログファイル管理

システムは以下の3つのログファイルを使用します：

- `filemanager.log` - システム全体のログ
- `download.log` - ダウンロード操作のみのログ
- `upload.log` - アップロード操作のみのログ

#### 1. 自動ログクリーンアップ（推奨）

Djangoサーバー起動時に自動的にログクリーンアップデーモンが起動し、一定間隔（デフォルト1時間）でログファイルのサイズをチェックします。サイズが70MBを超えた場合、古いログを削除して50MBに削減します。

設定ファイル（`filemanager/settings.py`）で設定を変更できます：

```python
# 自動クリーンアップ機能の設定
AUTO_CLEANUP_ENABLED = True  # 自動クリーンアップを有効にするフラグ
LOG_CLEANUP_INTERVAL = 3600  # ログクリーンアップの実行間隔（秒）
```

#### 2. 手動ログクリーンアップ

ログファイルを手動でクリーンアップするには、以下のバッチファイルを実行します：

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

## 自動クリーンアップ機能のセットアップと確認

### 1. 自動クリーンアップの設定

自動クリーンアップ機能は`filemanager/settings.py`で設定できます：

```python
# 自動クリーンアップ機能の設定
AUTO_CLEANUP_ENABLED = True  # 自動クリーンアップを有効にするフラグ
LOG_CLEANUP_INTERVAL = 3600  # ログクリーンアップの実行間隔（秒）
```

- `AUTO_CLEANUP_ENABLED = True`：自動クリーンアップ機能を有効にします
- `AUTO_CLEANUP_ENABLED = False`：自動クリーンアップ機能を無効にします
- `LOG_CLEANUP_INTERVAL`：ログファイルをチェックする間隔を秒単位で指定します

### 2. 動作確認方法

#### サーバー起動時のログメッセージ

Djangoサーバーを起動すると、コンソールに以下のようなメッセージが表示されます：

```
ログクリーンアップデーモンを起動しました（間隔: 3600秒）
ファイルクリーンアップデーモンを起動しました（毎日0時に実行）
```

これらのメッセージが表示されれば、自動クリーンアップ機能が正常に起動しています。

#### 手動での確認

デーモン機能を手動で起動して動作確認するには、以下のコマンドを使用します：

```
# ログクリーンアップデーモンを起動（10秒間隔で実行する例）
python manage.py cleanup_logs --daemon --interval=10

# ファイルクリーンアップデーモンを起動
python manage.py cleanup_files --daemon
```

### 3. トラブルシューティング

自動クリーンアップ機能が正しく動作しない場合は、以下を確認してください：

1. `settings.py`で`AUTO_CLEANUP_ENABLED = True`になっていることを確認
2. サーバー起動時にエラーメッセージが表示されていないことを確認
3. ログファイル（`logs/filemanager.log`）でエラーが記録されていないことを確認

問題が解決しない場合は、手動でバッチファイルを実行するか、直接コマンドを実行してください。
