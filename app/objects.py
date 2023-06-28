from typing import Union
from reportlab.lib.colors import HexColor
import os
from reportlab.lib.utils import ImageReader


class DrawingOptions:
    def __init__(
        self,
        watermark: str,
        opacity,
        angle: float,
        horizontal_boxes: int,
        vertical_boxes: int,
        margin: bool,
        text_color: str,
        text_font: str,
        text_size: int,
        image_scale: float,
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
        self.horizontal_boxes = horizontal_boxes
        self.vertical_boxes = vertical_boxes
        self.margin = margin
        self.text_color = HexColor(text_color)
        self.text_font = text_font
        self.text_size = text_size
        self.image_scale = image_scale


class FilesOptions:
    def __init__(
        self,
        input: str,
        output: Union[None, str] = None,
    ) -> None:
        input = os.path.join(os.getcwd(), input)

        if not os.path.exists(input):
            raise ValueError("Input file or directory does not exist.")
        elif os.path.isdir(input):
            if output is not None and output.endswith(".pdf"):
                raise ValueError(
                    "Output must be a directory when input is a directory."
                )
        elif os.path.isfile(input) and input.endswith(".pdf"):
            if output is not None and not output.endswith(".pdf"):
                raise ValueError("Output must be a pdf file when input is a pdf file.")
        else:
            raise ValueError("Input must be a pdf file or a directory.")

        if output is None:
            output = input
        else:
            output = os.path.join(os.getcwd(), output)

        if os.path.isfile(input):
            self.input_files = [input]
            if output is None:
                self.output_files = [input]
            else:
                self.output_files = [output]
        else:
            self.input_files = []
            self.output_files = []
            self.add_directory_to_files(input, output)

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

            elif os.path.isfile(input_path) and input_path.endswith(".pdf"):
                self.input_files.append(input_path)
                self.output_files.append(output_path)

                if not os.path.exists(output_directory):
                    os.makedirs(output_directory)

    def __iter__(self):
        return iter(zip(self.input_files, self.output_files))

    def __next__(self):
        return next(zip(self.input_files, self.output_files))


class UserInputs:
    def __init__(
        self,
        file: str,
        watermark: str,
        save: Union[None, str] = None,
        opacity=0.1,
        angle: float = 45,
        horizontal_boxes: int = 3,
        vertical_boxes: int = 6,
        margin: bool = False,
        text_color: str = "#000000",
        text_font: str = "Helvetica",
        text_size: int = 12,
        image_scale: float = 1,
    ) -> None:
        self.files_options = FilesOptions(file, save)
        self.drawing_options = DrawingOptions(
            watermark=watermark,
            opacity=opacity,
            angle=angle,
            horizontal_boxes=horizontal_boxes,
            vertical_boxes=vertical_boxes,
            margin=margin,
            text_color=text_color,
            text_font=text_font,
            text_size=text_size,
            image_scale=image_scale,
        )
