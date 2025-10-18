import pytest
from reportlab.pdfbase import pdfmetrics

from pdf_watermark.font_utils import (
    STANDARD_CID_FONTS,
    STANDARD_FONTS,
    register_custom_font,
)


@pytest.mark.parametrize("font_name", STANDARD_CID_FONTS + STANDARD_FONTS)
def test_register_standard_font(font_name: str):
    register_custom_font(font_name)
    assert pdfmetrics.getFont(font_name) is not None


def test_register_failure():
    if "TestFont" in pdfmetrics.getRegisteredFontNames():
        # TODO is there a way to unregister ? Or run test in separate environment ?
        pytest.skip("TestFont is already registered globally, cannot test.")

    with pytest.raises(ValueError):
        register_custom_font("TestFont")

    with pytest.raises(KeyError):
        pdfmetrics.getFont("TestFont")


def test_register_custom_font():
    register_custom_font("TestFont", custom_fonts_folder="tests/fonts/")
    assert pdfmetrics.getFont("TestFont") is not None
