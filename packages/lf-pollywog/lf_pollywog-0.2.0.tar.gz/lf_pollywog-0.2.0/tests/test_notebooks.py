"""Test that example notebooks execute without errors."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Get examples directory
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

# List of notebooks to test
NOTEBOOKS = [
    "basic_usage.ipynb",
    "conditional_logic.ipynb",
    "dependency_analysis.ipynb",
    "helper_functions.ipynb",
    "item_types_guide.ipynb",
    "modifying_lfcalc_files.ipynb",
    "pollywog_workflow_tutorial.ipynb",
    "querying_calcsets.ipynb",
    "running_with_dataframe.ipynb",
    "sklearn_conversion.ipynb",
    # Skip display and JupyterLite-specific notebooks
    # "display_final_workflow.ipynb",  # Requires .lfcalc file
    # "jupyterlite_demo.ipynb",  # JupyterLite-specific
    # "jupyterlite_quickstart.ipynb",  # JupyterLite-specific
]


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_notebook_executes(notebook_name):
    """Test that a notebook executes without errors."""
    notebook_path = EXAMPLES_DIR / notebook_name

    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.ipynb"

        # Use nbconvert to execute the notebook
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--ExecutePreprocessor.timeout=180",  # 3 minute timeout
                "--output",
                str(output_path),
                str(notebook_path),
            ],
            capture_output=True,
            text=True,
        )

        # Check if execution succeeded
        if result.returncode != 0:
            pytest.fail(
                f"Notebook {notebook_name} failed to execute:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )


def test_all_notebooks_exist():
    """Verify all notebooks in the list actually exist."""
    for notebook_name in NOTEBOOKS:
        notebook_path = EXAMPLES_DIR / notebook_name
        assert notebook_path.exists(), f"Notebook not found: {notebook_name}"
