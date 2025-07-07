"""
Test for PDFs with different page sizes.
"""

import os

import pytest

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import DrawingOptions, FilesOptions, GridOptions
from pdf_watermark.watermark import DEFAULTS
from tests.utils import assert_pdfs_are_close

INPUT = "tests/fixtures/different_sizes_input.pdf"
OUTPUT = "output.pdf"
FIXTURE = "tests/fixtures/different_sizes_output.pdf"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    os.remove(OUTPUT)


DRAWING_OPTIONS_FIXTURE = DrawingOptions(
    watermark="watermark",
    opacity=DEFAULTS.opacity,
    angle=DEFAULTS.angle,
    text_color=DEFAULTS.text_color,
    text_font=DEFAULTS.text_font,
    text_size=DEFAULTS.text_size,
    unselectable=DEFAULTS.unselectable,
    image_scale=DEFAULTS.image_scale,
    save_as_image=DEFAULTS.save_as_image,
    dpi=DEFAULTS.dpi,
)

FILES_OPTIONS_FIXTURE = FilesOptions(INPUT, OUTPUT, dry_run=False)

GRID_OPTIONS_FIXTURE = GridOptions(
    horizontal_boxes=DEFAULTS.horizontal_boxes,
    vertical_boxes=DEFAULTS.vertical_boxes,
    margin=DEFAULTS.margin,
)


def test_different_page_sizes():
    add_watermark_from_options(
        files_options=FILES_OPTIONS_FIXTURE,
        drawing_options=DRAWING_OPTIONS_FIXTURE,
        specific_options=GRID_OPTIONS_FIXTURE,
    )
    assert_pdfs_are_close(OUTPUT, FIXTURE)
