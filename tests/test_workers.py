"""
Test parallel processing of multiple PDFs.
"""

import os
from shutil import rmtree

import pytest

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import DrawingOptions, FilesOptions, GridOptions
from tests.utils import assert_pdfs_are_close

INPUT = "tests/fixtures/workers/inputs"
FIXTURES = "tests/fixtures/workers/outputs"
OUTPUT = "output"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    rmtree(OUTPUT)


def test_different_page_sizes():
    files_options = FilesOptions(INPUT, OUTPUT, workers=4)
    add_watermark_from_options(
        files_options=files_options,
        drawing_options=DrawingOptions(watermark="watermark"),
        specific_options=GridOptions(),
    )
    for file in files_options.output_files:
        assert_pdfs_are_close(file, os.path.join(FIXTURES, os.path.basename(file)))
