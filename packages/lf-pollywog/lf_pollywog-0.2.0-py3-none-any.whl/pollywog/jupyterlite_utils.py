"""
JupyterLite utilities for browser-based file operations.

This module provides helper functions for working with pollywog in JupyterLite,
a browser-based Jupyter environment that runs entirely in the client.
"""

from IPython.display import display, HTML


def download_file(content, filename, content_type="application/octet-stream"):
    """
    Display a download button in JupyterLite or Jupyter Notebook to save generated files
    (like .lfcalc files) directly to the user's computer. This uses a browser data URL and
    works in any notebook environment that supports HTML display.

    Args:
        content (str or bytes): File content to download.
        filename (str): Name of the file to download.
        content_type (str): MIME type of the file.
            Defaults to "application/octet-stream".

    Example:
        >>> from pollywog.jupyterlite_utils import download_file
        >>> download_file(b"Hello, world!", "test.txt", "text/plain")
    """
    import base64
    from IPython.display import display, HTML

    # Convert content to base64
    if isinstance(content, str):
        content_bytes = content.encode("utf-8")
    else:
        content_bytes = content
    content_b64 = base64.b64encode(content_bytes).decode("ascii")

    # Create a data URL for the file
    data_url = f"data:{content_type};base64,{content_b64}"
    html = f"""<a download="{filename}" href="{data_url}">
        <button style="font-size:1em;padding:0.5em 1em;margin:0.5em 0;">Download {filename}</button>
    </a>"""
    display(HTML(html))


def is_jupyterlite():
    """
    Check if code is running in a JupyterLite environment.

    JupyterLite is a browser-based Jupyter distribution that runs entirely
    in the client using Pyodide (Python compiled to WebAssembly). This function
    detects if the current environment is JupyterLite by checking for the
    pyodide module.

    Returns:
        bool: True if running in JupyterLite, False otherwise.

    Example:
        >>> from pollywog.jupyterlite_utils import is_jupyterlite
        >>> if is_jupyterlite():
        ...     print("Running in browser!")
    """
    try:
        import sys

        return "pyodide" in sys.modules
    except:
        return False
