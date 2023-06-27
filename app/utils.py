from reportlab.pdfgen import canvas
from math import cos, sin, pi
import numpy as np
from app.objects import DrawingOptions, UserInputs
import pypdf
from tempfile import NamedTemporaryFile


def create_watermark_pdf(
    file_name: str, width: float, height: float, drawing_options: DrawingOptions
):
    watermark = canvas.Canvas(file_name, pagesize=(width, height))

    horizontal_box_spacing = width / drawing_options.horizontal_boxes
    vertical_box_spacing = height / drawing_options.vertical_boxes

    rotation_angle_rad = drawing_options.angle * pi / 180
    rotation_matrix = np.array(
        [
            [cos(rotation_angle_rad), -sin(rotation_angle_rad)],
            [sin(rotation_angle_rad), cos(rotation_angle_rad)],
        ]
    )

    def change_base(x, y):
        # Since we rotated the original coordinates system, use the inverse of the rotation matrix
        # (which is the transposed matrix) to get the coordinates we have to draw at
        new_coordinates = np.transpose(rotation_matrix) @ np.array([[x], [y]])
        return new_coordinates[0, 0], new_coordinates[1, 0]

    watermark.setFillColor(drawing_options.color, alpha=drawing_options.opacity)
    watermark.setFont(drawing_options.font, drawing_options.size)
    watermark.rotate(drawing_options.angle)

    if drawing_options.margin:
        start_index = 1
    else:
        start_index = 0

    for x_index in range(start_index, drawing_options.horizontal_boxes + 1):
        for y_index in range(start_index, drawing_options.vertical_boxes + 1):
            # Coordinates to draw at in original coordinates system
            x_base = x_index * horizontal_box_spacing
            y_base = y_index * vertical_box_spacing

            if drawing_options.margin:
                x_base -= horizontal_box_spacing / 2
                y_base -= vertical_box_spacing / 2

            if drawing_options.text is not None:
                x_prime, y_prime = change_base(x_base, y_base)
                watermark.drawCentredString(
                    x_prime,
                    y_prime,
                    drawing_options.text,
                )

            if drawing_options.image is not None:
                # if the image is too big, scale it down to fit in the box
                width, height = drawing_options.image.getSize()
                if width > horizontal_box_spacing:
                    change_ratio = horizontal_box_spacing / width
                    width = horizontal_box_spacing
                    height *= change_ratio
                if height > vertical_box_spacing:
                    change_ratio = vertical_box_spacing / height
                    height = vertical_box_spacing
                    width *= change_ratio

                # drawImage draws from the bottom left corner, so we have to adjust the coordinates
                x_base -= width / 2
                y_base -= height / 2

                x_prime, y_prime = change_base(x_base, y_base)

                watermark.drawImage(
                    drawing_options.image,
                    x_prime,
                    y_prime,
                    width=width,
                    height=height,
                    mask="auto",
                )

    watermark.save()


def add_watermark_to_pdf(input: str, output: str, drawing_options: DrawingOptions):
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
        )

        watermark_pdf = pypdf.PdfReader(temporary_file.name)
        pdf_writer = pypdf.PdfWriter()

        for page in pdf_to_transform.pages:
            page.merge_page(watermark_pdf.pages[0])
            pdf_writer.add_page(page)

    with open(output, "wb") as f:
        pdf_writer.write(f)


def add_watermark_from_inputs(inputs: UserInputs):
    for input_file, output_file in inputs.files_options:
        add_watermark_to_pdf(input_file, output_file, inputs.drawing_options)
