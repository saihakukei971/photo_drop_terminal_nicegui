"""
現場報告DXシステム - Slack通知モジュール
画像とメタデータをSlackに送信
"""
import os
import aiohttp
import asyncio
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from logics.metadata import format_metadata_for_slack

# 環境変数のロード
load_dotenv()

# Slack設定
SLACK_TOKEN = os.getenv("SLACK_TOKEN", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "")
SLACK_ENABLED = os.getenv("SLACK_ENABLED", "false").lower() == "true"

async def send_slack_notification(img_path, metadata=None):
    """画像とメタデータをSlackに送信

    Args:
        img_path (str): 送信する画像ファイルのパス
        metadata (dict, optional): 送信するメタデータ

    Returns:
        bool: 送信成功時はTrue
    """
    # Slack機能が無効な場合
    if not SLACK_ENABLED:
        logger.warning("Slack機能は無効です。config.pyまたは.envで有効化してください")
        return False

    # トークンやチャンネルが未設定の場合
    if not SLACK_TOKEN or not SLACK_CHANNEL:
        logger.error("SlackトークンまたはチャンネルIDが設定されていません")
        return False

    # 画像ファイルの存在確認
    img_path = Path(img_path)
    if not img_path.exists():
        logger.error(f"送信する画像が存在しません: {img_path}")
        return False

    try:
        # メタデータがあればフォーマット
        text = format_metadata_for_slack(metadata) if metadata else "現場報告写真"

        # POSTリクエストの準備
        headers = {
            "Authorization": f"Bearer {SLACK_TOKEN}"
        }

        # ファイルアップロード用データ
        file_name = img_path.name

        # multipart/form-dataとしてアップロード
        async with aiohttp.ClientSession() as session:
            # ファイル送信用のフォームデータを作成
            with open(img_path, "rb") as f:
                form_data = aiohttp.FormData()
                form_data.add_field(
                    name="file",
                    value=f,
                    filename=file_name,
                    content_type="image/jpeg"
                )
                form_data.add_field("channels", SLACK_CHANNEL)
                form_data.add_field("initial_comment", text)

                # ファイルアップロードAPIを呼び出し
                async with session.post(
                    "https://slack.com/api/files.upload",
                    headers=headers,
                    data=form_data
                ) as response:
                    response_data = await response.json()

                    if not response_data.get("ok", False):
                        logger.error(f"Slack送信エラー: {response_data.get('error', '不明なエラー')}")
                        return False

        logger.info(f"Slack送信成功: {img_path}")
        return True

    except Exception as e:
        logger.error(f"Slack送信エラー: {str(e)}")
        return False

async def send_slack_message(message):
    """テキストメッセージをSlackに送信

    Args:
        message (str): 送信するメッセージ

    Returns:
        bool: 送信成功時はTrue
    """
    # Slack機能が無効な場合
    if not SLACK_ENABLED:
        logger.warning("Slack機能は無効です。config.pyまたは.envで有効化してください")
        return False

    # トークンやチャンネルが未設定の場合
    if not SLACK_TOKEN or not SLACK_CHANNEL:
        logger.error("SlackトークンまたはチャンネルIDが設定されていません")
        return False

    try:
        # POSTリクエストの準備
        headers = {
            "Authorization": f"Bearer {SLACK_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            "channel": SLACK_CHANNEL,
            "text": message
        }

        # API呼び出し
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://slack.com/api/chat.postMessage",
                headers=headers,
                json=data
            ) as response:
                response_data = await response.json()

                if not response_data.get("ok", False):
                    logger.error(f"Slackメッセージ送信エラー: {response_data.get('error', '不明なエラー')}")
                    return False

        logger.info(f"Slackメッセージ送信成功")
        return True

    except Exception as e:
        logger.error(f"Slackメッセージ送信エラー: {str(e)}")
        return False

async def send_bulk_to_slack(image_paths, metadata_list=None):
    """複数の画像をまとめてSlackに送信

    Args:
        image_paths (list): 送信する画像パスのリスト
        metadata_list (list, optional): 各画像に対応するメタデータのリスト

    Returns:
        tuple: (成功数, 失敗数)
    """
    success_count = 0
    failure_count = 0

    # 各画像を順番に送信
    for i, img_path in enumerate(image_paths):
        # 対応するメタデータがあれば使用
        metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else None

        # 送信
        if await send_slack_notification(img_path, metadata):
            success_count += 1
        else:
            failure_count += 1

        # Slack APIレート制限対策のため少し待機
        await asyncio.sleep(1)

    logger.info(f"Slack一括送信結果: 成功={success_count}, 失敗={failure_count}")
    return success_count, failure_count

async def test_slack_connection():
    """Slack接続テスト

    Returns:
        bool: 接続成功時はTrue
    """
    # テストメッセージ送信
    return await send_slack_message("現場報告システム: 接続テスト")