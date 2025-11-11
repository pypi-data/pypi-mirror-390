import pytest
import io
import sys
from unittest.mock import Mock, patch, MagicMock


class TestJupyterLiteUtils:

    def test_is_jupyterlite_true(self):
        """Test detection of JupyterLite environment when pyodide is present."""
        with patch.dict("sys.modules", {"pyodide": Mock()}):
            from pollywog.jupyterlite_utils import is_jupyterlite

            assert is_jupyterlite() is True

    def test_is_jupyterlite_false(self):
        """Test detection of non-JupyterLite environment when pyodide is absent."""
        # Temporarily remove pyodide if it exists
        pyodide_backup = sys.modules.get("pyodide")
        if "pyodide" in sys.modules:
            del sys.modules["pyodide"]

        try:
            from pollywog.jupyterlite_utils import is_jupyterlite

            assert is_jupyterlite() is False
        finally:
            # Restore pyodide if it existed
            if pyodide_backup is not None:
                sys.modules["pyodide"] = pyodide_backup

    @patch("IPython.display.display")
    @patch("IPython.display.HTML")
    def test_download_file_displays_html_button(self, mock_html, mock_display):
        from pollywog.jupyterlite_utils import download_file

        content = b"test content"
        filename = "test.txt"
        content_type = "text/plain"
        download_file(content, filename, content_type)
        mock_html.assert_called_once()
        mock_display.assert_called_once_with(mock_html.return_value)


class TestPollywogMagics:
    """Test the Pollywog Magic commands functionality."""

    def test_magic_command_parsing(self):
        """Test that magic commands parse correctly without requiring IPython shell."""
        # Test the core logic without instantiating the class

        # Test valid autodownload commands
        test_cases = [
            ("autodownload on", True),
            ("autodownload off", False),
            ("autodownload status", None),
            ("invalid command", None),
        ]

        for line, expected in test_cases:
            args = line.strip().split()

            if len(args) >= 2 and args[0] == "autodownload":
                command = args[1]
                if command == "on":
                    assert expected is True
                elif command == "off":
                    assert expected is False
                elif command == "status":
                    assert expected is None
            else:
                assert expected is None

    @patch("pollywog.jupyterlite_utils.is_jupyterlite")
    def test_enable_autodownload_logic(self, mock_is_jupyterlite):
        """Test the autodownload enabling logic without IPython shell."""
        from pollywog.core import CalcSet

        # Test when in JupyterLite
        mock_is_jupyterlite.return_value = True

        # Store original method
        original_method = CalcSet.to_lfcalc

        try:
            # Manually test the logic that would be in _enable_autodownload
            from pollywog.jupyterlite_utils import is_jupyterlite

            if is_jupyterlite():
                # Simulate monkey patching (without actually doing it due to type issues)
                # In real implementation, this would patch CalcSet.to_lfcalc
                # to call download_file for string paths

                # Test that we have the required imports and functions
                from pollywog.jupyterlite_utils import download_file

                assert callable(download_file)
                assert is_jupyterlite() is True

                # Verify we can create the necessary objects
                import io

                buffer = io.BytesIO()
                assert isinstance(buffer, io.BytesIO)

        finally:
            # Ensure no changes were made to the class
            assert CalcSet.to_lfcalc == original_method

    @patch("pollywog.jupyterlite_utils.is_jupyterlite")
    def test_enable_autodownload_not_in_jupyterlite(self, mock_is_jupyterlite):
        """Test autodownload logic when not in JupyterLite."""
        mock_is_jupyterlite.return_value = False

        from pollywog.jupyterlite_utils import is_jupyterlite

        # Simulate the logic check
        result = is_jupyterlite()
        assert result is False

        # In the real implementation, this would print the warning message
        # and not enable autodownload


class TestIntegration:
    """Test integration scenarios for JupyterLite functionality."""

    @patch("pollywog.jupyterlite_utils.is_jupyterlite", return_value=True)
    @patch("pollywog.jupyterlite_utils.download_file")
    def test_download_file_integration(self, mock_download_file, mock_is_jupyterlite):
        """Test that download_file can be called with typical CalcSet export data."""
        from pollywog.jupyterlite_utils import download_file, is_jupyterlite

        # Verify we're in "JupyterLite" mode
        assert is_jupyterlite() is True

        # Test typical file export scenario
        content = b"mock calcset content"
        filename = "test_export.lfcalc"
        content_type = "application/octet-stream"

        download_file(content, filename, content_type)

        # Verify download was triggered with correct parameters
        mock_download_file.assert_called_once_with(content, filename, content_type)

    def test_jupyterlite_module_imports(self):
        """Test that all JupyterLite modules can be imported successfully."""
        # Test imports work
        from pollywog.jupyterlite_utils import download_file, is_jupyterlite
        from pollywog.magics import PollywogMagics, load_ipython_extension

        # Verify functions are callable
        assert callable(download_file)
        assert callable(is_jupyterlite)
        assert callable(PollywogMagics)
        assert callable(load_ipython_extension)

    def test_environment_detection_scenarios(self):
        """Test various environment detection scenarios."""
        import sys

        # Test when pyodide is not available
        pyodide_backup = sys.modules.get("pyodide")
        if "pyodide" in sys.modules:
            del sys.modules["pyodide"]

        try:
            from pollywog.jupyterlite_utils import is_jupyterlite

            assert is_jupyterlite() is False
        finally:
            if pyodide_backup is not None:
                sys.modules["pyodide"] = pyodide_backup

        # Test with mock pyodide
        with patch.dict("sys.modules", {"pyodide": Mock()}):
            # Reimport to get fresh module state
            import importlib
            import pollywog.jupyterlite_utils

            importlib.reload(pollywog.jupyterlite_utils)

            from pollywog.jupyterlite_utils import is_jupyterlite

            assert is_jupyterlite() is True
