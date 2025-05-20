"""
現場報告DXシステム - ファイル管理モジュール
画像ファイルの保存・圧縮・ZIP化などを処理
"""
import os
import shutil
import zipfile
import datetime
from pathlib import Path
from loguru import logger

from config import UPLOAD_FOLDER, LOG_FOLDER

def ensure_folders_exist():
    """必要なフォルダ構造を確保"""
    # アップロードフォルダ
    upload_folder = Path(UPLOAD_FOLDER)
    upload_folder.mkdir(parents=True, exist_ok=True)

    # ログフォルダ
    log_folder = Path(LOG_FOLDER)
    log_folder.mkdir(parents=True, exist_ok=True)

    # 日付ベースのログフォルダ
    today = datetime.datetime.now().strftime("%Y%m%d")
    daily_log_folder = log_folder / today
    daily_log_folder.mkdir(parents=True, exist_ok=True)

    return True

def save_image(image_content, file_path, metadata=None):
    """画像ファイルを保存

    Args:
        image_content (bytes): 画像バイナリデータ
        file_path (Path): 保存先パス
        metadata (dict, optional): 保存するメタデータ

    Returns:
        bool: 保存成功時はTrue
    """
    try:
        # 保存先ディレクトリがなければ作成
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 画像データを保存
        with open(file_path, 'wb') as f:
            f.write(image_content)

        logger.info(f"画像保存成功: {file_path}")
        return True

    except Exception as e:
        logger.error(f"画像保存エラー: {file_path} - {str(e)}")
        return False

def delete_image(file_path):
    """画像ファイルを削除

    Args:
        file_path (Path): 削除する画像ファイルのパス

    Returns:
        bool: 削除成功時はTrue
    """
    try:
        file_path = Path(file_path)

        if file_path.exists():
            file_path.unlink()
            logger.info(f"画像削除成功: {file_path}")
            return True
        else:
            logger.warning(f"削除対象の画像が存在しません: {file_path}")
            return False

    except Exception as e:
        logger.error(f"画像削除エラー: {file_path} - {str(e)}")
        return False

def create_zip_archive(file_paths, output_path):
    """複数の画像ファイルをZIP化

    Args:
        file_paths (list): ZIP化する画像パスのリスト
        output_path (Path): 出力先ZIPファイルのパス

    Returns:
        bool: ZIP作成成功時はTrue
    """
    try:
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for file_path in file_paths:
                path = Path(file_path)
                if path.exists():
                    # ZIPファイル内には元のファイル名のみを使用
                    zipf.write(file_path, arcname=path.name)
                    logger.info(f"ZIP追加: {path.name}")
                else:
                    logger.warning(f"ZIP追加対象のファイルが存在しません: {file_path}")

        logger.info(f"ZIP作成成功: {output_path}")
        return True

    except Exception as e:
        logger.error(f"ZIP作成エラー: {output_path} - {str(e)}")
        return False

def get_uploaded_files():
    """アップロード済みの画像ファイル一覧を取得

    Returns:
        list: 画像ファイルパスのリスト
    """
    try:
        upload_folder = Path(UPLOAD_FOLDER)
        files = []

        # アップロードフォルダ内のすべてのJPEGファイルを検索
        for file_path in upload_folder.glob("*.jpg"):
            files.append(str(file_path))

        return files

    except Exception as e:
        logger.error(f"ファイル一覧取得エラー: {str(e)}")
        return []

def cleanup_old_files(days=30):
    """古いファイルを削除（デフォルトは30日以上前のファイル）

    Args:
        days (int): 削除する日数の閾値

    Returns:
        int: 削除したファイル数
    """
    try:
        now = datetime.datetime.now()
        threshold = now - datetime.timedelta(days=days)
        upload_folder = Path(UPLOAD_FOLDER)
        count = 0

        # フォルダ内のすべてのファイルをチェック
        for file_path in upload_folder.iterdir():
            if file_path.is_file():
                # ファイル更新日時を取得
                mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)

                # 閾値より古い場合は削除
                if mtime < threshold:
                    file_path.unlink()
                    count += 1
                    logger.info(f"古いファイルを削除: {file_path}")

        return count

    except Exception as e:
        logger.error(f"古いファイル削除エラー: {str(e)}")
        return 0

def move_to_archive(source_paths, archive_folder):
    """ファイルをアーカイブフォルダに移動

    Args:
        source_paths (list): 移動するファイルパスのリスト
        archive_folder (Path): アーカイブフォルダパス

    Returns:
        bool: すべて成功時はTrue
    """
    try:
        # アーカイブフォルダがなければ作成
        archive_path = Path(archive_folder)
        archive_path.mkdir(parents=True, exist_ok=True)

        success = True
        for source_path in source_paths:
            path = Path(source_path)
            if path.exists():
                # 移動先パス（同じファイル名）
                dest_path = archive_path / path.name

                # 既に同名ファイルがある場合は上書き
                if dest_path.exists():
                    dest_path.unlink()

                # 移動
                shutil.move(str(path), str(dest_path))
                logger.info(f"ファイル移動: {path} -> {dest_path}")
            else:
                logger.warning(f"移動対象ファイルが存在しません: {source_path}")
                success = False

        return success

    except Exception as e:
        logger.error(f"ファイル移動エラー: {str(e)}")
        return False