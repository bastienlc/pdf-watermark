"""
Integration tests for the CLI executable. These tests call the CLI directly
and verify that the output matches expected fixtures.
"""

import os
from itertools import product
from typing import Union

import pytest
from click.testing import CliRunner

from pdf_watermark.options import (
    DrawingOptions,
    FilesOptions,
    GridOptions,
    InsertOptions,
)
from pdf_watermark.watermark import cli
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
    runner = CliRunner()

    command = [
        "grid" if isinstance(specific_options, GridOptions) else "insert",
        str(files_options.file),
        drawing_options.watermark,
        "--save",
        str(files_options.output),
    ]

    # Run the CLI command
    result = runner.invoke(cli, command)

    # Check that the command succeeded
    assert result.exit_code == 0, f"CLI command failed: {result.output}"

    # Verify the output matches the expected fixture
    assert_pdfs_are_close(OUTPUT, fixture)


def test_cli_help_commands():
    """Test that help commands work correctly."""
    runner = CliRunner()

    # Test main help
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "grid" in result.output
    assert "insert" in result.output

    # Test grid help
    result = runner.invoke(cli, ["grid", "--help"])
    assert result.exit_code == 0
    assert "horizontal-boxes" in result.output

    # Test insert help
    result = runner.invoke(cli, ["insert", "--help"])
    assert result.exit_code == 0
    assert "--x" in result.output
    assert "--y" in result.output


def test_cli_dry_run():
    """Test that dry-run flag doesn't create output files."""
    runner = CliRunner()
    output = "dry_run_output.pdf"
    command = [
        "grid",
        INPUT,
        "DRY RUN",
        "--save",
        output,
        "--dry-run",
    ]

    result = runner.invoke(cli, command)

    assert result.exit_code == 0
    assert not os.path.exists(output), (
        "Output file should not be created with --dry-run"
    )


def test_cli_invalid_input_file():
    """Test CLI behavior with non-existent input file."""
    runner = CliRunner()
    command = [
        "grid",
        "nonexistent.pdf",
        "TEST",
        "--save",
        OUTPUT,
    ]

    result = runner.invoke(cli, command)

    assert result.exit_code != 0, "CLI should fail with non-existent input file"
