"""
現場報告DXシステム - テスト
pytestによる自動テスト
"""
import os
import json
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# テスト対象のモジュールをインポート
from logics.metadata import create_metadata, validate_metadata, format_metadata_for_slack
from logics.file_manager import ensure_folders_exist, save_image, delete_image, create_zip_archive
from logics.utils import generate_uuid, get_timestamp, safe_filename

# テスト用ディレクトリとファイル
TEST_DIR = Path("test_data")
TEST_UPLOAD_DIR = TEST_DIR / "uploaded"
TEST_LOG_DIR = TEST_DIR / "log"

# テスト前後の処理
@pytest.fixture(scope="module")
def setup_test_environment():
    """テスト環境のセットアップと後片付け"""
    # テストディレクトリの作成
    TEST_DIR.mkdir(exist_ok=True)
    TEST_UPLOAD_DIR.mkdir(exist_ok=True)
    TEST_LOG_DIR.mkdir(exist_ok=True)
    
    # テスト用のダミー画像を作成
    test_image_path = TEST_UPLOAD_DIR / "test_image.jpg"
    with open(test_image_path, "wb") as f:
        f.write(b"dummy image data")
    
    yield
    
    # テスト終了後にテストディレクトリを削除
    shutil.rmtree(TEST_DIR)

# メタデータテスト
class TestMetadata:
    def test_create_metadata(self):
        """メタデータ作成のテスト"""
        # メタデータを作成
        metadata = create_metadata(
            user_name="テスト太郎",
            location="A棟1F",
            tags=["施工前", "確認依頼"],
            comment="テストコメント"
        )
        
        # 結果を検証
        assert metadata["user_name"] == "テスト太郎"
        assert metadata["location"] == "A棟1F"
        assert "施工前" in metadata["tags"]
        assert "確認依頼" in metadata["tags"]
        assert metadata["comment"] == "テストコメント"
        assert "timestamp" in metadata
    
    def test_validate_metadata_valid(self):
        """有効なメタデータのバリデーションテスト"""
        metadata = {
            "user_name": "テスト太郎",
            "location": "A棟1F",
            "tags": ["施工前"],
            "comment": "テストコメント",
            "timestamp": "2025-05-20 12:34:56"
        }
        
        valid, _ = validate_metadata(metadata)
        assert valid is True
    
    def test_validate_metadata_invalid(self):
        """無効なメタデータのバリデーションテスト"""
        # 必須フィールドが不足している
        metadata1 = {
            "user_name": "テスト太郎",
            "tags": ["施工前"]
        }
        
        valid1, _ = validate_metadata(metadata1)
        assert valid1 is False
        
        # タグがリスト形式でない
        metadata2 = {
            "user_name": "テスト太郎",
            "location": "A棟1F",
            "tags": "施工前",  # リストではなく文字列
            "timestamp": "2025-05-20 12:34:56"
        }
        
        valid2, _ = validate_metadata(metadata2)
        assert valid2 is False
    
    def test_format_metadata_for_slack(self):
        """Slack通知用メタデータフォーマットのテスト"""
        metadata = {
            "user_name": "テスト太郎",
            "location": "A棟1F",
            "tags": ["施工前", "確認依頼"],
            "comment": "テストコメント",
            "timestamp": "2025-05-20 12:34:56"
        }
        
        formatted = format_metadata_for_slack(metadata)
        
        # フォーマット結果を検証
        assert "テスト太郎" in formatted
        assert "A棟1F" in formatted
        assert "施工前" in formatted
        assert "確認依頼" in formatted
        assert "テストコメント" in formatted
        assert "2025-05-20 12:34:56" in formatted

# ファイル管理テスト
class TestFileManager:
    def test_ensure_folders_exist(self, setup_test_environment):
        """フォルダ作成のテスト"""
        # config.pyのインポートパスをモック
        with patch("logics.file_manager.UPLOAD_FOLDER", TEST_UPLOAD_DIR), \
             patch("logics.file_manager.LOG_FOLDER", TEST_LOG_DIR):
            
            result = ensure_folders_exist()
            
            assert result is True
            assert TEST_UPLOAD_DIR.exists()
            assert TEST_LOG_DIR.exists()
    
    def test_save_and_delete_image(self, setup_test_environment):
        """画像の保存と削除のテスト"""
        # テスト用の画像データ
        image_data = b"test image data"
        file_path = TEST_UPLOAD_DIR / "test_save.jpg"
        
        # 画像を保存
        save_result = save_image(image_data, file_path)
        assert save_result is True
        assert file_path.exists()
        
        # 保存された内容を確認
        with open(file_path, "rb") as f:
            saved_data = f.read()
        assert saved_data == image_data
        
        # 画像を削除
        delete_result = delete_image(file_path)
        assert delete_result is True
        assert not file_path.exists()
    
    def test_create_zip_archive(self, setup_test_environment):
        """ZIPアーカイブ作成のテスト"""
        # テスト用のファイルを作成
        file1 = TEST_UPLOAD_DIR / "zip_test1.txt"
        file2 = TEST_UPLOAD_DIR / "zip_test2.txt"
        
        with open(file1, "w") as f:
            f.write("test file 1")
        
        with open(file2, "w") as f:
            f.write("test file 2")
        
        # ZIPアーカイブを作成
        zip_path = TEST_DIR / "test_archive.zip"
        result = create_zip_archive([str(file1), str(file2)], zip_path)
        
        assert result is True
        assert zip_path.exists()
        
        # ZIPファイルのサイズをチェック
        assert os.path.getsize(zip_path) > 0

# ユーティリティテスト
class TestUtils:
    def test_generate_uuid(self):
        """UUID生成のテスト"""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        
        assert isinstance(uuid1, str)
        assert len(uuid1) > 0
        # 2つのUUIDは異なるはず
        assert uuid1 != uuid2
    
    def test_get_timestamp(self):
        """タイムスタンプ取得のテスト"""
        # デフォルトフォーマット
        timestamp1 = get_timestamp()
        assert len(timestamp1) > 0
        
        # カスタムフォーマット
        timestamp2 = get_timestamp("%Y-%m-%d")
        assert "-" in timestamp2
        assert len(timestamp2.split("-")) == 3
    
    def test_safe_filename(self):
        """安全なファイル名変換のテスト"""
        # 無効な文字を含むファイル名
        unsafe_name = 'test<>:"/\\|?*file.jpg'
        safe_name = safe_filename(unsafe_name)
        
        # 無効な文字がアンダースコアに置換されていること
        assert "<" not in safe_name
        assert ">" not in safe_name
        assert ":" not in safe_name
        assert '"' not in safe_name
        assert "/" not in safe_name
        assert "\\" not in safe_name
        assert "|" not in safe_name
        assert "?" not in safe_name
        assert "*" not in safe_name
        
        # 基本的な部分は保持されていること
        assert "test" in safe_name
        assert "file" in safe_name
        assert ".jpg" in safe_name

# Slack通知テスト（モック使用）
@pytest.mark.asyncio
class TestNotifier:
    @pytest.mark.asyncio
    async def test_send_slack_notification(self, setup_test_environment):
        """Slack通知送信のテスト（モック使用）"""
        from logics.notifier import send_slack_notification
        
        # テスト用の画像ファイル
        test_image_path = TEST_UPLOAD_DIR / "slack_test.jpg"
        with open(test_image_path, "wb") as f:
            f.write(b"test image data for slack")
        
        # テスト用のメタデータ
        metadata = {
            "user_name": "テスト太郎",
            "location": "A棟1F",
            "tags": ["施工前"],
            "timestamp": "2025-05-20 12:34:56",
            "comment": "Slackテスト"
        }
        
        # aiohttp.ClientSessionのpostメソッドをモック
        class MockResponse:
            async def json(self):
                return {"ok": True}
            
            async def __aenter__(self):
                return self
            
            async def __aexit__(self, *args):
                pass
        
        mock_session = MagicMock()
        mock_session.post.return_value = MockResponse()
        
        # 設定値をモック
        with patch("logics.notifier.SLACK_ENABLED", True), \
             patch("logics.notifier.SLACK_TOKEN", "mock_token"), \
             patch("logics.notifier.SLACK_CHANNEL", "mock_channel"), \
             patch("aiohttp.ClientSession", return_value=mock_session):
            
            result = await send_slack_notification(test_image_path, metadata)
            
            assert result is True