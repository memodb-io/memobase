"""Tests for api_key validation in MemoBaseClient and AsyncMemoBaseClient."""
import os
import pytest
from unittest.mock import patch

from memobase.core.entry import MemoBaseClient
from memobase.core.async_entry import AsyncMemoBaseClient


class TestMemoBaseClientApiKeyValidation:
    def test_empty_string_api_key_raises_value_error(self):
        with patch.dict(os.environ, {}, clear=True):
            # Remove MEMOBASE_API_KEY if set
            os.environ.pop("MEMOBASE_API_KEY", None)
            with pytest.raises(ValueError, match="api_key cannot be empty"):
                MemoBaseClient(api_key="")

    def test_none_api_key_raises_value_error(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MEMOBASE_API_KEY", None)
            with pytest.raises(ValueError, match="api_key cannot be empty"):
                MemoBaseClient(api_key=None)

    def test_missing_env_var_raises_value_error(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MEMOBASE_API_KEY", None)
            with pytest.raises(ValueError, match="api_key cannot be empty"):
                MemoBaseClient()

    def test_valid_api_key_does_not_raise(self):
        # Should not raise; httpx client init is fine with a fake URL+key
        client = MemoBaseClient(api_key="test-key-123")
        assert client.api_key == "test-key-123"

    def test_env_var_api_key_does_not_raise(self):
        with patch.dict(os.environ, {"MEMOBASE_API_KEY": "env-key-456"}):
            client = MemoBaseClient(api_key=None)
            assert client.api_key == "env-key-456"


class TestAsyncMemoBaseClientApiKeyValidation:
    def test_empty_string_api_key_raises_value_error(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MEMOBASE_API_KEY", None)
            with pytest.raises(ValueError, match="api_key cannot be empty"):
                AsyncMemoBaseClient(api_key="")

    def test_none_api_key_raises_value_error(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("MEMOBASE_API_KEY", None)
            with pytest.raises(ValueError, match="api_key cannot be empty"):
                AsyncMemoBaseClient(api_key=None)

    def test_valid_api_key_does_not_raise(self):
        client = AsyncMemoBaseClient(api_key="async-test-key-789")
        assert client.api_key == "async-test-key-789"
