import os

import pytest

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import DrawingOptions, FilesOptions, InsertOptions
from pdf_watermark.watermark import DEFAULTS
from tests.utils import assert_pdfs_are_close

OUTPUT = "output.pdf"
INPUT = "tests/fixtures/input.pdf"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    os.remove(OUTPUT)


def test_DarkGardenMK():
    add_watermark_from_options(
        files_options=FilesOptions(
            INPUT, OUTPUT, dry_run=DEFAULTS.dry_run, workers=DEFAULTS.workers
        ),
        drawing_options=DrawingOptions(
            watermark="watermark",
            opacity=DEFAULTS.opacity,
            angle=DEFAULTS.angle,
            text_color=DEFAULTS.text_color,
            text_font="DarkGardenMK",
            text_size=DEFAULTS.text_size,
            unselectable=DEFAULTS.unselectable,
            image_scale=DEFAULTS.image_scale,
            save_as_image=DEFAULTS.save_as_image,
            dpi=DEFAULTS.dpi,
        ),
        specific_options=InsertOptions(
            y=DEFAULTS.y,
            x=DEFAULTS.x,
            horizontal_alignment=DEFAULTS.horizontal_alignment,
        ),
        verbose=False,
    )
    assert_pdfs_are_close(OUTPUT, "tests/fixtures/DarkGardenMK.pdf")


def test_STSong_Light():
    add_watermark_from_options(
        files_options=FilesOptions(
            INPUT, OUTPUT, dry_run=DEFAULTS.dry_run, workers=DEFAULTS.workers
        ),
        drawing_options=DrawingOptions(
            watermark="你好，世界！",
            opacity=DEFAULTS.opacity,
            angle=DEFAULTS.angle,
            text_color=DEFAULTS.text_color,
            text_font="STSong-Light",
            text_size=DEFAULTS.text_size,
            unselectable=DEFAULTS.unselectable,
            image_scale=DEFAULTS.image_scale,
            save_as_image=DEFAULTS.save_as_image,
            dpi=DEFAULTS.dpi,
        ),
        specific_options=InsertOptions(
            y=DEFAULTS.y,
            x=DEFAULTS.x,
            horizontal_alignment=DEFAULTS.horizontal_alignment,
        ),
        verbose=False,
    )
    assert_pdfs_are_close(OUTPUT, "tests/fixtures/STSong-Light.pdf")


def test_MSung_Light():
    add_watermark_from_options(
        files_options=FilesOptions(
            INPUT, OUTPUT, dry_run=DEFAULTS.dry_run, workers=DEFAULTS.workers
        ),
        drawing_options=DrawingOptions(
            watermark="哈囉，世界！",
            opacity=DEFAULTS.opacity,
            angle=DEFAULTS.angle,
            text_color=DEFAULTS.text_color,
            text_font="MSung-Light",
            text_size=DEFAULTS.text_size,
            unselectable=DEFAULTS.unselectable,
            image_scale=DEFAULTS.image_scale,
            save_as_image=DEFAULTS.save_as_image,
            dpi=DEFAULTS.dpi,
        ),
        specific_options=InsertOptions(
            y=DEFAULTS.y,
            x=DEFAULTS.x,
            horizontal_alignment=DEFAULTS.horizontal_alignment,
        ),
        verbose=False,
    )
    assert_pdfs_are_close(OUTPUT, "tests/fixtures/MSung-Light.pdf")


def test_HYGothic_Medium():
    add_watermark_from_options(
        files_options=FilesOptions(
            INPUT, OUTPUT, dry_run=DEFAULTS.dry_run, workers=DEFAULTS.workers
        ),
        drawing_options=DrawingOptions(
            watermark="안녕하세요, 세상!",
            opacity=DEFAULTS.opacity,
            angle=DEFAULTS.angle,
            text_color=DEFAULTS.text_color,
            text_font="HYGothic-Medium",
            text_size=DEFAULTS.text_size,
            unselectable=DEFAULTS.unselectable,
            image_scale=DEFAULTS.image_scale,
            save_as_image=DEFAULTS.save_as_image,
            dpi=DEFAULTS.dpi,
        ),
        specific_options=InsertOptions(
            y=DEFAULTS.y,
            x=DEFAULTS.x,
            horizontal_alignment=DEFAULTS.horizontal_alignment,
        ),
        verbose=False,
    )
    assert_pdfs_are_close(OUTPUT, "tests/fixtures/HYGothic-Medium.pdf")


def test_HeiseiMin_W3():
    add_watermark_from_options(
        files_options=FilesOptions(
            INPUT, OUTPUT, dry_run=DEFAULTS.dry_run, workers=DEFAULTS.workers
        ),
        drawing_options=DrawingOptions(
            watermark="こんにちは、世界！",
            opacity=DEFAULTS.opacity,
            angle=DEFAULTS.angle,
            text_color=DEFAULTS.text_color,
            text_font="HeiseiMin-W3",
            text_size=DEFAULTS.text_size,
            unselectable=DEFAULTS.unselectable,
            image_scale=DEFAULTS.image_scale,
            save_as_image=DEFAULTS.save_as_image,
            dpi=DEFAULTS.dpi,
        ),
        specific_options=InsertOptions(
            y=DEFAULTS.y,
            x=DEFAULTS.x,
            horizontal_alignment=DEFAULTS.horizontal_alignment,
        ),
        verbose=False,
    )
    assert_pdfs_are_close(OUTPUT, "tests/fixtures/HeiseiMin-W3.pdf")


def test_TestFont():
    add_watermark_from_options(
        files_options=FilesOptions(
            INPUT, OUTPUT, dry_run=DEFAULTS.dry_run, workers=DEFAULTS.workers
        ),
        drawing_options=DrawingOptions(
            watermark="watermark",
            opacity=DEFAULTS.opacity,
            angle=DEFAULTS.angle,
            text_color=DEFAULTS.text_color,
            text_font="TestFont",
            text_size=DEFAULTS.text_size,
            unselectable=DEFAULTS.unselectable,
            image_scale=DEFAULTS.image_scale,
            save_as_image=DEFAULTS.save_as_image,
            dpi=DEFAULTS.dpi,
            custom_fonts_folder="tests/fonts",
        ),
        specific_options=InsertOptions(
            y=DEFAULTS.y,
            x=DEFAULTS.x,
            horizontal_alignment=DEFAULTS.horizontal_alignment,
        ),
        verbose=False,
    )
    assert_pdfs_are_close(OUTPUT, "tests/fixtures/TestFont.pdf")
