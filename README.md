# pdf-watermark

A python CLI tool to add watermarks to a PDF. Support for bulk processing of multiple PDF files, with nice saving options.

## Description

There are multiple similar tools out there but I couldn't find one that really suited my needs. This project also serves as an excuse to play with building and distributing a python CLI tool.

With this tool you can add a watermark to a PDF file. The watermark can either be a text string that you provide, or an image (PNG being the recommanded format).

This tool provides two commands.
* **insert**: The watermark is placed once on each page at a specific position.
* **grid**: The watermark is repeated multiple times on each page in a grid pattern.

Below is an example of a PDF before using this tool, after using this tool with the *grid* command and a text watermark, and after using this tool with the *grid* command and an image watermark.

<p align="middle">
  <img src="https://raw.githubusercontent.com/bastienlc/pdf-watermark/master/images/before.png" width="29%" />
  <img src="https://raw.githubusercontent.com/bastienlc/pdf-watermark/master/images/text.png" width="29%" />
  <img src="https://raw.githubusercontent.com/bastienlc/pdf-watermark/master/images/image.png" width="29%" />
</p>

You can control the opacity of the watermark and its inclination.

There are also specific options for text and image watermarks. For text watermarks, you can control the color, font and font size. For image watermarks, you can add a scale factor (by default, the image is scaled to fit nicely in the rectangles created by the horizontal and vertical repetitions).

With the *grid* command, you can control the number of repetitions along the horizontal and vertical directions, as well as wether to leave a margin around the page or not.

With the *insert* command, you can control the x and y coordinates at which the watermark is inserted, as well as the horizontal alignment relative to x (left, center or right).

## Getting Started

### Dependencies

* This project was built with python 3.11. However it should also run just fine with older versions.
* See `requirements.txt` for the list of dependencies.

### Installing

This package is available on PyPi.

```
pip install pdf-watermark
```

### Usage

```
Usage: watermark [OPTIONS] COMMAND [ARGS]...

  Add a watermark to one or more PDF files.

  The watermark can be repeated in a grid pattern using the grid command, or
  inserted at a specific position using the insert command.

Options:
  --help  Show this message and exit.

Commands:
  grid    Add a watermark in a grid pattern.
  insert  Add a watermark at a specific position.
```

**insert** command:
```
Usage: watermark insert [OPTIONS] FILE WATERMARK

  Add a watermark at a specific position.

  Add a WATERMARK to one or more PDF files referenced by FILE. WATERMARK can
  be either a string or a path to an image file. FILE can be a single file or
  a directory, in which case all PDF files in the directory will be
  watermarked.

Options:
  -y, --y FLOAT                   Position of the watermark with respect to
                                  the vertical direction. Must be between 0
                                  and 1.
  -x, --x FLOAT                   Position of the watermark with respect to
                                  the horizontal direction. Must be between 0
                                  and 1.
  -ha, --horizontal-alignment TEXT
                                  Alignment of the watermark with respect to
                                  the horizontal direction. Can be one of
                                  'left', 'right' and 'center'.
  -s, --save TEXT                 File or folder to save results to. By
                                  default, the input files are overwritten.
  -o, --opacity FLOAT             Watermark opacity between 0 (invisible) and
                                  1 (no transparency).
  -a, --angle FLOAT               Watermark inclination in degrees.
  -tc, --text-color TEXT          Text color in hexadecimal format, e.g.
                                  #000000.
  -tf, --text-font TEXT           Text font to use. Supported fonts are those
                                  supported by reportlab.
  -ts, --text-size INTEGER        Text font size.
  -is, --image-scale FLOAT        Scale factor for the image. Note that before
                                  this factor is applied, the image is already
                                  scaled down to fit in the boxes.
  --help                          Show this message and exit.
```

**grid** command:
```
Usage: watermark grid [OPTIONS] FILE WATERMARK

  Add a watermark in a grid pattern.

  Add a WATERMARK to one or more PDF files referenced by FILE. WATERMARK can
  be either a string or a path to an image file. FILE can be a single file or
  a directory, in which case all PDF files in the directory will be
  watermarked.

Options:
  -h, --horizontal-boxes INTEGER  Number of repetitions of the watermark along
                                  the horizontal direction.
  -v, --vertical-boxes INTEGER    Number of repetitions of the watermark along
                                  the vertical direction.
  -m, --margin BOOLEAN            Wether to leave a margin around the page or
                                  not. When False (default), the watermark
                                  will be cut on the PDF edges.
  -s, --save TEXT                 File or folder to save results to. By
                                  default, the input files are overwritten.
  -o, --opacity FLOAT             Watermark opacity between 0 (invisible) and
                                  1 (no transparency).
  -a, --angle FLOAT               Watermark inclination in degrees.
  -tc, --text-color TEXT          Text color in hexadecimal format, e.g.
                                  #000000.
  -tf, --text-font TEXT           Text font to use. Supported fonts are those
                                  supported by reportlab.
  -ts, --text-size INTEGER        Text font size.
  -is, --image-scale FLOAT        Scale factor for the image. Note that before
                                  this factor is applied, the image is already
                                  scaled down to fit in the boxes.
  --help                          Show this message and exit.
```

## Authors

[@bastienlc](https://github.com/bastienlc)

## Version History

* 1.0.0
    * Add text watermark support.
    * Add image watermark support.
    * Add CLI.
    * Add complex directories support.
* 2.0.0
    * Move tool to subcommand **grid**.
    * Add **insert** command.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

* [readme template](https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc)
