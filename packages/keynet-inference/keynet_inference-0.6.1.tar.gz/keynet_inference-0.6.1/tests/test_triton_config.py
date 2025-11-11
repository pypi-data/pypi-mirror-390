"""
Tests for _TritonConfig class.

These tests verify the S3 URI parsing logic, path cleaning,
and configuration initialization.
"""

import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_boto3():
    """Auto-mock boto3 for all tests in this module."""
    mock_boto3_module = MagicMock()
    mock_s3_client = MagicMock()
    mock_boto3_module.client.return_value = mock_s3_client

    # Inject into sys.modules
    original_boto3 = sys.modules.get("boto3")
    sys.modules["boto3"] = mock_boto3_module

    # Need to reload config module to pick up the mocked boto3
    if "keynet_inference.config" in sys.modules:
        del sys.modules["keynet_inference.config"]

    yield mock_boto3_module

    # Restore original
    if original_boto3:
        sys.modules["boto3"] = original_boto3
    elif "boto3" in sys.modules:
        del sys.modules["boto3"]

    # Reload config to restore original state
    if "keynet_inference.config" in sys.modules:
        del sys.modules["keynet_inference.config"]


class TestTritonConfigInitialization:
    """Test _TritonConfig initialization and environment variable handling."""

    def test_init_requires_env_vars(self):
        """Test that initialization requires environment variables."""
        from keynet_inference.config import _TritonConfig

        # Without TRITON_URL or TRITON_MODEL_REPO, should raise Exception
        with pytest.raises((Exception, OSError)):
            _TritonConfig()

    def test_init_with_local_model_repo(self):
        """Test initialization with local file system model repository."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "/local/path/models")

            config = _TritonConfig()
            assert config["triton_url"] == "localhost:8001"
            assert config["triton_model_repo"] == "/local/path/models"
            assert "s3" not in config

    def test_init_with_s3_model_repo(self):
        """Test initialization with S3 model repository."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://my-bucket/models")

            config = _TritonConfig()
            assert config["triton_url"] == "localhost:8001"
            assert config["s3_bucket"] == "my-bucket"
            assert config["s3_prefix"] == "models"
            assert "s3" in config

    def test_init_with_model_name(self):
        """Test initialization with MODEL_NAME environment variable."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "/local/path/models")
            mp.setenv("MODEL_NAME", "yolo-v8")

            config = _TritonConfig()
            assert config["model_name"] == "yolo-v8"

    def test_init_without_model_name(self):
        """Test initialization without MODEL_NAME (optional)."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "/local/path/models")
            # MODEL_NAME not set

            config = _TritonConfig()
            assert config.get("model_name") is None


class TestS3PathParsing:
    """Test S3 URI parsing logic."""

    def test_parse_s3_uri_with_endpoint(self):
        """Test parsing S3 URI with endpoint and port."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv(
                "TRITON_MODEL_REPO",
                "s3://http://minio:9000/my-bucket/models/subdir",
            )

            config = _TritonConfig()
            uri = config.parse_path("s3://http://minio:9000/my-bucket/models/subdir")

            assert uri.protocol == "http://"
            assert uri.host_name == "minio"
            assert uri.host_port == "9000"
            assert uri.bucket == "my-bucket"
            assert uri.prefix == "models/subdir"

    def test_parse_simple_s3_uri(self):
        """Test parsing simple S3 URI without endpoint."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://my-bucket/models")

            config = _TritonConfig()
            uri = config.parse_path("s3://my-bucket/models")

            assert uri.protocol == ""
            assert uri.host_name == ""
            assert uri.host_port == ""
            assert uri.bucket == "my-bucket"
            assert uri.prefix == "models"

    def test_parse_s3_uri_bucket_only(self):
        """Test parsing S3 URI with bucket only (no prefix)."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://my-bucket")

            config = _TritonConfig()
            uri = config.parse_path("s3://my-bucket")

            assert uri.bucket == "my-bucket"
            assert uri.prefix == ""

    def test_parse_invalid_s3_uri_no_bucket(self):
        """Test that invalid S3 URI without bucket raises exception."""
        from mlflow.exceptions import MlflowException

        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://bucket")

            config = _TritonConfig()
            with pytest.raises(MlflowException, match="Invalid bucket name"):
                config.parse_path("s3://")


class TestS3PathCleaning:
    """Test S3 path cleaning logic."""

    def test_clean_path_extra_slashes(self):
        """Test cleaning path with extra internal slashes."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://bucket/path")

            config = _TritonConfig()
            cleaned = config.clean_path("s3://my-bucket///models//subdir")

            # clean_path removes internal double slashes but preserves structure
            assert "///" not in cleaned
            assert cleaned.startswith("s3://my-bucket/")
            assert "models" in cleaned
            assert "subdir" in cleaned

    def test_clean_path_handles_slashes(self):
        """Test that clean_path handles various slash patterns."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://bucket/path")

            config = _TritonConfig()

            # Test that path structure is preserved
            cleaned = config.clean_path("s3://my-bucket/models")
            assert cleaned.startswith("s3://my-bucket")
            assert "models" in cleaned

            # Test that excessive slashes are reduced
            cleaned_multi = config.clean_path("s3://my-bucket///models")
            assert "///" not in cleaned_multi  # No triple slashes

    def test_clean_path_invalid_empty_bucket(self):
        """Test that empty bucket name raises exception."""
        from mlflow.exceptions import MlflowException

        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://bucket/path")

            config = _TritonConfig()
            with pytest.raises(MlflowException, match="Invalid bucket name"):
                config.clean_path("s3://////")


class TestConfigDictInterface:
    """Test that _TritonConfig behaves like a dict."""

    def test_dict_access(self):
        """Test dictionary-style access."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://bucket/models")

            config = _TritonConfig()

            # Test __getitem__
            assert config["triton_url"] == "localhost:8001"

            # Test get() with default
            assert config.get("nonexistent", "default") == "default"

            # Test 'in' operator
            assert "triton_url" in config
            assert "nonexistent" not in config

    def test_dict_inheritance(self):
        """Test that _TritonConfig properly inherits from dict."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://bucket/models")

            config = _TritonConfig()

            # Should be instance of dict
            assert isinstance(config, dict)

            # Should support dict operations
            keys = list(config.keys())
            assert "triton_url" in keys
            assert "triton_model_repo" in keys


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_minio_deployment(self):
        """Test typical MinIO deployment configuration."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "triton-server:8001")
            mp.setenv(
                "TRITON_MODEL_REPO",
                "s3://http://minio-service:9000/triton-models/production",
            )

            config = _TritonConfig()

            assert config["triton_url"] == "triton-server:8001"
            assert config["s3_bucket"] == "triton-models"
            assert config["s3_prefix"] == "production"
            assert "s3" in config

    def test_aws_s3_deployment(self):
        """Test AWS S3 deployment configuration."""
        from keynet_inference.config import _TritonConfig

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("TRITON_URL", "localhost:8001")
            mp.setenv("TRITON_MODEL_REPO", "s3://my-company-ml-models/triton/v2")

            config = _TritonConfig()

            assert config["s3_bucket"] == "my-company-ml-models"
            assert config["s3_prefix"] == "triton/v2"
            assert "s3" in config
