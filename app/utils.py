from reportlab.pdfgen import canvas
from math import cos, sin, pi
import numpy as np
from app.inputs import UserInputs
import pypdf
from tempfile import NamedTemporaryFile


def create_watermark_pdf(
    file_name: str, width: float, height: float, inputs: UserInputs
):
    watermark = canvas.Canvas(file_name, pagesize=(width, height))

    horizontal_box_spacing = width / inputs.horizontal_boxes
    vertical_box_spacing = height / inputs.vertical_boxes

    rotation_angle_rad = inputs.angle * pi / 180
    rotation_matrix = np.array(
        [
            [cos(rotation_angle_rad), -sin(rotation_angle_rad)],
            [sin(rotation_angle_rad), cos(rotation_angle_rad)],
        ]
    )

    watermark.setFillColor(inputs.color, alpha=inputs.opacity)
    watermark.setFont(inputs.font, inputs.size)
    watermark.rotate(inputs.angle)

    if inputs.margin:
        start_index = 1
    else:
        start_index = 0

    for x_index in range(start_index, inputs.horizontal_boxes + 1):
        for y_index in range(start_index, inputs.vertical_boxes + 1):
            # Coordinates to draw at in original coordinates system
            x_base = x_index * horizontal_box_spacing
            y_base = y_index * vertical_box_spacing

            if inputs.margin:
                x_base -= horizontal_box_spacing / 2
                y_base -= vertical_box_spacing / 2

            # Since we rotated the original coordinates system, use the inverse of the rotation matrix
            # (which is the transposed matrix) to get the coordinates we have to draw at
            new_coordinates = np.transpose(rotation_matrix) @ np.array(
                [[x_base], [y_base]]
            )

            watermark.drawCentredString(
                new_coordinates[0, 0],
                new_coordinates[1, 0],
                inputs.text,
            )

    watermark.save()


def add_watermark_to_pdf(inputs: UserInputs):
    pdf_to_transform = pypdf.PdfReader(inputs.file)
    pdf_box = pdf_to_transform.pages[0].mediabox
    page_width = pdf_box.width
    page_height = pdf_box.height

    with NamedTemporaryFile() as temporary_file:
        # The watermark is stored in a temporary pdf file
        create_watermark_pdf(
            temporary_file.name,
            page_width,
            page_height,
            inputs,
        )

        watermark_pdf = pypdf.PdfReader(temporary_file.name)
        pdf_writer = pypdf.PdfWriter()

        for page in pdf_to_transform.pages:
            page.merge_page(watermark_pdf.pages[0])
            pdf_writer.add_page(page)

    if inputs.save_to is None:
        save_to = inputs.file
    else:
        save_to = inputs.save_to

    with open(save_to, "wb") as fp:
        pdf_writer.write(fp)
