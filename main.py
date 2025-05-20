"""
現場報告DXシステム - メインアプリケーション
NiceGUIベースの現場報告画像アップロードシステム
"""
import os
import uuid
import datetime
from pathlib import Path
from loguru import logger
from nicegui import ui, app
import asyncio
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# ローカルモジュールのインポート
from config import (
    UPLOAD_FOLDER, LOG_FOLDER, TAGS, COMPRESSION_QUALITY,
    SLACK_ENABLED, DEFAULT_LOCATION_PRESETS
)
from logics.file_manager import save_image, create_zip_archive, ensure_folders_exist
from logics.notifier import send_slack_notification
from logics.metadata import create_metadata, validate_metadata
from logics.utils import get_timestamp, generate_uuid
from ui_components import create_mobile_ui, create_desktop_ui, create_shared_ui_elements

# 環境変数のロード
load_dotenv()

# グローバル変数
uploaded_images = {}  # uuid: {path, metadata, preview_url}
current_user = {"name": "", "location": ""}
device_type = "desktop"  # desktop/mobile（デバイス検出用）

# ログの初期化
def setup_logging():
    """日付ベースのログフォルダを作成し、loguruを設定"""
    today = datetime.datetime.now().strftime("%Y%m%d")
    log_path = Path(LOG_FOLDER) / today
    log_path.mkdir(parents=True, exist_ok=True)

    # loguruの設定
    logger.remove()  # デフォルトのハンドラを削除
    logger.add(
        log_path / "app.log",
        rotation="00:00",  # 日付変更時にローテーション
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {file}:{function}:{line} - {message}",
        level="INFO"
    )
    logger.info(f"アプリケーション起動 - ログ出力先: {log_path}")

# 初期化処理
def initialize_app():
    """アプリケーションの初期化処理"""
    # 必要なフォルダを作成
    ensure_folders_exist()
    # ログの設定
    setup_logging()
    logger.info("アプリケーション初期化完了")

# 画像アップロード処理
async def handle_upload(e):
    """画像アップロード時の処理"""
    for file in e.files:
        file_uuid = generate_uuid()
        temp_path = Path(UPLOAD_FOLDER) / f"{file_uuid}.jpg"

        # 画像の保存
        content = await file.read()

        # PILで画像を開いて圧縮
        img = Image.open(file.file)

        # メタデータを作成
        metadata = create_metadata(
            user_name=current_user.get("name", "名前なし"),
            location=current_user.get("location", "場所なし"),
            tags=current_user.get("tags", []),
            comment=current_user.get("comment", "")
        )

        # 画像にメタデータを追加
        img_with_text = add_text_to_image(img, metadata)

        # 圧縮して保存
        img_with_text.save(temp_path, "JPEG", quality=COMPRESSION_QUALITY)

        # プレビュー用URL作成
        preview_url = f"/_nicegui/auto/local_file/{str(temp_path)}"

        # アップロード済み画像リストに追加
        uploaded_images[file_uuid] = {
            "path": str(temp_path),
            "metadata": metadata,
            "preview_url": preview_url,
            "filename": file.name
        }

        logger.info(f"画像アップロード: {file.name} -> {temp_path} (UUID: {file_uuid})")

        # UIの更新（画像プレビュー表示）
        update_image_previews()

# 画像にテキスト追加
def add_text_to_image(img, metadata):
    """画像の左上にメタデータを追加"""
    draw = ImageDraw.Draw(img)

    # フォントの設定（日本語対応フォント）
    try:
        # Windowsの場合
        font_path = "C:/Windows/Fonts/meiryo.ttc"
        if not os.path.exists(font_path):
            # Macの場合
            font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc"
            if not os.path.exists(font_path):
                # Linuxの場合
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        font = ImageFont.truetype(font_path, 24)
        small_font = ImageFont.truetype(font_path, 18)
    except IOError:
        # フォントが見つからない場合はデフォルトフォント
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 半透明の背景を追加
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # テキスト情報の作成
    text_lines = [
        f"名前: {metadata['user_name']}",
        f"場所: {metadata['location']}",
        f"タグ: {', '.join(metadata['tags'])}",
        f"日時: {metadata['timestamp']}",
    ]

    if metadata['comment']:
        text_lines.append(f"コメント: {metadata['comment']}")

    # 背景の高さを計算
    padding = 10
    line_height = 30
    bg_height = len(text_lines) * line_height + padding * 2

    # 半透明の背景を描画
    draw_overlay.rectangle(
        [(0, 0), (img.width, bg_height)],
        fill=(0, 0, 0, 128)
    )

    # テキストを描画
    for i, line in enumerate(text_lines):
        draw.text(
            (padding, padding + i * line_height),
            line,
            font=small_font if i == len(text_lines) - 1 else font,
            fill=(255, 255, 255)
        )

    # 元の画像と半透明背景を合成
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    result = Image.alpha_composite(img, overlay)
    return result.convert('RGB')  # JPEGとして保存するためRGB変換

# 画像プレビュー更新
def update_image_previews():
    """アップロードされた画像のプレビューを更新"""
    # 既存のプレビュー表示をクリア
    preview_container.clear()

    if not uploaded_images:
        with preview_container:
            ui.label("アップロードされた画像はありません").classes("text-gray-500")
        return

    # 画像プレビューを表示
    with preview_container:
        for img_uuid, img_data in uploaded_images.items():
            with ui.card().classes("mb-2 w-full").style("max-width: 800px"):
                ui.image(img_data["preview_url"]).classes("w-full")

                with ui.row().classes("w-full justify-between items-center"):
                    ui.label(f"ファイル: {img_data['filename']}").classes("text-sm")
                    ui.button(
                        "削除",
                        color="red",
                        on_click=lambda u=img_uuid: delete_image(u)
                    ).classes("text-xs")

                location = img_data["metadata"]["location"]
                tags = ", ".join(img_data["metadata"]["tags"])
                timestamp = img_data["metadata"]["timestamp"]

                with ui.column().classes("text-xs text-gray-600 w-full"):
                    ui.label(f"撮影者: {img_data['metadata']['user_name']}")
                    ui.label(f"場所: {location}")
                    ui.label(f"タグ: {tags}")
                    ui.label(f"日時: {timestamp}")

                    if img_data["metadata"]["comment"]:
                        ui.label(f"コメント: {img_data['metadata']['comment']}")

# 画像削除
def delete_image(img_uuid):
    """画像を削除"""
    if img_uuid in uploaded_images:
        path = uploaded_images[img_uuid]["path"]
        filename = uploaded_images[img_uuid]["filename"]

        try:
            os.remove(path)
            logger.info(f"画像削除: {path}")
        except Exception as e:
            logger.error(f"画像削除エラー: {path} - {str(e)}")

        # 削除
        del uploaded_images[img_uuid]

        # UIの更新
        update_image_previews()
        ui.notify(f"画像を削除しました: {filename}")

# Slack通知送信
async def send_to_slack():
    """アップロードされた画像をSlackに送信"""
    if not uploaded_images:
        ui.notify("送信する画像がありません", color="warning")
        return

    with ui.dialog() as dialog, ui.card():
        ui.label("Slackに送信しますか？").classes("text-lg font-bold")
        ui.label(f"送信する画像: {len(uploaded_images)}枚")

        with ui.row():
            ui.button("キャンセル", on_click=dialog.close).classes("mr-2")
            ui.button(
                "送信",
                color="primary",
                on_click=lambda: slack_send_confirmed(dialog)
            )

    dialog.open()

# Slack送信実行
async def slack_send_confirmed(dialog):
    """Slack送信確認後の処理"""
    dialog.close()

    with ui.dialog() as progress_dialog, ui.card():
        progress = ui.progress()
        status_label = ui.label("Slackに送信中...")

    progress_dialog.open()

    try:
        # 送信処理
        for i, (img_uuid, img_data) in enumerate(uploaded_images.items()):
            # 進捗更新
            progress.set_value(i / len(uploaded_images))

            # Slack送信
            success = await send_slack_notification(
                img_path=img_data["path"],
                metadata=img_data["metadata"]
            )

            if success:
                logger.info(f"Slack送信成功: {img_data['path']}")
            else:
                logger.error(f"Slack送信失敗: {img_data['path']}")
                ui.notify(f"画像の送信に失敗しました: {img_data['filename']}", color="negative")
                progress_dialog.close()
                return

        # 全て送信完了
        progress.set_value(1.0)
        status_label.set_text("送信完了！")

        # 通知
        ui.notify("すべての画像をSlackに送信しました", color="positive")

        # ダイアログを閉じる（少し待機）
        await asyncio.sleep(1)
        progress_dialog.close()

    except Exception as e:
        logger.error(f"Slack送信エラー: {str(e)}")
        status_label.set_text(f"エラー: {str(e)}")
        ui.notify("Slack送信中にエラーが発生しました", color="negative")

        # ダイアログを閉じる（少し待機）
        await asyncio.sleep(2)
        progress_dialog.close()

# 一括ZIP保存
async def save_as_zip():
    """アップロードされた画像をZIPで保存"""
    if not uploaded_images:
        ui.notify("保存する画像がありません", color="warning")
        return

    try:
        # ZIP作成
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"現場報告_{timestamp}.zip"
        zip_path = Path(UPLOAD_FOLDER).parent / zip_filename

        # 画像パスのリスト
        image_paths = [img_data["path"] for img_data in uploaded_images.values()]

        # ZIP作成
        success = create_zip_archive(image_paths, zip_path)

        if success:
            logger.info(f"ZIP作成成功: {zip_path}")
            ui.notify(f"ZIPファイルを作成しました: {zip_filename}", color="positive")

            # ダウンロードリンク
            download_path = f"/_nicegui/auto/local_file/{str(zip_path)}"
            ui.download(download_path, filename=zip_filename)
        else:
            logger.error(f"ZIP作成失敗")
            ui.notify("ZIPファイルの作成に失敗しました", color="negative")

    except Exception as e:
        logger.error(f"ZIP作成エラー: {str(e)}")
        ui.notify(f"エラー: {str(e)}", color="negative")

# ユーザー情報更新
def update_user_info(name, location, tags=None, comment=None):
    """ユーザー情報を更新"""
    current_user["name"] = name
    current_user["location"] = location

    if tags is not None:
        current_user["tags"] = tags

    if comment is not None:
        current_user["comment"] = comment

    logger.info(f"ユーザー情報更新: {name} @ {location}")

# デバイスタイプ検出
def detect_device_type(request):
    """リクエストのUser-Agentからデバイスタイプを検出"""
    user_agent = request.headers.get("User-Agent", "").lower()

    if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
        return "mobile"
    return "desktop"

# メインページ
@ui.page("/")
def main_page():
    global preview_container, device_type

    # デバイスタイプの検出
    device_type = detect_device_type(app.storage.user.get("request"))
    logger.info(f"デバイスタイプ: {device_type}")

    # 共通UI要素
    with ui.column().classes("w-full max-w-screen-lg mx-auto p-4"):
        ui.label("現場報告アップロードシステム").classes("text-2xl font-bold mb-4")

        # デバイスタイプによってUIを分岐
        if device_type == "mobile":
            create_mobile_ui(
                handle_upload=handle_upload,
                update_user_info=update_user_info,
                tags=TAGS,
                location_presets=DEFAULT_LOCATION_PRESETS
            )
        else:
            create_desktop_ui(
                handle_upload=handle_upload,
                update_user_info=update_user_info,
                send_to_slack=send_to_slack,
                save_as_zip=save_as_zip,
                tags=TAGS,
                location_presets=DEFAULT_LOCATION_PRESETS
            )

        # プレビューコンテナ（両方のUIで共有）
        ui.label("アップロードされた画像").classes("text-xl font-bold mt-4")
        preview_container = ui.column().classes("w-full")

        # 初期状態では「アップロードされた画像はありません」と表示
        with preview_container:
            ui.label("アップロードされた画像はありません").classes("text-gray-500")

        # フッター
        with ui.row().classes("w-full justify-between items-center mt-8 text-xs text-gray-500"):
            ui.label("© 2025 現場報告DXシステム")
            ui.label(f"バージョン: 1.0.0")

# アプリケーション初期化
def main():
    initialize_app()
    ui.run(port=8080, title="現場報告システム", favicon="📸")

if __name__ == "__main__":
    main()