"""
Test parallel processing of multiple PDFs.
"""

import os
from shutil import rmtree

import pytest

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import DrawingOptions, FilesOptions, GridOptions
from pdf_watermark.watermark import DEFAULTS
from tests.utils import assert_pdfs_are_close

INPUT = "tests/fixtures/workers/inputs"
FIXTURES = "tests/fixtures/workers/outputs"
OUTPUT = "output"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    rmtree(OUTPUT)


DRAWING_OPTIONS = DrawingOptions(
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

FILES_OPTIONS = FilesOptions(INPUT, OUTPUT, dry_run=DEFAULTS.dry_run, workers=4)

GRID_OPTIONS = GridOptions(
    horizontal_boxes=DEFAULTS.horizontal_boxes,
    vertical_boxes=DEFAULTS.vertical_boxes,
    margin=DEFAULTS.margin,
)


def test_different_page_sizes():
    add_watermark_from_options(
        files_options=FILES_OPTIONS,
        drawing_options=DRAWING_OPTIONS,
        specific_options=GRID_OPTIONS,
        verbose=False,
    )
    for file in FILES_OPTIONS.output_files:
        assert_pdfs_are_close(file, os.path.join(FIXTURES, os.path.basename(file)))
