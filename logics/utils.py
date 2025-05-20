"""
現場報告DXシステム - ユーティリティモジュール
共通で使用する関数と便利な機能
"""
import uuid
import datetime
import os
import platform
from pathlib import Path
from loguru import logger

def generate_uuid():
    """一意のIDを生成

    Returns:
        str: UUID文字列
    """
    return str(uuid.uuid4())

def get_timestamp(format_str="%Y%m%d_%H%M%S"):
    """現在時刻のタイムスタンプを取得

    Args:
        format_str (str, optional): 日時フォーマット文字列

    Returns:
        str: フォーマットされたタイムスタンプ
    """
    return datetime.datetime.now().strftime(format_str)

def get_today_folder_name():
    """今日の日付フォルダ名を取得

    Returns:
        str: YYYYMMDD形式の日付文字列
    """
    return datetime.datetime.now().strftime("%Y%m%d")

def get_os_info():
    """実行環境のOS情報を取得

    Returns:
        dict: OS情報の辞書
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }

def detect_font_path():
    """OS別に日本語フォントのパスを検出

    Returns:
        str: フォントのパス（見つからない場合はNone）
    """
    system = platform.system()

    if system == "Windows":
        # Windowsの一般的な日本語フォント
        font_paths = [
            "C:/Windows/Fonts/meiryo.ttc",
            "C:/Windows/Fonts/msgothic.ttc",
            "C:/Windows/Fonts/YuGothM.ttc"
        ]
    elif system == "Darwin":  # macOS
        # macOSの一般的な日本語フォント
        font_paths = [
            "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
            "/Library/Fonts/Osaka.ttf",
            "/System/Library/Fonts/AppleGothic.ttf"
        ]
    else:  # Linux
        # Linuxの一般的な日本語フォント
        font_paths = [
            "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # 代替
        ]

    # 存在するフォントパスを検索
    for path in font_paths:
        if os.path.exists(path):
            return path

    # 見つからない場合はNone
    return None

def is_valid_image_file(file_path):
    """有効な画像ファイルかどうかをチェック

    Args:
        file_path (str): 画像ファイルのパス

    Returns:
        bool: 有効な画像ファイルの場合はTrue
    """
    # 拡張子チェック
    valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    extension = Path(file_path).suffix.lower()

    if extension not in valid_extensions:
        return False

    # ファイルサイズチェック
    try:
        file_size = os.path.getsize(file_path)
        if file_size <= 0:
            return False

        # サイズ上限（例: 20MB）
        max_size = 20 * 1024 * 1024
        if file_size > max_size:
            return False
    except:
        return False

    return True

def create_dir_if_not_exists(dir_path):
    """ディレクトリが存在しなければ作成

    Args:
        dir_path (str): 作成するディレクトリのパス

    Returns:
        bool: 作成成功または既に存在する場合はTrue
    """
    try:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"ディレクトリ作成エラー: {dir_path} - {str(e)}")
        return False

def format_file_size(size_bytes):
    """ファイルサイズを読みやすい形式に変換

    Args:
        size_bytes (int): バイト単位のサイズ

    Returns:
        str: フォーマットされたサイズ文字列
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.2f} PB"

def safe_filename(filename):
    """安全なファイル名に変換（無効な文字を除去）

    Args:
        filename (str): 変換する元のファイル名

    Returns:
        str: 安全なファイル名
    """
    # 無効な文字を置換
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # 長すぎる場合は切り詰め
    max_length = 255  # ほとんどのファイルシステムの制限
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext

    return filename