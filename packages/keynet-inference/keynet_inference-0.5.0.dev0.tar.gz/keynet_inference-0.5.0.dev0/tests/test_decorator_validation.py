from unittest.mock import patch

import pytest

from keynet_inference.function.decorator import keynet_function


class TestDecoratorValidation:
    """Test @keynet_function decorator signature validation"""

    def test_valid_main_function(self):
        """Valid main function with single args parameter"""

        @keynet_function("test-function")
        def main(args):
            return {"result": "success"}

        # Should not raise any exception
        result = main({"test": "data"})
        assert result == {"result": "success"}

    def test_invalid_no_parameters(self):
        """Main function with no parameters should fail"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main():
                return {"result": "success"}

    def test_invalid_wrong_parameter_name(self):
        """Main function with wrong parameter name should fail"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main(params):
                return {"result": "success"}

    def test_invalid_multiple_parameters(self):
        """Main function with multiple parameters should fail"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main(args, extra):
                return {"result": "success"}

    def test_function_with_kwargs(self):
        """Test that function with kwargs raises error"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main(args, **kwargs):
                return {}

    def test_function_with_defaults(self):
        """Test that function with default args raises error"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main(args, optional=None):
                return {}

    def test_decorator_with_empty_name(self):
        """Test decorator with empty name string"""
        with pytest.raises(
            ValueError, match="Function name must be a non-empty string"
        ):

            @keynet_function("")
            def main(args):
                return {}

    def test_decorator_with_whitespace_name(self):
        """Test decorator with whitespace-only name"""
        with pytest.raises(
            ValueError, match="Function name must be a non-empty string"
        ):

            @keynet_function("   ")
            def main(args):
                return {}

    def test_decorator_with_non_string_name(self):
        """Test decorator with non-string name"""
        with pytest.raises(
            ValueError, match="Function name must be a non-empty string"
        ):

            @keynet_function(123)  # type: ignore
            def main(args):
                return {}

    def test_auto_load_env(self):
        """Test that load_env is automatically called with args"""

        @keynet_function("test-function")
        def main(args):
            return {"input": args}

        # load_env should always be called with args dict
        with patch("keynet_inference.config.load_env") as mock_load_env:
            test_args = {"param": "value", "MLFLOW_TRACKING_URI": "http://..."}
            result = main(test_args)

            # load_env should be called with the args
            mock_load_env.assert_called_once_with(test_args)
            assert result == {"input": test_args}

    def test_load_env_import_error_handling(self):
        """Test handling of load_env import errors"""

        @keynet_function("test-function")
        def main(args):
            return {"input": args}

        # Mock the module import to raise error
        import sys

        original_modules = sys.modules.copy()
        sys.modules["keynet_inference.config"] = None

        try:
            # Should raise import error when trying to import
            with pytest.raises((ImportError, AttributeError)):
                main({"param": "value"})
        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_load_env_execution_error(self):
        """Test handling of load_env execution errors"""

        @keynet_function("test-function")
        def main(args):
            return {"input": args}

        # Mock load_env to raise an exception
        with patch(
            "keynet_inference.config.load_env",
            side_effect=Exception("Load env failed"),
        ):
            # Should propagate the exception
            with pytest.raises(Exception, match="Load env failed"):
                main({"param": "value"})
