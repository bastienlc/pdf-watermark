"""
Test the outputs of the CLI with a bunch of different options on simple features. These tests are far from perfect.
"""

import os
from itertools import product

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
INPUT_UPPERCASE = "tests/fixtures/input.PDF"
OUTPUT = "output.pdf"
FIXTURES = [
    "tests/fixtures/0.pdf",
    "tests/fixtures/1.pdf",
    "tests/fixtures/2.pdf",
    "tests/fixtures/3.pdf",
    "tests/fixtures/4.pdf",
    "tests/fixtures/5.pdf",
    "tests/fixtures/6.pdf",
    "tests/fixtures/7.pdf",
]


@pytest.fixture(autouse=True)
def cleanup():
    yield
    os.remove(OUTPUT)


DRAWING_OPTIONS = [
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

FILES_OPTIONS = [
    FilesOptions(INPUT, OUTPUT, dry_run=DEFAULTS.dry_run, workers=DEFAULTS.workers),
    FilesOptions(
        INPUT_UPPERCASE, OUTPUT, dry_run=DEFAULTS.dry_run, workers=DEFAULTS.workers
    ),
]

GRID_OPTIONS = [
    GridOptions(
        horizontal_boxes=DEFAULTS.horizontal_boxes,
        vertical_boxes=DEFAULTS.vertical_boxes,
        margin=DEFAULTS.margin,
    )
]

INSERT_OPTIONS = [
    InsertOptions(
        y=DEFAULTS.y,
        x=DEFAULTS.x,
        horizontal_alignment=DEFAULTS.horizontal_alignment,
    )
]


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
def test_add_watermark_from_options(
    files_options, drawing_options, specific_options, fixture
):
    add_watermark_from_options(
        files_options=files_options,
        drawing_options=drawing_options,
        specific_options=specific_options,
        verbose=False,
    )
    assert_pdfs_are_close(OUTPUT, fixture)
