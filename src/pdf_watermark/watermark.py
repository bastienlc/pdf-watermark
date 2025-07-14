from functools import wraps

import click

from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import (
    DrawingOptions,
    FilesOptions,
    GridOptions,
    InsertOptions,
)


class DEFAULTS:
    angle = 45
    dpi = 300
    dry_run = False
    workers = 1
    horizontal_alignment = "center"
    horizontal_boxes = 3
    image_scale = 1
    margin = False
    opacity = 0.1
    save_as_image = False
    text_color = "#000000"
    text_font = "Helvetica"
    text_size = 12
    unselectable = False
    verbose = True
    vertical_boxes = 6
    x = 0.5
    y = 0.5


def generic_watermark_parameters(f):
    @wraps(f)
    @click.argument("file")
    @click.argument("watermark")
    @click.option(
        "-s",
        "--save",
        type=str,
        help="File or folder to save results to. By default, the input files are overwritten.",
        show_default=True,
    )
    @click.option(
        "-o",
        "--opacity",
        type=float,
        help="Watermark opacity between 0 (invisible) and 1 (no transparency).",
        default=DEFAULTS.opacity,
        show_default=True,
    )
    @click.option(
        "-a",
        "--angle",
        type=float,
        help="Watermark inclination in degrees.",
        default=DEFAULTS.angle,
        show_default=True,
    )
    @click.option(
        "-tc",
        "--text-color",
        type=str,
        help="Text color in hexadecimal format, e.g. #000000.",
        default=DEFAULTS.text_color,
        show_default=True,
    )
    @click.option(
        "-tf",
        "--text-font",
        type=str,
        help="Text font to use. Supported fonts are those supported by reportlab.",
        default=DEFAULTS.text_font,
        show_default=True,
    )
    @click.option(
        "-ts",
        "--text-size",
        type=int,
        help="Text font size.",
        default=DEFAULTS.text_size,
        show_default=True,
    )
    @click.option(
        "--unselectable",
        type=bool,
        is_flag=True,
        help="Make the watermark text unselectable. This works by drawing the text as an image, and thus results in a larger file size.",
        default=DEFAULTS.unselectable,
        show_default=True,
    )
    @click.option(
        "-is",
        "--image-scale",
        type=float,
        help="Scale factor for the image. Note that before this factor is applied, the image is already scaled down to fit in the boxes.",
        default=DEFAULTS.image_scale,
        show_default=True,
    )
    @click.option(
        "--save-as-image",
        type=bool,
        is_flag=True,
        help="Convert each PDF page to an image. This makes removing the watermark more difficult but also increases the file size.",
        default=DEFAULTS.save_as_image,
        show_default=True,
    )
    @click.option(
        "--dpi",
        type=int,
        help="DPI to use when saving the PDF as an image.",
        default=DEFAULTS.dpi,
        show_default=True,
    )
    @click.option(
        "--dry-run",
        is_flag=True,
        help="Enumerate affected files without modifying them.",
        default=DEFAULTS.dry_run,
        show_default=True,
    )
    @click.option(
        "--workers",
        type=int,
        help="Number of parallel workers to use. This can speed up processing of multiple files.",
        default=DEFAULTS.workers,
        show_default=True,
    )
    @click.option(
        "--verbose",
        type=bool,
        help="Print information about the files being processed.",
        default=DEFAULTS.verbose,
        show_default=True,
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
    default=DEFAULTS.y,
    show_default=True,
)
@click.option(
    "-x",
    "--x",
    type=float,
    help="Position of the watermark with respect to the horizontal direction. Must be between 0 and 1.",
    default=DEFAULTS.x,
    show_default=True,
)
@click.option(
    "-ha",
    "--horizontal-alignment",
    type=str,
    help="Alignment of the watermark with respect to the horizontal direction. Can be one of 'left', 'right' and 'center'.",
    default=DEFAULTS.horizontal_alignment,
    show_default=True,
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
    unselectable,
    image_scale,
    save_as_image,
    dpi,
    dry_run,
    workers,
    verbose,
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
        FilesOptions(input=file, output=save, dry_run=dry_run, workers=workers),
        DrawingOptions(
            watermark=watermark,
            opacity=opacity,
            angle=angle,
            text_color=text_color,
            text_font=text_font,
            text_size=text_size,
            unselectable=unselectable,
            image_scale=image_scale,
            save_as_image=save_as_image,
            dpi=dpi,
        ),
        InsertOptions(
            y=y,
            x=x,
            horizontal_alignment=horizontal_alignment,
        ),
        verbose=verbose,
    )


@cli.command()
@click.option(
    "-h",
    "--horizontal-boxes",
    type=int,
    help="Number of repetitions of the watermark along the horizontal direction.",
    default=DEFAULTS.horizontal_boxes,
    show_default=True,
)
@click.option(
    "-v",
    "--vertical-boxes",
    type=int,
    help="Number of repetitions of the watermark along the vertical direction.",
    default=DEFAULTS.vertical_boxes,
    show_default=True,
)
@click.option(
    "-m",
    "--margin",
    type=bool,
    is_flag=True,
    help="Wether to leave a margin around the page or not. When False (default), the watermark will be cut on the PDF edges.",
    default=DEFAULTS.margin,
    show_default=True,
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
    unselectable,
    image_scale,
    save_as_image,
    dpi,
    dry_run,
    workers,
    verbose,
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
        FilesOptions(input=file, output=save, dry_run=dry_run, workers=workers),
        DrawingOptions(
            watermark=watermark,
            opacity=opacity,
            angle=angle,
            text_color=text_color,
            text_font=text_font,
            text_size=text_size,
            unselectable=unselectable,
            image_scale=image_scale,
            save_as_image=save_as_image,
            dpi=dpi,
        ),
        GridOptions(
            horizontal_boxes=horizontal_boxes,
            vertical_boxes=vertical_boxes,
            margin=margin,
        ),
        verbose=verbose,
    )


if __name__ == "__main__":
    cli()
