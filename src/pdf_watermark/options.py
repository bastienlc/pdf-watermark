import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Annotated, List

from dataclass_click import argument, option
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
class FilesOptions:
    file: Annotated[Path, argument()]
    output: Annotated[
        Path | None,
        option(
            "-s",
            "--save",
            default=None,
            show_default=True,
            help="File or folder to save results to. By default, the input files are overwritten.",
        ),
    ] = None
    dry_run: Annotated[
        bool,
        option(
            "--dry-run",
            is_flag=True,
            default=False,
            show_default=True,
            help="Enumerate affected files without modifying them.",
        ),
    ] = False
    workers: Annotated[
        int,
        option(
            "--workers",
            default=1,
            show_default=True,
            help="Number of parallel workers to use. This can speed up processing of multiple files.",
        ),
    ] = 1
    verbose: Annotated[
        bool,
        option(
            "--verbose",
            default=True,
            show_default=True,
            help="Print information about the files being processed.",
        ),
    ] = True

    def __post_init__(self):
        if not os.path.exists(self.file):
            raise ValueError("Input file or directory does not exist.")
        elif os.path.isdir(self.file):
            if self.output is not None and str(self.output).endswith((".pdf", ".PDF")):
                raise ValueError(
                    "Output must be a directory when input is a directory."
                )
        elif os.path.isfile(self.file) and str(self.file).endswith((".pdf", ".PDF")):
            if self.output is not None and not str(self.output).endswith(
                (".pdf", ".PDF")
            ):
                raise ValueError("Output must be a pdf file when input is a pdf file.")
        else:
            raise ValueError("Input must be a pdf file or a directory.")

        if self.output is None:
            output = self.file
        else:
            output = self.output

        if os.path.isfile(self.file):
            self.input_files: List[str] = [self.file]
            if self.output is None:
                self.output_files: List[str] = [self.file]
            else:
                self.output_files = [output]
        else:
            self.input_files, self.output_files = add_directory_to_files(
                str(self.file), str(output)
            )

        if len(self.input_files) != len(set(self.input_files)):
            raise ValueError("Input files must be unique.")

        if len(self.output_files) != len(set(self.output_files)):
            raise ValueError("Output files must be unique.")

    def __iter__(self):
        return iter(zip(self.input_files, self.output_files))

    def __next__(self):
        return next(zip(self.input_files, self.output_files))


@dataclass
class DrawingOptions:
    watermark: Annotated[str, argument()]
    opacity: Annotated[
        float,
        option(
            "-o",
            "--opacity",
            default=0.1,
            show_default=True,
            help="Watermark opacity between 0 (invisible) and 1 (no transparency).",
        ),
    ] = 0.1
    angle: Annotated[
        float,
        option(
            "-a",
            "--angle",
            default=45,
            show_default=True,
            help="Watermark inclination in degrees.",
        ),
    ] = 45
    text_color: Annotated[
        str,
        option(
            "-tc",
            "--text-color",
            default="#000000",
            show_default=True,
            help="Text color in hexadecimal format, e.g. #000000.",
        ),
    ] = "#000000"
    text_font: Annotated[
        str,
        option(
            "-tf",
            "--text-font",
            default="Helvetica",
            show_default=True,
            help="Text font to use. Supported fonts are those supported by reportlab, or available on the system or in the custom fonts folder.",
        ),
    ] = "Helvetica"
    text_size: Annotated[
        int,
        option(
            "-ts", "--text-size", default=12, show_default=True, help="Text font size."
        ),
    ] = 12
    unselectable: Annotated[
        bool,
        option(
            "--unselectable",
            is_flag=True,
            default=False,
            show_default=True,
            help="Make the watermark text unselectable. This works by drawing the text as an image, and thus results in a larger file size.",
        ),
    ] = False
    image_scale: Annotated[
        float,
        option(
            "-is",
            "--image-scale",
            default=1,
            show_default=True,
            help="Scale factor for the image. Note that before this factor is applied, the image is already scaled down to fit in the boxes.",
        ),
    ] = 1
    save_as_image: Annotated[
        bool,
        option(
            "--save-as-image",
            is_flag=True,
            default=False,
            show_default=True,
            help="Convert each PDF page to an image. This makes removing the watermark more difficult but also increases the file size.",
        ),
    ] = False
    dpi: Annotated[
        int,
        option(
            "--dpi",
            default=300,
            show_default=True,
            help="DPI to use when saving the PDF as an image.",
        ),
    ] = 300
    custom_fonts_folder: Annotated[
        Path | None,
        option(
            "--custom-fonts-folder",
            default=None,
            show_default=True,
            help="Folder path containing custom font files (TTF, OTF, etc.) to search for non-standard fonts.",
        ),
    ] = None

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
class GridOptions:
    horizontal_boxes: Annotated[
        int,
        option(
            "-h",
            "--horizontal-boxes",
            default=3,
            show_default=True,
            help="Number of repetitions of the watermark along the horizontal direction.",
        ),
    ] = 3
    vertical_boxes: Annotated[
        int,
        option(
            "-v",
            "--vertical-boxes",
            default=6,
            show_default=True,
            help="Number of repetitions of the watermark along the vertical direction.",
        ),
    ] = 6
    margin: Annotated[
        bool,
        option(
            "-m",
            "--margin",
            is_flag=True,
            default=False,
            show_default=True,
            help="Wether to leave a margin around the page or not. When False (default), the watermark will be cut on the PDF edges.",
        ),
    ] = False


class Alignments(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass
class InsertOptions:
    y: Annotated[
        float,
        option(
            "-y",
            "--y",
            default=0.5,
            show_default=True,
            help="Position of the watermark with respect to the vertical direction. Must be between 0 and 1.",
        ),
    ] = 0.5
    x: Annotated[
        float,
        option(
            "-x",
            "--x",
            default=0.5,
            show_default=True,
            help="Position of the watermark with respect to the horizontal direction. Must be between 0 and 1.",
        ),
    ] = 0.5
    horizontal_alignment: Annotated[
        str,
        option(
            "-ha",
            "--horizontal-alignment",
            default="center",
            show_default=True,
            help="Alignment of the watermark with respect to the horizontal direction. Can be one of 'left', 'right' and 'center'.",
        ),
    ] = "center"

    def __post_init__(self):
        if not Alignments.has_value(self.horizontal_alignment):
            raise Exception(
                "Invalid argument. Horizontal alignment must be either left, right or center."
            )
