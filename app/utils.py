from typing import Tuple
from reportlab.pdfgen import canvas
import numpy as np
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


def fit_image(image_width, image_height, max_image_width, max_image_height, scale):
    if image_width > max_image_width:
        change_ratio = max_image_width / image_width
        image_width = max_image_width
        image_height *= change_ratio
    if image_height > max_image_height:
        change_ratio = max_image_height / image_height
        image_height = max_image_height
        image_width *= change_ratio

    image_width *= scale
    image_height *= scale

    return image_width, image_height
