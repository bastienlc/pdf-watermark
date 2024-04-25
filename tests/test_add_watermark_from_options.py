"""
Test the outputs of the CLI with a bunch of different options on simple features. These tests are far from perfect.
"""

import os

import pytest

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import (
    DrawingOptions,
    FilesOptions,
    GridOptions,
    InsertOptions,
)
from pdf_watermark.watermark import DEFAULTS
from tests.utils import assert_pdfs_are_close

INPUT = "tests/fixtures/input.pdf"
OUTPUT = "output.pdf"
FIXTURES = [
    "tests/fixtures/0.pdf",
    "tests/fixtures/1.pdf",
    "tests/fixtures/2.pdf",
    "tests/fixtures/3.pdf",
]


@pytest.fixture(autouse=True)
def cleanup():
    yield
    os.remove(OUTPUT)


DRAWING_OPTIONS_FIXTURES = [
    DrawingOptions(
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
    ),
    DrawingOptions(
        watermark=r"watermark\nwith\nline\nbreaks",
        opacity=DEFAULTS.opacity,
        angle=DEFAULTS.angle,
        text_color=DEFAULTS.text_color,
        text_font=DEFAULTS.text_font,
        text_size=DEFAULTS.text_size,
        unselectable=DEFAULTS.unselectable,
        image_scale=DEFAULTS.image_scale,
        save_as_image=DEFAULTS.save_as_image,
        dpi=DEFAULTS.dpi,
    ),
]

FILES_OPTIONS_FIXTURES = [FilesOptions(INPUT, OUTPUT)]

GRID_OPTIONS_FIXTURES = [
    GridOptions(
        horizontal_boxes=DEFAULTS.horizontal_boxes,
        vertical_boxes=DEFAULTS.vertical_boxes,
        margin=DEFAULTS.margin,
    )
]

INSERT_OPTIONS_FIXTURES = [
    InsertOptions(
        y=DEFAULTS.y,
        x=DEFAULTS.x,
        horizontal_alignment=DEFAULTS.horizontal_alignment,
    )
]


def test_add_watermark_from_options():
    index = 0
    for files_options in FILES_OPTIONS_FIXTURES:
        for drawing_options in DRAWING_OPTIONS_FIXTURES:
            for specific_options in GRID_OPTIONS_FIXTURES + INSERT_OPTIONS_FIXTURES:
                add_watermark_from_options(
                    files_options=files_options,
                    drawing_options=drawing_options,
                    specific_options=specific_options,
                )
                assert_pdfs_are_close(OUTPUT, FIXTURES[index])
                index += 1
