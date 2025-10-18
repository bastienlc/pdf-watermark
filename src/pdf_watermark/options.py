import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

from pdf_watermark.font_utils import register_custom_font


def add_directory_to_files(
    input_directory: str, output_directory: str
) -> tuple[List[str], List[str]]:
    """
    Recursively scan directory for PDF files and return lists of input and output file paths.

    Args:
        input_directory: Directory to scan for PDF files
        output_directory: Corresponding output directory

    Returns:
        Tuple of (input_files, output_files) lists
    """
    if not os.path.isdir(input_directory):
        raise ValueError("Directory argument must be a directory.")

    input_files = []
    output_files = []

    for file in os.listdir(input_directory):
        input_path = os.path.join(input_directory, file)
        output_path = os.path.join(output_directory, file)

        if os.path.isdir(input_path):
            sub_input_files, sub_output_files = add_directory_to_files(
                input_path, output_path
            )
            input_files.extend(sub_input_files)
            output_files.extend(sub_output_files)

        elif os.path.isfile(input_path) and input_path.endswith((".pdf", ".PDF")):
            input_files.append(input_path)
            output_files.append(output_path)

            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

    return input_files, output_files


@dataclass
class DrawingOptions:
    watermark: str
    opacity: float
    angle: float
    text_color: str
    text_font: str
    text_size: int
    unselectable: bool
    image_scale: float
    save_as_image: bool
    dpi: int
    custom_fonts_folder: Optional[str] = None

    def __post_init__(self):
        self.image = None
        self.text = None

        potential_image_path = os.path.join(os.getcwd(), self.watermark)
        if self.watermark.endswith(
            (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG")
        ) and os.path.isfile(potential_image_path):
            self.image = ImageReader(self.watermark)
        else:
            self.text = self.watermark

        self.text_color = HexColor(self.text_color)

        # Register the font if needed
        register_custom_font(self.text_font, self.custom_fonts_folder)


@dataclass
class FilesOptions:
    input: str
    output: Union[None, str]
    dry_run: bool
    workers: int

    def __post_init__(self):
        input = os.path.join(os.getcwd(), self.input)

        if not os.path.exists(input):
            raise ValueError("Input file or directory does not exist.")
        elif os.path.isdir(input):
            if self.output is not None and self.output.endswith((".pdf", ".PDF")):
                raise ValueError(
                    "Output must be a directory when input is a directory."
                )
        elif os.path.isfile(input) and input.endswith((".pdf", ".PDF")):
            if self.output is not None and not self.output.endswith((".pdf", ".PDF")):
                raise ValueError("Output must be a pdf file when input is a pdf file.")
        else:
            raise ValueError("Input must be a pdf file or a directory.")

        if self.output is None:
            output = input
        else:
            output = os.path.join(os.getcwd(), self.output)

        if os.path.isfile(input):
            self.input_files: List[str] = [input]
            if self.output is None:
                self.output_files: List[str] = [input]
            else:
                self.output_files = [output]
        else:
            self.input_files, self.output_files = add_directory_to_files(input, output)

        if len(self.input_files) != len(set(self.input_files)):
            raise ValueError("Input files must be unique.")

        if len(self.output_files) != len(set(self.output_files)):
            raise ValueError("Output files must be unique.")

    def __iter__(self):
        return iter(zip(self.input_files, self.output_files))

    def __next__(self):
        return next(zip(self.input_files, self.output_files))


@dataclass
class GridOptions:
    horizontal_boxes: int
    vertical_boxes: int
    margin: bool


class Alignments(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass
class InsertOptions:
    y: float
    x: float
    horizontal_alignment: str

    def __post_init__(self):
        if not Alignments.has_value(self.horizontal_alignment):
            raise Exception(
                "Invalid argument. Horizontal alignment must be either left, right or center."
            )
