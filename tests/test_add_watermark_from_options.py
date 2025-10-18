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
    DrawingOptions(watermark="watermark"),
    DrawingOptions(watermark=r"watermark\nwith\nline\nbreaks"),
]
FILES_OPTIONS = [
    FilesOptions(INPUT, OUTPUT),
    FilesOptions(INPUT_UPPERCASE, OUTPUT),
]
GRID_OPTIONS = [GridOptions()]
INSERT_OPTIONS = [InsertOptions()]


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
    )
    assert_pdfs_are_close(OUTPUT, fixture)
