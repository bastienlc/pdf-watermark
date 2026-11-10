"""Tests for DrawingOptions validation."""

import pytest

from pdf_watermark.options import DrawingOptions


@pytest.mark.parametrize("opacity", [-1.0, -0.5, 1.5, 2.0])
def test_opacity_out_of_range_rejected(opacity):
    """Opacity outside [0, 1] must fail fast instead of crashing in reportlab."""
    with pytest.raises(ValueError, match="between 0 and 1"):
        DrawingOptions(watermark="hello", opacity=opacity)


@pytest.mark.parametrize("opacity", [0, 0.1, 0.5, 1])
def test_opacity_boundaries_accepted(opacity):
    assert DrawingOptions(watermark="hello", opacity=opacity).opacity == opacity
