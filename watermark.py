import click
from app.options import (
    DrawingOptions,
    FilesOptions,
    GridOptions,
    InsertOptions,
)
from app.handler import add_watermark_from_options
from functools import wraps


def generic_watermark_parameters(f):
    @wraps(f)
    @click.argument("file")
    @click.argument("watermark")
    @click.option(
        "-s",
        "--save",
        type=str,
        help="File or folder to save results to. By default, the input files are overwritten.",
    )
    @click.option(
        "-o",
        "--opacity",
        type=float,
        help="Watermark opacity between 0 (invisible) and 1 (no transparency).",
        default=0.1,
    )
    @click.option(
        "-a",
        "--angle",
        type=float,
        help="Watermark inclination in degrees.",
        default=45,
    )
    @click.option(
        "-tc",
        "--text-color",
        type=str,
        help="Text color in hexadecimal format, e.g. #000000.",
        default="#000000",
    )
    @click.option(
        "-tf",
        "--text-font",
        type=str,
        help="Text font to use. Supported fonts are those supported by reportlab.",
        default="Helvetica",
    )
    @click.option(
        "-ts",
        "--text-size",
        type=int,
        help="Text font size.",
        default=12,
    )
    @click.option(
        "-is",
        "--image-scale",
        type=float,
        help="Scale factor for the image. Note that before this factor is applied, the image is already scaled down to fit in the boxes.",
        default=1,
    )
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


@click.group()
def cli():
    """
    Add a watermark to one or more PDF files.

    The watermark can be repeated in a grid pattern using the grid command, or inserted at a specific position using the insert command.
    """
    pass


@cli.command()
@click.option(
    "-y",
    "--y",
    type=float,
    help="Position of the watermark with respect to the vertical direction. Must be between 0 and 1.",
    default=0.5,
)
@click.option(
    "-x",
    "--x",
    type=float,
    help="Position of the watermark with respect to the horizontal direction. Must be between 0 and 1.",
    default=0.5,
)
@click.option(
    "-ha",
    "--horizontal-alignment",
    type=str,
    help="Alignment of the watermark with respect to the horizontal direction. Can be one of 'left', 'right' and 'center'.",
    default="center",
)
@generic_watermark_parameters
def insert(
    file,
    watermark,
    save,
    opacity,
    angle,
    text_color,
    text_font,
    text_size,
    image_scale,
    y,
    x,
    horizontal_alignment,
):
    """
    Add a watermark at a specific position.

    Add a WATERMARK to one or more PDF files referenced by FILE.
    WATERMARK can be either a string or a path to an image file.
    FILE can be a single file or a directory, in which case all PDF files in the directory will be watermarked.
    """
    add_watermark_from_options(
        FilesOptions(input=file, output=save),
        DrawingOptions(
            watermark=watermark,
            opacity=opacity,
            angle=angle,
            text_color=text_color,
            text_font=text_font,
            text_size=text_size,
            image_scale=image_scale,
        ),
        InsertOptions(
            y=y,
            x=x,
            horizontal_alignment=horizontal_alignment,
        ),
    )


@cli.command()
@click.option(
    "-h",
    "--horizontal-boxes",
    type=int,
    help="Number of repetitions of the watermark along the horizontal direction.",
    default=3,
)
@click.option(
    "-v",
    "--vertical-boxes",
    type=int,
    help="Number of repetitions of the watermark along the vertical direction.",
    default=6,
)
@click.option(
    "-m",
    "--margin",
    type=bool,
    help="Wether to leave a margin around the page or not. When False (default), the watermark will be cut on the PDF edges.",
    default=False,
)
@generic_watermark_parameters
def grid(
    file,
    watermark,
    save,
    opacity,
    angle,
    text_color,
    text_font,
    text_size,
    image_scale,
    horizontal_boxes,
    vertical_boxes,
    margin,
):
    """
    Add a watermark in a grid pattern.

    Add a WATERMARK to one or more PDF files referenced by FILE.
    WATERMARK can be either a string or a path to an image file.
    FILE can be a single file or a directory, in which case all PDF files in the directory will be watermarked.
    """
    add_watermark_from_options(
        FilesOptions(input=file, output=save),
        DrawingOptions(
            watermark=watermark,
            opacity=opacity,
            angle=angle,
            text_color=text_color,
            text_font=text_font,
            text_size=text_size,
            image_scale=image_scale,
        ),
        GridOptions(
            horizontal_boxes=horizontal_boxes,
            vertical_boxes=vertical_boxes,
            margin=margin,
        ),
    )
