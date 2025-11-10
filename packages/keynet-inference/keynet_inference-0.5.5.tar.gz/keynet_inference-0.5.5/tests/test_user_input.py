"""Tests for UserInput class and integration with keynet_function decorator."""

import pytest

from keynet_inference import UserInput, keynet_function


class TestUserInputClass:
    """Tests for UserInput class basic functionality."""

    def test_user_input_filters_env_vars(self):
        """UserInput should exclude environment variable keys."""
        original = {
            "TRITON_URL": "localhost:8001",
            "MODEL_NAME": "yolo-v8",
            "MLFLOW_TRACKING_URI": "http://mlflow:5000",
            "image_url": "s3://bucket/img.jpg",
            "threshold": 0.5,
        }

        user_input = UserInput(original)

        # Environment variables should be excluded
        assert "TRITON_URL" not in user_input
        assert "MODEL_NAME" not in user_input
        assert "MLFLOW_TRACKING_URI" not in user_input

        # User input should be preserved
        assert "image_url" in user_input
        assert "threshold" in user_input
        assert user_input["image_url"] == "s3://bucket/img.jpg"
        assert user_input["threshold"] == 0.5

    def test_user_input_dict_methods(self):
        """UserInput should support standard dict methods."""
        user_input = UserInput({"key1": "value1", "key2": "value2"})

        # Dict-like access
        assert user_input["key1"] == "value1"
        # Use dict.get() function instead of instance method
        assert dict.get(user_input, "key2") == "value2"
        assert dict.get(user_input, "missing", "default") == "default"

        # Contains
        assert "key1" in user_input
        assert "missing" not in user_input

        # Keys/values/items
        assert set(user_input.keys()) == {"key1", "key2"}
        assert set(user_input.values()) == {"value1", "value2"}

    def test_user_input_empty_args(self):
        """UserInput should work with empty dict."""
        user_input = UserInput({})
        assert len(user_input) == 0
        assert dict.get(user_input, "any_key") is None

    def test_user_input_only_env_vars(self):
        """UserInput should be empty if args only contain env vars."""
        original = {
            "TRITON_URL": "localhost:8001",
            "MODEL_NAME": "yolo-v8",
            "AWS_ACCESS_KEY_ID": "key",
        }

        user_input = UserInput(original)
        assert len(user_input) == 0


class TestUserInputSingleton:
    """Tests for UserInput singleton pattern."""

    def test_get_outside_decorator_raises_error(self):
        """UserInput.get() should raise error outside @keynet_function."""
        with pytest.raises(RuntimeError, match="UserInput is not initialized"):
            UserInput.get("any_key")

    def test_get_current_returns_none_outside_decorator(self):
        """UserInput.get_current() should return None outside @keynet_function."""
        assert UserInput.get_current() is None


class TestUserInputWithDecorator:
    """Tests for UserInput integration with @keynet_function decorator."""

    def test_decorator_provides_user_input(self):
        """@keynet_function should set up UserInput singleton."""

        @keynet_function("test")
        def main(args):
            # UserInput singleton should be available
            current = UserInput.get_current()
            assert isinstance(current, UserInput)
            assert "image_url" in current
            assert "threshold" in current
            assert "TRITON_URL" not in current
            return UserInput.get("image_url")

        args = {
            "TRITON_URL": "localhost:8001",
            "image_url": "s3://test",
            "threshold": 0.5,
        }

        result = main(args)
        assert result == "s3://test"

    def test_singleton_access_in_decorated_function(self):
        """UserInput.get() should work inside @keynet_function."""

        def helper_function():
            # Access from nested function via singleton
            threshold = UserInput.get("threshold", 0.5)
            debug = UserInput.get("debug", False)
            return threshold, debug

        @keynet_function("test")
        def main(args):
            # Access via UserInput singleton
            assert UserInput.get("image_url") == "s3://test"
            threshold, debug = helper_function()
            assert threshold == 0.7
            assert debug is False
            return True

        args = {
            "TRITON_URL": "localhost:8001",
            "image_url": "s3://test",
            "threshold": 0.7,
        }

        result = main(args)
        assert result is True

    def test_singleton_cleared_after_function(self):
        """UserInput singleton should be cleared after function execution."""

        @keynet_function("test")
        def main(args):
            assert UserInput.get_current() is not None
            return True

        args = {"image_url": "s3://test"}
        main(args)

        # Should be cleared after execution
        assert UserInput.get_current() is None

    def test_multiple_calls_use_different_instances(self):
        """Each function call should get its own UserInput instance."""

        @keynet_function("test")
        def main(args):
            return UserInput.get("value")

        result1 = main({"value": "first"})
        result2 = main({"value": "second"})

        assert result1 == "first"
        assert result2 == "second"

    def test_nested_functions_share_singleton(self):
        """Nested functions should access same UserInput instance."""
        instances = []

        def helper():
            instances.append(UserInput.get_current())
            return UserInput.get("image_url")

        @keynet_function("test")
        def main(args):
            instances.append(UserInput.get_current())
            url = helper()
            return url

        args = {"image_url": "s3://test"}
        result = main(args)

        assert result == "s3://test"
        assert len(instances) == 2
        assert instances[0] is instances[1]  # Same instance


class TestUserInputEnvironmentVariables:
    """Tests for environment variable loading with UserInput."""

    def test_env_vars_loaded_to_os_environ(self, monkeypatch):
        """Environment variables should be loaded to os.environ."""
        import os

        @keynet_function("test")
        def main(args):
            # Check that env vars were loaded
            assert os.environ.get("TRITON_URL") == "localhost:8001"
            assert os.environ.get("MODEL_NAME") == "yolo-v8"
            # UserInput should not contain them
            current = UserInput.get_current()
            assert "TRITON_URL" not in current
            assert "MODEL_NAME" not in current
            return True

        args = {
            "TRITON_URL": "localhost:8001",
            "MODEL_NAME": "yolo-v8",
            "image_url": "s3://test",
        }

        result = main(args)
        assert result is True
