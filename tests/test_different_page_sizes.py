"""
Test for PDFs with different page sizes.
"""

import os

import pytest

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import DrawingOptions, FilesOptions, GridOptions
from tests.utils import assert_pdfs_are_close

INPUT = "tests/fixtures/different_sizes_input.pdf"
OUTPUT = "output.pdf"
FIXTURE = "tests/fixtures/different_sizes_output.pdf"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    os.remove(OUTPUT)


def test_different_page_sizes():
    add_watermark_from_options(
        files_options=FilesOptions(INPUT, OUTPUT),
        drawing_options=DrawingOptions(watermark="watermark"),
        specific_options=GridOptions(),
    )
    assert_pdfs_are_close(OUTPUT, FIXTURE)
