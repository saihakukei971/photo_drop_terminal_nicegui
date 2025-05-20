"""
現場報告DXシステム - 設定ファイル
システムの設定値を一元管理
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# ベースディレクトリ（このファイルが存在するディレクトリ）
BASE_DIR = Path(__file__).parent.absolute()

# 保存先の設定
UPLOAD_FOLDER = BASE_DIR / "data" / "uploaded"
LOG_FOLDER = BASE_DIR / "log"

# 画像圧縮の設定
COMPRESSION_QUALITY = 70  # JPEG圧縮率（0-100）

# Slack設定
SLACK_ENABLED = os.getenv("SLACK_ENABLED", "false").lower() == "true"
SLACK_TOKEN = os.getenv("SLACK_TOKEN", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "")

# タグリスト（職人が選択できるタグ）
TAGS = [
    "施工前",
    "施工中",
    "施工後",
    "問題箇所",
    "修繕必要",
    "確認依頼",
    "完了報告",
    "清掃",
    "安全対策",
    "材料搬入",
    "その他"
]

# 場所のプリセット（現場ごとにカスタマイズ可能）
DEFAULT_LOCATION_PRESETS = [
    "A棟1F",
    "A棟2F",
    "A棟3F",
    "B棟1F",
    "B棟2F",
    "B棟3F",
    "外構",
    "駐車場",
    "倉庫"
]

# 保存ファイル名のフォーマット
FILENAME_FORMAT = "現場報告_{timestamp}_{username}_{location}"

# デフォルト値
DEFAULT_USERNAME = "名前未設定"
DEFAULT_LOCATION = "場所未設定"

# メタデータのデフォルト値
DEFAULT_METADATA = {
    "user_name": DEFAULT_USERNAME,
    "location": DEFAULT_LOCATION,
    "tags": [],
    "comment": "",
    "timestamp": ""
}

# デバッグモード（開発時のみTrue）
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 画像に追加するフォント設定
FONT_SIZE = 24
SMALL_FONT_SIZE = 18

# フォントパス（OSによって異なる）
FONT_PATHS = {
    "windows": "C:/Windows/Fonts/meiryo.ttc",
    "mac": "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "linux": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
}

# 初期化時の設定
def init_config():
    """アプリケーション起動時の設定初期化"""
    # 必要なフォルダが存在しない場合は作成
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    LOG_FOLDER.mkdir(parents=True, exist_ok=True)

    # Slack設定のバリデーション
    if SLACK_ENABLED and (not SLACK_TOKEN or not SLACK_CHANNEL):
        print("警告: Slack機能が有効ですが、トークンまたはチャンネルが設定されていません")
        print("Slack機能を使用するには.envファイルに以下を設定してください:")
        print("SLACK_TOKEN=xoxb-...")
        print("SLACK_CHANNEL=チャンネルID")