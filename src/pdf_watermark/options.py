import os
from enum import Enum
from typing import List, Union

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader


class DrawingOptions:
    def __init__(
        self,
        watermark: str,
        opacity: float,
        angle: float,
        text_color: str,
        text_font: str,
        text_size: int,
        unselectable: bool,
        image_scale: float,
        save_as_image: bool,
        dpi: int,
    ) -> None:
        self.image = None
        self.text = None

        potential_image_path = os.path.join(os.getcwd(), watermark)
        if watermark.endswith(
            (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG")
        ) and os.path.isfile(potential_image_path):
            self.image = ImageReader(watermark)
        else:
            self.text = watermark

        self.opacity = opacity
        self.angle = angle
        self.text_color = HexColor(text_color)
        self.text_font = text_font
        self.text_size = text_size
        self.unselectable = unselectable
        self.image_scale = image_scale
        self.save_as_image = save_as_image
        self.dpi = dpi


class FilesOptions:
    def __init__(
        self,
        input: str,
        output: Union[None, str],
        dry_run: bool,
        workers: int,
    ) -> None:
        self.dry_run = dry_run
        self.workers = workers
        input = os.path.join(os.getcwd(), input)

        if not os.path.exists(input):
            raise ValueError("Input file or directory does not exist.")
        elif os.path.isdir(input):
            if output is not None and output.endswith((".pdf", ".PDF")):
                raise ValueError(
                    "Output must be a directory when input is a directory."
                )
        elif os.path.isfile(input) and input.endswith((".pdf", ".PDF")):
            if output is not None and not output.endswith((".pdf", ".PDF")):
                raise ValueError("Output must be a pdf file when input is a pdf file.")
        else:
            raise ValueError("Input must be a pdf file or a directory.")

        if output is None:
            output = input
        else:
            output = os.path.join(os.getcwd(), output)

        if os.path.isfile(input):
            self.input_files: List[str] = [input]
            if output is None:
                self.output_files: List[str] = [input]
            else:
                self.output_files = [output]
        else:
            self.input_files = []
            self.output_files = []
            self.add_directory_to_files(input, output)

        if len(self.input_files) != len(set(self.input_files)):
            raise ValueError("Input files must be unique.")

        if len(self.output_files) != len(set(self.output_files)):
            raise ValueError("Output files must be unique.")

    def add_directory_to_files(
        self, input_directory: str, output_directory: str
    ) -> None:
        if not os.path.isdir(input_directory):
            raise ValueError("Directory argument must be a directory.")

        for file in os.listdir(input_directory):
            input_path = os.path.join(input_directory, file)
            output_path = os.path.join(output_directory, file)

            if os.path.isdir(input_path):
                self.add_directory_to_files(input_path, output_path)

            elif os.path.isfile(input_path) and input_path.endswith((".pdf", ".PDF")):
                self.input_files.append(input_path)
                self.output_files.append(output_path)

                if not os.path.exists(output_directory):
                    os.makedirs(output_directory)

    def __iter__(self):
        return iter(zip(self.input_files, self.output_files))

    def __next__(self):
        return next(zip(self.input_files, self.output_files))


class GridOptions:
    def __init__(
        self,
        horizontal_boxes: int,
        vertical_boxes: int,
        margin: bool,
    ) -> None:
        self.horizontal_boxes = horizontal_boxes
        self.vertical_boxes = vertical_boxes
        self.margin = margin


class Alignments(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class InsertOptions:
    def __init__(
        self,
        y: float,
        x: float,
        horizontal_alignment: List[Alignments],
    ) -> None:
        if not Alignments.has_value(horizontal_alignment):
            raise Exception(
                "Invalid argument. Horizontal alignment must be either left, right or center."
            )
        self.y = y
        self.x = x
        self.horizontal_alignment = horizontal_alignment
