from typing import Union
from reportlab.lib.colors import HexColor
import os


class DrawingOptions:
    def __init__(
        self,
        text: str,
        color: str = "#000000",
        opacity=0.1,
        angle: float = 45,
        font: str = "Helvetica",
        size: int = 12,
        horizontal_boxes: int = 3,
        vertical_boxes: int = 6,
        margin: bool = False,
    ) -> None:
        self.text = text
        self.color = HexColor(color)
        self.opacity = opacity
        self.angle = angle
        self.font = font
        self.size = size
        self.horizontal_boxes = horizontal_boxes
        self.vertical_boxes = vertical_boxes
        self.margin = margin


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
        elif not os.path.isfile(input) or not input.endswith(".pdf"):
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
        text: str,
        color: str = "#000000",
        opacity=0.1,
        angle: float = 45,
        font: str = "Helvetica",
        size: int = 12,
        horizontal_boxes: int = 3,
        vertical_boxes: int = 6,
        margin: bool = False,
        save_to: Union[None, str] = None,
    ) -> None:
        self.files_options = FilesOptions(file, save_to)
        self.drawing_options = DrawingOptions(
            text=text,
            color=color,
            opacity=opacity,
            angle=angle,
            font=font,
            size=size,
            horizontal_boxes=horizontal_boxes,
            vertical_boxes=vertical_boxes,
            margin=margin,
        )
