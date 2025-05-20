# 現場報告DXシステム

現場の写真報告をデジタル化し、メタデータ付きでSlackに自動通知するシステムです。スマホとPC両方に対応し、オフライン環境でも利用可能です。

## 特徴

- **NiceGUI**によるモダンな操作性（PC/スマホ対応）
- 画像に自動でメタデータを追加（名前・場所・タグなど）
- Slack連携による自動通知
- オフライン対応（通信がなくても一時保存可能）
- 画像圧縮による通信量削減
- 日付別ログ管理（loguru）
- ZIP一括ダウンロード機能

## インストール方法

### 必要環境

- Python 3.8以上
- pip（Pythonパッケージマネージャ）

### インストール手順

1. リポジトリをクローンまたはダウンロード

```bash
git clone https://github.com/yourusername/photo-report-dx.git
cd photo-report-dx
```

2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

3. 環境設定（Slack連携を使用する場合）

`.env`ファイルを作成し、以下の内容を設定：

```ini
SLACK_ENABLED=true
SLACK_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=your-channel-id
```

## 使い方

### アプリケーションの起動

```bash
python main.py
```

起動すると、ブラウザで自動的に開きます。スマホからアクセスする場合は、同じWi-Fi内から`http://PCのIPアドレス:8080`にアクセスしてください。

### PC（管理者）での操作

1. 左側のフォームに報告情報（名前・場所・タグなど）を入力
2. 画像をアップロード
3. 必要に応じて「Slackに送信」または「ZIPで保存」ボタンを使用

### スマホ（現場）での操作

1. 名前・場所・タグを選択
2. 「カメラで撮影」から直接写真撮影、または「タップして写真を選択」から端末内の画像を選択
3. アップロード完了

## システム構成

```
photo_uploader_nicegui/
├── main.py                # アプリ本体（NiceGUI + UI/処理制御）
├── config.py              # 設定管理（保存先・Slack設定など）
├── logics/
│   ├── file_manager.py    # 保存処理・圧縮・ログ記録
│   ├── notifier.py        # Slack通知処理
│   ├── metadata.py        # メタデータ管理
│   └── utils.py           # 共通ユーティリティ
├── ui_components.py       # UI構築（PC/スマホ対応）
├── data/
│   └── uploaded/          # 一時保存画像（日付別）
├── log/
│   └── YYYYMMDD/          # 実行ログ（日付別・追記形式）
├── .env                   # 環境変数（Slackトークンなど）
├── requirements.txt       # 必要ライブラリ
└── README.md              # 本ファイル
```

## カスタマイズ方法

### タグリストの変更

`config.py`内のTAGSリストを編集して、現場に合わせたタグを設定できます。

```python
TAGS = [
    "施工前",
    "施工中",
    "施工後",
    # ここに追加のタグを記載
]
```

### 場所プリセットの変更

`config.py`内のDEFAULT_LOCATION_PRESETSリストを編集して、現場に合わせた場所を設定できます。

```python
DEFAULT_LOCATION_PRESETS = [
    "A棟1F",
    "A棟2F",
    # ここに追加の場所を記載
]
```

### 画像圧縮率の変更

`config.py`内のCOMPRESSION_QUALITYを変更して、画像圧縮率を調整できます（0～100）。

```python
COMPRESSION_QUALITY = 70  # 値を大きくすると高画質・大容量になります
```

## テスト実行

```bash
pytest -v tests/
```

## トラブルシューティング

### Slack通知が送信されない場合

1. `.env`ファイルの設定を確認
2. `SLACK_ENABLED=true`になっているか確認
3. SlackトークンとチャンネルIDが正しいか確認
4. ログファイル（`log/YYYYMMDD/app.log`）でエラー内容を確認

### 画像がアップロードできない場合

1. アップロードフォルダ（`data/uploaded/`）の書き込み権限を確認
2. ログファイルでエラー内容を確認
3. 画像サイズが大きすぎないか確認

### スマホからアクセスできない場合

1. PCとスマホが同じWi-Fi/ネットワーク内にあるか確認
2. PCのファイアウォール設定でポート8080が開放されているか確認
3. ブラウザで正しいIPアドレスとポート番号（`http://192.168.x.x:8080`）にアクセスしているか確認
