import click
from app.objects import UserInputs
from app.utils import add_watermark_from_inputs


@click.command()
@click.argument(
    "file",
)
@click.argument("text")
@click.option(
    "-c",
    "--color",
    type=str,
    help="Hexadecimal color, e.g. #000000.",
    default="#000000",
)
@click.option(
    "-o",
    "--opacity",
    type=float,
    help="Opacity between 0 (invisible) and 1 (no transparency).",
    default=0.1,
)
@click.option(
    "-a",
    "--angle",
    type=float,
    help="Inclination of the text in degrees.",
    default=45,
)
@click.option(
    "-f",
    "--font",
    type=str,
    help="Font to use. Supported fonts are those supported by reportlab.",
    default="Helvetica",
)
@click.option(
    "-s",
    "--size",
    type=int,
    help="Font size.",
    default=12,
)
@click.option(
    "-h",
    "--horizontal-boxes",
    type=int,
    help="Number of times the text is repeated in the horizontal direction.",
    default=3,
)
@click.option(
    "-v",
    "--vertical-boxes",
    type=int,
    help="Number of times the text is repeated in the vertical direction.",
    default=6,
)
@click.option(
    "-m",
    "--margin",
    type=bool,
    help="Wether to leave a margin around the page or not. When False (default), the text will be cut on the PDF edges.",
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
    text,
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
    Add a watermark TEXT to one or more PDF files referenced by FILE. FILE can be a single file or a directory, in which case all PDF files in the directory will be watermarked.
    """
    add_watermark_from_inputs(
        UserInputs(
            file,
            text=text,
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
