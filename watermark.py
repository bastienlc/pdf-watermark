import click
from app.objects import UserInputs
from app.utils import add_watermark_from_inputs


@click.command()
@click.argument(
    "file",
)
@click.argument("watermark")
@click.option(
    "-c",
    "--color",
    type=str,
    help="Text color in hexadecimal format, e.g. #000000.",
    default="#000000",
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
    "-f",
    "--font",
    type=str,
    help="Text font to use. Supported fonts are those supported by reportlab.",
    default="Helvetica",
)
@click.option(
    "-s",
    "--size",
    type=int,
    help="Text font size.",
    default=12,
)
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
@click.option(
    "-r",
    "--save",
    type=str,
    help="File or folder to save results to. By default, the input files are overwritten.",
)
def cli(
    file,
    watermark,
    color,
    opacity,
    angle,
    font,
    size,
    horizontal_boxes,
    vertical_boxes,
    margin,
    save,
):
    """
    Add a WATERMARK to one or more PDF files referenced by FILE.
    WATERMARK can be either a string or a path to an image file.
    FILE can be a single file or a directory, in which case all PDF files in the directory will be watermarked.
    """
    add_watermark_from_inputs(
        UserInputs(
            file,
            watermark=watermark,
            color=color,
            opacity=opacity,
            angle=angle,
            font=font,
            size=size,
            horizontal_boxes=horizontal_boxes,
            vertical_boxes=vertical_boxes,
            margin=margin,
            save_to=save,
        )
    )
