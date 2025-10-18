"""
Integration tests for the CLI executable. These tests call the CLI directly
and verify that the output matches expected fixtures.
"""

import os
import subprocess
from itertools import product
from typing import Union

import pytest

from pdf_watermark.options import (
    DrawingOptions,
    FilesOptions,
    GridOptions,
    InsertOptions,
)
from tests.test_add_watermark_from_options import (
    DRAWING_OPTIONS,
    FILES_OPTIONS,
    FIXTURES,
    GRID_OPTIONS,
    INPUT,
    INSERT_OPTIONS,
    OUTPUT,
)
from tests.utils import assert_pdfs_are_close


@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(OUTPUT):
        os.remove(OUTPUT)


@pytest.mark.parametrize(
    "files_options, drawing_options, specific_options, fixture",
    [
        (a, b, c, d)
        for (a, b, c), d in zip(
            product(
                FILES_OPTIONS,
                DRAWING_OPTIONS,
                GRID_OPTIONS + INSERT_OPTIONS,
            ),
            FIXTURES,
        )
    ],
)
def test_cli_watermark(
    files_options: FilesOptions,
    drawing_options: DrawingOptions,
    specific_options: Union[GridOptions, InsertOptions],
    fixture: str,
):
    """Test CLI commands produce expected output PDFs."""
    command = [
        "python",
        "-m",
        "pdf_watermark.watermark",
        "grid" if isinstance(specific_options, GridOptions) else "insert",
        str(files_options.file),
        drawing_options.watermark,
        "--save",
        str(files_options.output),
    ]

    # Run the CLI command
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    # Check that the command succeeded
    assert result.returncode == 0, f"CLI command failed: {result.stderr}"

    # Verify the output matches the expected fixture
    assert_pdfs_are_close(OUTPUT, fixture)


def test_cli_help_commands():
    """Test that help commands work correctly."""
    # Test main help
    result = subprocess.run(
        ["python", "-m", "pdf_watermark.watermark", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "grid" in result.stdout
    assert "insert" in result.stdout

    # Test grid help
    result = subprocess.run(
        ["python", "-m", "pdf_watermark.watermark", "grid", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "horizontal-boxes" in result.stdout

    # Test insert help
    result = subprocess.run(
        ["python", "-m", "pdf_watermark.watermark", "insert", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--x" in result.stdout
    assert "--y" in result.stdout


def test_cli_dry_run():
    """Test that dry-run flag doesn't create output files."""
    output = "dry_run_output.pdf"
    command = [
        "python",
        "-m",
        "pdf_watermark.watermark",
        "grid",
        INPUT,
        "DRY RUN",
        "--save",
        output,
        "--dry-run",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert not os.path.exists(output), (
        "Output file should not be created with --dry-run"
    )


def test_cli_invalid_input_file():
    """Test CLI behavior with non-existent input file."""
    command = [
        "python",
        "-m",
        "pdf_watermark.watermark",
        "grid",
        "nonexistent.pdf",
        "TEST",
        "--save",
        OUTPUT,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, "CLI should fail with non-existent input file"
