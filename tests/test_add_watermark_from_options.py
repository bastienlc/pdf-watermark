"""
Test the outputs of the CLI with a bunch of different options on simple features. These tests are far from perfect.
"""

import os

import numpy as np
import pytest
from pdf2image import convert_from_path

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import (
    DrawingOptions,
    FilesOptions,
    GridOptions,
    InsertOptions,
)
from pdf_watermark.watermark import DEFAULTS

INPUT = "tests/fixtures/input.pdf"
OUTPUT = "output.pdf"
FIXTURES = ["tests/fixtures/0.pdf", "tests/fixtures/1.pdf"]


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
    )
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


def assert_pdfs_are_close(path_1: str, path_2: str, epsilon: float = 1e-10):
    """This function checks that two PDFs are close enough. We chose to convert the PDFs to images and then compare their L1 norms, because other techniques (hashing for instance) might break easily."""
    images_1 = convert_from_path(path_1)
    images_2 = convert_from_path(path_2)

    for im1, im2 in zip(images_1, images_2):
        assert np.sum(np.abs(np.array(im1) - np.array(im2))) < epsilon


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
