# pdf-watermark

A python CLI tool to add watermarks to a PDF.

## Description

There are multiple similar tools out there but I couldn't find one that really suited my needs. This project also serves as an excuse to play with building and distributing a python CLI tool.

## Getting Started

### Dependencies

* This project was built with python 3.11. However it should also run just fine with older versions.

### Installing

Available on PyPi (soon).

```
pip install pdf-watermark
```

### Usage

```
watermark --help
Usage: watermark [OPTIONS] FILE TEXT

Options:
  -c, --color TEXT                Hexadecimal color, e.g. #000000.
  -o, --opacity FLOAT             Opacity between 0 (invisible) and 1 (no
                                  transparency).
  -a, --angle FLOAT               Inclination of the text in degrees.
  -f, --font TEXT                 Font to use. Supported fonts are those
                                  supported by reportlab.
  -s, --size INTEGER              Font size.
  -h, --horizontal-boxes INTEGER  Number of times the text is repeated in the
                                  horizontal direction.
  -v, --vertical-boxes INTEGER    Number of times the text is repeated in the
                                  vertical direction.
  -m, --margin BOOLEAN            Wether to leave a margin around the page or
                                  not. When False (default), the text will be
                                  cut on the PDF edges.
  -r, --save TEXT                 File to save result to. By default, the
                                  input file is used.
  --help                          Show this message and exit.
```

## Authors

[@bastienlc](https://github.com/bastienlc)

## Version History

* 0.0.1
    * Work in progress

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

* [readme template](https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc)
