"""
現場報告DXシステム - メタデータ処理モジュール
画像のメタデータ（タグ、位置情報など）の管理
"""
import json
import datetime
from pathlib import Path
from loguru import logger

from config import DEFAULT_METADATA

def create_metadata(user_name, location, tags=None, comment=None):
    """画像のメタデータを作成

    Args:
        user_name (str): ユーザー名
        location (str): 場所
        tags (list, optional): タグリスト
        comment (str, optional): コメント

    Returns:
        dict: メタデータ辞書
    """
    # デフォルト値をコピー
    metadata = DEFAULT_METADATA.copy()

    # 値を設定
    metadata["user_name"] = user_name or "名前未設定"
    metadata["location"] = location or "場所未設定"
    metadata["tags"] = tags or []
    metadata["comment"] = comment or ""
    metadata["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return metadata

def validate_metadata(metadata):
    """メタデータのバリデーション

    Args:
        metadata (dict): 検証するメタデータ

    Returns:
        tuple: (有効か, エラーメッセージ)
    """
    # 必須フィールドのチェック
    required_fields = ["user_name", "location", "timestamp"]
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            return False, f"必須フィールドが不足しています: {field}"

    # タグは空でも良いがリスト型であること
    if "tags" in metadata and not isinstance(metadata["tags"], list):
        return False, "タグはリスト形式である必要があります"

    return True, ""

def save_metadata_to_json(metadata, output_path):
    """メタデータをJSONファイルとして保存

    Args:
        metadata (dict): 保存するメタデータ
        output_path (Path): 出力先JSONファイルのパス

    Returns:
        bool: 保存成功時はTrue
    """
    try:
        # バリデーション
        valid, error_msg = validate_metadata(metadata)
        if not valid:
            logger.error(f"無効なメタデータ: {error_msg}")
            return False

        # 保存先ディレクトリがなければ作成
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # JSON形式で保存
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"メタデータ保存成功: {output_path}")
        return True

    except Exception as e:
        logger.error(f"メタデータ保存エラー: {output_path} - {str(e)}")
        return False

def load_metadata_from_json(json_path):
    """JSONファイルからメタデータを読み込み

    Args:
        json_path (Path): 読み込むJSONファイルのパス

    Returns:
        dict: 読み込んだメタデータ（エラー時は空辞書）
    """
    try:
        json_path = Path(json_path)

        if not json_path.exists():
            logger.warning(f"メタデータファイルが存在しません: {json_path}")
            return {}

        # JSONを読み込み
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # バリデーション
        valid, error_msg = validate_metadata(metadata)
        if not valid:
            logger.warning(f"無効なメタデータ: {error_msg}")
            return {}

        return metadata

    except json.JSONDecodeError as e:
        logger.error(f"JSONパースエラー: {json_path} - {str(e)}")
        return {}

    except Exception as e:
        logger.error(f"メタデータ読み込みエラー: {json_path} - {str(e)}")
        return {}

def format_metadata_for_slack(metadata):
    """SlackメッセージようにメタデータをフォーマットJ

    Args:
        metadata (dict): フォーマットするメタデータ

    Returns:
        str: Slack通知用にフォーマットされたテキスト
    """
    # バリデーション
    valid, _ = validate_metadata(metadata)
    if not valid:
        return "メタデータが不足しています"

    # メッセージフォーマット
    lines = [
        "📸 【現場報告写真】",
        f"👷 作業者: {metadata['user_name']}",
        f"📍 場所: {metadata['location']}",
        f"🏷️ タグ: {', '.join(metadata['tags']) if metadata['tags'] else 'なし'}",
        f"🕒 日時: {metadata['timestamp']}"
    ]

    # コメントがあれば追加
    if metadata.get("comment"):
        lines.append(f"💬 コメント: {metadata['comment']}")

    return "\n".join(lines)

def extract_image_metadata(image_path):
    """画像ファイルからExifメタデータを抽出（将来機能）

    Args:
        image_path (Path): 画像ファイルのパス

    Returns:
        dict: 抽出したメタデータ
    """
    # 将来実装のための関数
    # PILやExifReadを使ってEXIF情報を抽出
    return {}