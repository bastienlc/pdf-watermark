import os
from dataclasses import dataclass
from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import IndirectObject
from pypdf.types import OutlineType

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import DrawingOptions, FilesOptions, InsertOptions

PDF_W_OUTLINES = "tests/fixtures/temp/pdf_w_outlines.pdf"
PDF_W_OUTLINES_WATERMARKED = "tests/fixtures/temp/pdf_w_outlines_watermarked.pdf"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    # TODO: remove temporary output
    if os.path.exists(PDF_W_OUTLINES):
        os.remove(PDF_W_OUTLINES)
    if os.path.exists(PDF_W_OUTLINES_WATERMARKED):
        os.remove(PDF_W_OUTLINES_WATERMARKED)


# Core Type
@dataclass(frozen=True)
class OutlineItem:
    """Custom dataclass to store the data for a single Outline's details"""

    title: str
    level: int
    page_number: int | None


def create_pdf_with_outlines(
    outline_spec: list[tuple[str, int, int | None]] | None, page_count: int
) -> str:
    """Creates a pdf with outlines and returns the path

    Args:
        outline_spec (list[tuple[str, int, int  |  None]]): A list tuples where each tuple consists of a title(str), level(int), page_number(int)
        page_count (int): Number of page to be in the pdf

    Returns:
        str: Path to the generated pdf file
    """
    writer = PdfWriter()

    for _ in range(page_count):
        writer.add_blank_page(612, 792)  # Letter size

    if outline_spec:
        last_seen_at_level: dict[int, IndirectObject] = {}
        for outline in outline_spec:
            level = outline[1]
            if level == 0:
                top_level_outline = writer.add_outline_item(
                    title=outline[0], page_number=outline[2]
                )
                last_seen_at_level[level] = top_level_outline
            else:
                nested_outline = writer.add_outline_item(
                    title=outline[0],
                    page_number=outline[2],
                    parent=last_seen_at_level[
                        level - 1
                    ],  # Edge Case: if level jumps from 0 to 2 skipping 1, it will through a KeyError
                )

                last_seen_at_level[level] = nested_outline

    Path(PDF_W_OUTLINES).parent.mkdir(parents=True, exist_ok=True)
    writer.write(PDF_W_OUTLINES)
    return PDF_W_OUTLINES


def extract_outline_tree(path: str) -> list[OutlineItem]:
    """Extracts an outline tree from a given pdf file path and returns a list of OutlineItem dataclass

    Args:
        path (str): Path to the pdf file

    Returns:
        list[OutlineItem]: A list of OutlineItem dataclass
    """
    reader = PdfReader(path)
    items = []
    items = walk_outline(reader.outline, reader, 0, items)
    return items


def walk_outline(node: OutlineType, reader: PdfReader, level, items: list):
    """Walks through an OutlineType and returns a list of OutlineItem dataclass

    Args:
        node (OutlineType): One instance of OutlineType
        reader (PdfReader): The PdfReader instance
        level (_type_): Current level in the outline hierarchy
        items (list): List of items containing OutlineItem dataclass

    Returns:
        list: A list of OutlineItem dataclass
    """
    for item in node:
        if isinstance(item, list):
            walk_outline(item, reader, level + 1, items)
        else:
            page = reader.get_destination_page_number(item)
            items.append(
                OutlineItem(
                    title=item.title,
                    level=level,
                    page_number=(page + 1) if page is not None else None,
                )
            )

    return items


def assert_outline_equal(before: list[OutlineItem], after: list[OutlineItem]) -> None:
    for b, a in zip(before, after):
        assert b == a, f"Mismatch: {b} != {a}"
    assert len(before) == len(after)


@pytest.mark.parametrize(
    "outline_spec, page_count",
    [
        ([("Chapter 1", 0, 0), ("Chapter 2", 0, 1), ("Chapter 3", 0, 2)], 3),  # flat
        (
            [
                ("Chapter 1", 0, 1),
                ("Section 1.1", 1, 2),
                ("Section 1.2", 1, 3),
                ("Section 1.2.1", 2, 4),
                ("Section 1.2.2", 2, 5),
                ("Chapter 2", 0, 6),
            ],
            6,
        ),  # nested
        (None, 3),  # no outlines
    ],
    ids=["flat", "nested", "no_outlines"],
)
def test_outlines_preserved(outline_spec, page_count):
    input = create_pdf_with_outlines(outline_spec=outline_spec, page_count=page_count)

    add_watermark_from_options(
        files_options=FilesOptions(input, PDF_W_OUTLINES_WATERMARKED),
        drawing_options=DrawingOptions("Watermarked On a PDF that has Outlines"),
        specific_options=InsertOptions(),
    )

    input_outline_tree = extract_outline_tree(input)
    output_outline_tree = extract_outline_tree(PDF_W_OUTLINES_WATERMARKED)

    assert_outline_equal(before=input_outline_tree, after=output_outline_tree)
