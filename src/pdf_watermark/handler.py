import os
from concurrent.futures import ThreadPoolExecutor
from tempfile import NamedTemporaryFile
from typing import Union

import click
import pypdf

from pdf_watermark.draw import draw_watermarks
from pdf_watermark.options import (
    DrawingOptions,
    FilesOptions,
    GridOptions,
    InsertOptions,
)
from pdf_watermark.utils import convert_content_to_images, sort_pages


def add_watermark_to_pdf(
    input: str,
    output: str,
    drawing_options: DrawingOptions,
    specific_options: Union[GridOptions, InsertOptions],
):
    pdf_writer = pypdf.PdfWriter()
    pdf_to_transform = pypdf.PdfReader(input)

    page_sizes = []
    for page in pdf_to_transform.pages:
        page_sizes.append((page.mediabox.width, page.mediabox.height))

    order = []
    # Only one watermark is computed per page size
    for watermark_width, watermark_height in set(page_sizes):
        with NamedTemporaryFile(delete=False) as temporary_file:
            # The watermark is stored in a temporary pdf file
            draw_watermarks(
                temporary_file.name,
                watermark_width,
                watermark_height,
                drawing_options,
                specific_options,
            )

            if drawing_options.unselectable and not drawing_options.save_as_image:
                convert_content_to_images(
                    temporary_file.name,
                    drawing_options.dpi,
                )

            watermark_pdf = pypdf.PdfReader(temporary_file.name)

            # Add watermark to pages with the same size
            for index, (page, (page_width, page_height)) in enumerate(
                zip(pdf_to_transform.pages, page_sizes)
            ):
                if page_width == watermark_width and page_height == watermark_height:
                    page.merge_page(watermark_pdf.pages[0])
                    pdf_writer.add_page(page)
                    order.append(index)

            # Remove temp file - https://stackoverflow.com/questions/23212435/permission-denied-to-write-to-my-temporary-file
            temporary_file.close()
            os.unlink(temporary_file.name)

    pdf_writer = sort_pages(pdf_writer, order)

    with open(output, "wb") as f:
        pdf_writer.write(f)

    if drawing_options.save_as_image:
        convert_content_to_images(output, drawing_options.dpi)


def add_watermark_from_options(
    files_options: FilesOptions,
    drawing_options: DrawingOptions,
    specific_options: Union[GridOptions, InsertOptions],
    verbose: bool,
):
    def process_file(input_file, output_file):
        if verbose or files_options.dry_run:
            if input_file == output_file:
                click.echo(f"modifying: {output_file}")
            else:
                click.echo(f"creating: {output_file}")
        if not files_options.dry_run:
            add_watermark_to_pdf(
                input_file, output_file, drawing_options, specific_options
            )

    if files_options.workers > 1:
        with ThreadPoolExecutor(max_workers=files_options.workers) as executor:
            futures = [
                executor.submit(process_file, inp, out) for inp, out in files_options
            ]
            for future in futures:
                future.result()
    else:
        for input_file, output_file in files_options:
            process_file(input_file, output_file)
