"""
Font utilities for pdf-watermark.
Handles custom font registration including TTF and CID fonts.
"""

import os
from typing import Optional

import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont

# Standard fonts that come with reportlab and don't need registration
STANDARD_FONTS = [
    "Helvetica",
    "Helvetica-Bold",
    "Helvetica-BoldOblique",
    "Helvetica-Oblique",
    "Times-Roman",
    "Times-Bold",
    "Times-BoldItalic",
    "Times-Italic",
    "Courier",
    "Courier-Bold",
    "Courier-BoldOblique",
    "Courier-Oblique",
    "Symbol",
    "ZapfDingbats",
    # Test font
    "DarkGardenMK",
]

# Standard CID fonts that reportlab can use but still need registration
STANDARD_CID_FONTS = [
    "STSong-Light",
    "MSung-Light",
    "HYGothic-Medium",
    "HeiseiMin-W3",
    "HeiseiKakuGo-W5",
    # Fonts not working though reportlab lists them
    # "MHei-Medium",
    # "HYSMyeongJoStd-Medium",
]


def register_custom_font(
    font_name: str, custom_fonts_folder: Optional[str] = None
) -> None:
    """
    Register a custom font for use in PDF generation.

    1. If font_name is a standard font, do nothing.
    2. If font_name is a standard CID font, register it as CID font.
    3. Try to register the font as a TTF font (searching default paths and custom folder).

    Args:
        font_name: The name of the font to register
        custom_fonts_folder: Optional folder path to search for custom fonts first

    Raises:
        ValueError: If the font cannot be found or registered.
    """
    setup_custom_fonts_path(custom_fonts_folder)

    if font_name in STANDARD_FONTS:
        return

    if font_name in STANDARD_CID_FONTS:
        try:
            pdfmetrics.registerFont(UnicodeCIDFont(font_name))
            return
        except Exception as e:
            raise ValueError(f"Failed to register standard CID font '{font_name}': {e}")

    register_ttf_font(font_name)


def register_ttf_font(font_name: str) -> None:
    """
    Try to register a font as a TTF font.

    Args:
        font_name: The name of the font to register
        custom_fonts_folder: Optional folder path to search for font files first
    """
    try:
        # Check if font is already registered
        existing_fonts = pdfmetrics.getRegisteredFontNames()
        if font_name in existing_fonts:
            return
    except Exception:
        pass

    # Try different common extensions with reportlab's search
    possible_extensions = [".ttf", ".TTF", ".otf", ".OTF"]
    for ext in possible_extensions:
        try:
            ttf_font = TTFont(font_name, font_name + ext)
            pdfmetrics.registerFont(ttf_font)
            return
        except Exception as e:
            if "Can't open file" not in str(e):
                print(
                    f"Warning: Could not register font '{font_name + ext}' due to error: {e}"
                )
            continue

    # If font_name could not be registered, look for similar names in the font folders
    similar_fonts = set()
    for folder in reportlab.rl_config.TTFSearchPath:
        for _, _, files in os.walk(folder):
            for file in files:
                if font_name.lower() in file.lower():
                    similar_fonts.add(file.rsplit(".", 1)[0])

    raise ValueError(
        f"Font '{font_name}' could not be registered. Maybe you meant one of {list(similar_fonts)} ?"
    )


def setup_custom_fonts_path(custom_fonts_folder: Optional[str] = None) -> None:
    """
    Set up the custom fonts search path for reportlab.

    Args:
        custom_fonts_folder: Optional folder path to add to font search paths
    """
    if custom_fonts_folder is None:
        return

    if not os.path.exists(custom_fonts_folder):
        raise ValueError(f"Custom fonts folder does not exist: {custom_fonts_folder}")

    # Add the custom fonts folder to reportlab's TTF search path
    if hasattr(reportlab.rl_config, "TTFSearchPath"):
        if custom_fonts_folder not in reportlab.rl_config.TTFSearchPath:
            reportlab.rl_config.TTFSearchPath = reportlab.rl_config.TTFSearchPath + [
                custom_fonts_folder
            ]
    else:
        reportlab.rl_config.TTFSearchPath = [custom_fonts_folder]
