from math import cos, pi, sin
from typing import Union

import numpy as np
from reportlab.pdfgen import canvas

from pdf_watermark.options import Alignments, DrawingOptions, GridOptions, InsertOptions
from pdf_watermark.utils import (
    change_base,
    draw_centered_image,
    draw_centered_string_with_line_breaks,
    fit_image,
)


def draw_one_watermark(
    watermark: canvas.Canvas,
    x: float,
    y: float,
    rotation_matrix: np.ndarray,
    drawing_options: DrawingOptions,
    image_width: float,
    image_height: float,
):
    x_prime, y_prime = change_base(x, y, rotation_matrix)

    if drawing_options.text is not None:
        draw_centered_string_with_line_breaks(
            watermark,
            x_prime,
            y_prime,
            drawing_options.text,
        )

    if drawing_options.image is not None:
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
    max_image_height = min(
        2 * specific_options.y * height, 2 * (2 * (1 - specific_options.y) * height)
    )
    image_width, image_height = 0, 0

    if drawing_options.text is not None:
        watermark_width = watermark.stringWidth(
            drawing_options.text, drawing_options.text_font, drawing_options.text_size
        )

    elif drawing_options.image is not None:
        if specific_options.horizontal_alignment == Alignments.LEFT.value:
            max_image_width = specific_options.x * width

        elif specific_options.horizontal_alignment == Alignments.RIGHT.value:
            max_image_width = (1 - specific_options.x) * width

        elif specific_options.horizontal_alignment == Alignments.CENTER.value:
            max_image_width = min(
                2 * (1 - specific_options.x) * width, 2 * specific_options.x * width
            )

        else:
            raise ValueError(
                f"Invalid alignment value: '{specific_options.horizontal_alignment}'."
            )

        # if the image is too big, scale it down to fit in the box
        image_width, image_height = drawing_options.image.getSize()
        image_width, image_height = fit_image(
            image_width,
            image_height,
            max_image_width,
            max_image_height,
            drawing_options.image_scale,
        )

        watermark_width = image_width

    else:
        raise ValueError("No watermark to draw.")

    if specific_options.horizontal_alignment == Alignments.LEFT.value:
        offset = -watermark_width / 2

    elif specific_options.horizontal_alignment == Alignments.RIGHT.value:
        offset = watermark_width / 2

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
        image_width,
        image_height,
    )


def draw_grid_watermark(
    watermark: canvas.Canvas,
    drawing_options: DrawingOptions,
    specific_options: GridOptions,
    width: float,
    height: float,
    rotation_matrix: np.ndarray,
):
    image_width, image_height = 0, 0

    horizontal_box_spacing = width / specific_options.horizontal_boxes
    vertical_box_spacing = height / specific_options.vertical_boxes

    if specific_options.margin:
        start_index = 1
    else:
        start_index = 0

    if drawing_options.image is not None:
        # if the image is too big, scale it down to fit in the box
        image_width, image_height = drawing_options.image.getSize()
        image_width, image_height = fit_image(
            image_width,
            image_height,
            horizontal_box_spacing,
            vertical_box_spacing,
            drawing_options.image_scale,
        )

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
                image_width,
                image_height,
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
