from typing import Tuple, Union
from reportlab.pdfgen import canvas
from math import cos, sin, pi
import numpy as np
from app.objects import DrawingOptions, GenericInputs, GridInputs, InsertInputs
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


def create_watermark_pdf(
    file_name: str,
    width: float,
    height: float,
    drawing_options: DrawingOptions,
    specific_inputs: Union[GridInputs, InsertInputs],
):
    if isinstance(specific_inputs, InsertInputs):
        raise NotImplementedError("Inserting watermarks is not implemented yet")

    watermark = canvas.Canvas(file_name, pagesize=(width, height))

    horizontal_box_spacing = width / specific_inputs.horizontal_boxes
    vertical_box_spacing = height / specific_inputs.vertical_boxes

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

            x_prime, y_prime = change_base(x_base, y_base, rotation_matrix)

            if drawing_options.text is not None:
                watermark.drawCentredString(
                    x_prime,
                    y_prime,
                    drawing_options.text,
                )

            if drawing_options.image is not None:
                # if the image is too big, scale it down to fit in the box
                image_width, image_height = drawing_options.image.getSize()
                if image_width > horizontal_box_spacing:
                    change_ratio = horizontal_box_spacing / image_width
                    image_width = horizontal_box_spacing
                    image_height *= change_ratio
                if image_height > vertical_box_spacing:
                    change_ratio = vertical_box_spacing / image_height
                    image_height = vertical_box_spacing
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
