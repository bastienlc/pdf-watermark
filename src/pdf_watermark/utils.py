from io import BytesIO
from typing import List, Tuple

import numpy as np
import pypdf
from pdf2image import convert_from_path
from pdf2image.exceptions import PopplerNotInstalledError
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


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


def draw_centered_string_with_line_breaks(
    watermark: canvas.Canvas,
    x: float,
    y: float,
    text: str,
):
    text_lines = text.split(r"\n")
    line_height = (
        watermark._leading
    )  # line height is set when setting the font of the canvas
    y += (len(text_lines) - 1) * line_height / 2  # also center the text vertically
    for line in text_lines:
        watermark.drawCentredString(x, y, line)
        y -= watermark._leading


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


def convert_content_to_images(file_name: str, dpi: int):
    # load pages as images
    try:
        images = convert_from_path(file_name, dpi=dpi, fmt="png", transparent=True)
    except PopplerNotInstalledError:
        print(
            "Warning : the --save-as-image and --unselectable options require poppler to be installed. Proceeding without these options. Pleaser refer to the documentation for more information."
        )
        return None

    # get the page sizes
    pdf_to_transform = pypdf.PdfReader(file_name)
    page_sizes = []
    for page in pdf_to_transform.pages:
        page_sizes.append((page.mediabox.width, page.mediabox.height))

    # create new pdf
    pdf = canvas.Canvas(file_name)

    for image, (page_width, page_height) in zip(images, page_sizes):
        pdf.setPageSize((page_width, page_height))
        compressed = BytesIO()
        image.save(compressed, format="png", optimize=True, quality=dpi // 10)

        pdf.drawImage(
            ImageReader(compressed),
            0,
            0,
            width=page_width,
            height=page_height,
            mask="auto",
        )
        pdf.showPage()

    pdf.save()


def sort_pages(pdf: pypdf.PdfWriter, order: List[int]):
    output = pypdf.PdfWriter()
    for index in np.argsort(order):
        output.add_page(pdf.pages[int(index)])

    return output
