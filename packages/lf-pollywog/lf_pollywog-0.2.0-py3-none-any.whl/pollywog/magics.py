from IPython.core.magic import Magics, line_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.core.events import EventManager
import io
import ast
import inspect


@magics_class
class PollywogMagics(Magics):
    """
    IPython magic commands for pollywog.

    This class provides custom magic commands to enhance pollywog's functionality
    in Jupyter notebooks, particularly for JupyterLite environments.

    Available commands:
        %pollywog autodownload on/off/status - Manage automatic display of download buttons for exported files
    """

    def __init__(self, shell):
        """
        Initialize the PollywogMagics extension.

        Args:
            shell: IPython shell instance.
        """
        super().__init__(shell)
        self.autodownload_enabled = False
        self._original_to_lfcalc = None

    @line_magic
    @magic_arguments()
    @argument(
        "command",
        choices=["on", "off", "status"],
        help="Enable/disable autodownload (download button appears automatically)",
    )
    def pollywog(self, line):
        """
        Pollywog magic commands for Jupyter notebooks.

        This magic command provides utilities for working with pollywog in
        notebook environments, especially JupyterLite.

        Usage:
            %pollywog autodownload on     - Enable automatic display of download button for .lfcalc files in JupyterLite
            %pollywog autodownload off    - Disable automatic download button
            %pollywog autodownload status - Show current autodownload status

        When autodownload is enabled in JupyterLite, calling CalcSet.to_lfcalc()
        will automatically display a download button below the cell, allowing you to save the file to your computer. The file is not downloaded automatically; you must click the button.
        """
        args = line.strip().split()

        if len(args) < 2 or args[0] != "autodownload":
            print("Usage: %pollywog autodownload [on|off|status]")
            return

        command = args[1]

        if command == "on":
            self._enable_autodownload()
            print(
                "Pollywog autodownload enabled (download button will appear automatically)"
            )
        elif command == "off":
            self._disable_autodownload()
            print(
                "Pollywog autodownload disabled (download button will not appear automatically)"
            )
        elif command == "status":
            status = "enabled" if self.autodownload_enabled else "disabled"
            print(
                f"Pollywog autodownload is {status} (download button {'will' if status == 'enabled' else 'will not'} appear automatically)"
            )

    def _enable_autodownload(self):
        if not self.autodownload_enabled:
            try:
                from pollywog.core import CalcSet
                from pollywog.jupyterlite_utils import is_jupyterlite, download_file

                if is_jupyterlite():
                    # Monkey patch CalcSet.to_lfcalc in JupyterLite
                    if self._original_to_lfcalc is None:
                        self._original_to_lfcalc = CalcSet.to_lfcalc

                    def patched_to_lfcalc(self, filepath_or_buffer, sort_items=True):
                        if isinstance(
                            filepath_or_buffer, (str, type(None).__class__.__bases__[0])
                        ):  # str or Path
                            # Generate file content and trigger download
                            buffer = io.BytesIO()
                            self._original_to_lfcalc(buffer, sort_items=sort_items)
                            buffer_data = buffer.getvalue()
                            download_file(
                                buffer_data,
                                str(filepath_or_buffer),
                                "application/octet-stream",
                            )
                            # save the buffer content to a file as well. We could just call _original_to_lfcalc again,
                            # but this avoids any side effects of multiple calls.
                            with open(str(filepath_or_buffer), "wb") as f:
                                f.write(buffer_data)
                        else:
                            # Call original method for file-like objects
                            self._original_to_lfcalc(
                                filepath_or_buffer, sort_items=sort_items
                            )

                    CalcSet._original_to_lfcalc = CalcSet.to_lfcalc
                    CalcSet.to_lfcalc = patched_to_lfcalc
                    self.autodownload_enabled = True
                else:
                    print(
                        "Autodownload (download button) only works in JupyterLite environment"
                    )

            except ImportError as e:
                print(f"Could not enable autodownload (download button): {e}")

    def _disable_autodownload(self):
        if self.autodownload_enabled and self._original_to_lfcalc is not None:
            try:
                from pollywog.core import CalcSet

                CalcSet.to_lfcalc = self._original_to_lfcalc
                self.autodownload_enabled = False
            except ImportError:
                pass


def load_ipython_extension(ipython):
    """
    Load the pollywog IPython extension.

    This function is called by IPython when the extension is loaded via
    %load_ext pollywog.magics.

    Args:
        ipython: IPython shell instance.
    """
    ipython.register_magic_function(
        PollywogMagics(ipython).pollywog, "line", "pollywog"
    )


def unload_ipython_extension(ipython):
    """
    Unload the pollywog IPython extension.

    This function is called by IPython when the extension is unloaded via
    %unload_ext pollywog.magics.

    Args:
        ipython: IPython shell instance.
    """
    # Clean up if needed
    pass
