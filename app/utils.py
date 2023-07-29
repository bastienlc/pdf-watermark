from typing import Tuple, Union
from reportlab.pdfgen import canvas
from math import cos, sin, pi
import numpy as np
from app.objects import (
    Alignments,
    DrawingOptions,
    GenericInputs,
    GridInputs,
    InsertInputs,
)
import pypdf
from tempfile import NamedTemporaryFile
from reportlab.lib.utils import ImageReader


def draw_centered_image(
    canvas: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    image: ImageReader,
):
    bottom_left_x = x - width / 2
    bottom_left_y = y - height / 2
    canvas.drawImage(
        image,
        bottom_left_x,
        bottom_left_y,
        width=width,
        height=height,
        mask="auto",
    )


def change_base(x: float, y: float, rotation_matrix: np.ndarray) -> Tuple[float, float]:
    # Since we rotated the original coordinates system, use the inverse of the rotation matrix
    # (which is the transposed matrix) to get the coordinates we have to draw at
    new_coordinates = np.transpose(rotation_matrix) @ np.array([[x], [y]])
    return new_coordinates[0, 0], new_coordinates[1, 0]


def draw_watermark(
    watermark: canvas.Canvas,
    x: float,
    y: float,
    rotation_matrix: np.ndarray,
    drawing_options: DrawingOptions,
    max_image_width: float,
    max_image_height: float,
):
    x_prime, y_prime = change_base(x, y, rotation_matrix)

    if drawing_options.text is not None:
        watermark.drawCentredString(
            x_prime,
            y_prime,
            drawing_options.text,
        )

    if drawing_options.image is not None:
        # if the image is too big, scale it down to fit in the box
        image_width, image_height = drawing_options.image.getSize()
        if image_width > max_image_width:
            change_ratio = max_image_width / image_width
            image_width = max_image_width
            image_height *= change_ratio
        if image_height > max_image_height:
            change_ratio = max_image_height / image_height
            image_height = max_image_height
            image_width *= change_ratio

        image_width *= drawing_options.image_scale
        image_height *= drawing_options.image_scale

        draw_centered_image(
            watermark,
            x_prime,
            y_prime,
            image_width,
            image_height,
            drawing_options.image,
        )


def draw_insert_watermark(
    watermark: canvas.Canvas,
    drawing_options: DrawingOptions,
    specific_inputs: InsertInputs,
    width: float,
    height: float,
    rotation_matrix: np.ndarray,
):
    string_width = watermark.stringWidth(
        drawing_options.text, drawing_options.text_font, drawing_options.text_size
    )

    if specific_inputs.horizontal_alignment == Alignments.LEFT.value:
        offset = -string_width / 2

    elif specific_inputs.horizontal_alignment == Alignments.RIGHT.value:
        offset = string_width / 2

    elif specific_inputs.horizontal_alignment == Alignments.CENTER.value:
        offset = 0

    else:
        raise ValueError(
            f"Invalid alignment value: '{specific_inputs.horizontal_alignment}'."
        )

    draw_watermark(
        watermark,
        specific_inputs.x * width + offset,
        specific_inputs.y * height,
        rotation_matrix,
        drawing_options,
        width,
        height,
    )


def draw_grid_watermark(
    watermark: canvas.Canvas,
    drawing_options: DrawingOptions,
    specific_inputs: GridInputs,
    width: float,
    height: float,
    rotation_matrix: np.ndarray,
):
    horizontal_box_spacing = width / specific_inputs.horizontal_boxes
    vertical_box_spacing = height / specific_inputs.vertical_boxes

    if specific_inputs.margin:
        start_index = 1
    else:
        start_index = 0

    for x_index in range(start_index, specific_inputs.horizontal_boxes + 1):
        for y_index in range(start_index, specific_inputs.vertical_boxes + 1):
            # Coordinates to draw at in original coordinates system
            x_base = x_index * horizontal_box_spacing
            y_base = y_index * vertical_box_spacing

            if specific_inputs.margin:
                x_base -= horizontal_box_spacing / 2
                y_base -= vertical_box_spacing / 2

            draw_watermark(
                watermark,
                x_base,
                y_base,
                rotation_matrix,
                drawing_options,
                horizontal_box_spacing,
                vertical_box_spacing,
            )


def create_watermark_pdf(
    file_name: str,
    width: float,
    height: float,
    drawing_options: DrawingOptions,
    specific_inputs: Union[GridInputs, InsertInputs],
):
    watermark = canvas.Canvas(file_name, pagesize=(width, height))

    rotation_angle_rad = drawing_options.angle * pi / 180
    rotation_matrix = np.array(
        [
            [cos(rotation_angle_rad), -sin(rotation_angle_rad)],
            [sin(rotation_angle_rad), cos(rotation_angle_rad)],
        ]
    )

    watermark.setFillColor(drawing_options.text_color, alpha=drawing_options.opacity)
    watermark.setFont(drawing_options.text_font, drawing_options.text_size)
    watermark.rotate(drawing_options.angle)

    if isinstance(specific_inputs, InsertInputs):
        draw_insert_watermark(
            watermark, drawing_options, specific_inputs, width, height, rotation_matrix
        )

    elif isinstance(specific_inputs, GridInputs):
        draw_grid_watermark(
            watermark, drawing_options, specific_inputs, width, height, rotation_matrix
        )
    else:
        raise NotImplementedError("Unknown watermark type.")

    watermark.save()


def add_watermark_to_pdf(
    input: str,
    output: str,
    drawing_options: DrawingOptions,
    specific_inputs: Union[GridInputs, InsertInputs],
):
    pdf_to_transform = pypdf.PdfReader(input)
    pdf_box = pdf_to_transform.pages[0].mediabox
    page_width = pdf_box.width
    page_height = pdf_box.height

    with NamedTemporaryFile() as temporary_file:
        # The watermark is stored in a temporary pdf file
        create_watermark_pdf(
            temporary_file.name,
            page_width,
            page_height,
            drawing_options,
            specific_inputs,
        )

        watermark_pdf = pypdf.PdfReader(temporary_file.name)
        pdf_writer = pypdf.PdfWriter()

        for page in pdf_to_transform.pages:
            page.merge_page(watermark_pdf.pages[0])
            pdf_writer.add_page(page)

    with open(output, "wb") as f:
        pdf_writer.write(f)


def add_watermark_from_inputs(
    generic_inputs: GenericInputs, specific_inputs: Union[GridInputs, InsertInputs]
):
    for input_file, output_file in generic_inputs.files_options:
        add_watermark_to_pdf(
            input_file, output_file, generic_inputs.drawing_options, specific_inputs
        )
