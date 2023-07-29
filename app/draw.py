from typing import Union
from reportlab.pdfgen import canvas
from math import cos, sin, pi
import numpy as np
from app.options import (
    Alignments,
    DrawingOptions,
    GridOptions,
    InsertOptions,
)

from app.utils import draw_centered_image, change_base


def draw_one_watermark(
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
    specific_options: InsertOptions,
    width: float,
    height: float,
    rotation_matrix: np.ndarray,
):
    string_width = watermark.stringWidth(
        drawing_options.text, drawing_options.text_font, drawing_options.text_size
    )

    if specific_options.horizontal_alignment == Alignments.LEFT.value:
        offset = -string_width / 2

    elif specific_options.horizontal_alignment == Alignments.RIGHT.value:
        offset = string_width / 2

    elif specific_options.horizontal_alignment == Alignments.CENTER.value:
        offset = 0

    else:
        raise ValueError(
            f"Invalid alignment value: '{specific_options.horizontal_alignment}'."
        )

    draw_one_watermark(
        watermark,
        specific_options.x * width + offset,
        specific_options.y * height,
        rotation_matrix,
        drawing_options,
        width,
        height,
    )


def draw_grid_watermark(
    watermark: canvas.Canvas,
    drawing_options: DrawingOptions,
    specific_options: GridOptions,
    width: float,
    height: float,
    rotation_matrix: np.ndarray,
):
    horizontal_box_spacing = width / specific_options.horizontal_boxes
    vertical_box_spacing = height / specific_options.vertical_boxes

    if specific_options.margin:
        start_index = 1
    else:
        start_index = 0

    for x_index in range(start_index, specific_options.horizontal_boxes + 1):
        for y_index in range(start_index, specific_options.vertical_boxes + 1):
            # Coordinates to draw at in original coordinates system
            x_base = x_index * horizontal_box_spacing
            y_base = y_index * vertical_box_spacing

            if specific_options.margin:
                x_base -= horizontal_box_spacing / 2
                y_base -= vertical_box_spacing / 2

            draw_one_watermark(
                watermark,
                x_base,
                y_base,
                rotation_matrix,
                drawing_options,
                horizontal_box_spacing,
                vertical_box_spacing,
            )


def draw_watermarks(
    file_name: str,
    width: float,
    height: float,
    drawing_options: DrawingOptions,
    specific_options: Union[GridOptions, InsertOptions],
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

    if isinstance(specific_options, InsertOptions):
        draw_insert_watermark(
            watermark, drawing_options, specific_options, width, height, rotation_matrix
        )

    elif isinstance(specific_options, GridOptions):
        draw_grid_watermark(
            watermark, drawing_options, specific_options, width, height, rotation_matrix
        )
    else:
        raise NotImplementedError("Unknown watermark type.")

    watermark.save()
