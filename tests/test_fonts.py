import os

import pytest

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import DrawingOptions, FilesOptions, InsertOptions
from tests.utils import assert_pdfs_are_close

OUTPUT = "output.pdf"
INPUT = "tests/fixtures/input.pdf"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    os.remove(OUTPUT)


# Define font test configurations
FONT_CONFIGS = [
    ("watermark", "DarkGardenMK", None),
    ("你好，世界！", "STSong-Light", None),
    ("哈囉，世界！", "MSung-Light", None),
    ("안녕하세요, 세상!", "HYGothic-Medium", None),
    ("こんにちは、世界！", "HeiseiMin-W3", None),
    ("watermark", "TestFont", "tests/fonts"),
]


@pytest.mark.parametrize(
    "watermark,text_font,custom_fonts_folder",
    FONT_CONFIGS,
    ids=[
        "DarkGardenMK",
        "STSong-Light",
        "MSung-Light",
        "HYGothic-Medium",
        "HeiseiMin-W3",
        "TestFont",
    ],
)
def test_fonts(watermark, text_font, custom_fonts_folder):
    expected_fixture = f"tests/fixtures/{text_font}.pdf"
    add_watermark_from_options(
        files_options=FilesOptions(INPUT, OUTPUT),
        drawing_options=DrawingOptions(
            watermark=watermark,
            text_font=text_font,
            custom_fonts_folder=custom_fonts_folder,
        ),
        specific_options=InsertOptions(),
    )
    assert_pdfs_are_close(OUTPUT, expected_fixture)
