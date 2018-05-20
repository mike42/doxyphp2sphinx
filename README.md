# doxyphp2sphinx

API Documentation generator for PHP projects which use Sphinx.

It acts as a compatibility layer between Doxygen (which is good at reading PHP),
and Sphinx (which is used by some online services to host HTML docs).

- http://www.sphinx-doc.org/en/master/
- http://www.doxygen.org/

This tool is compatible with Python 2 and 3.

## Installation

### From source

```bash
git clone https://github.com/mike42/
python setup.py bdist_wheel --universal
pip install dist/doxyphp2sphinx-*.whl
```

### From pip

```bash
pip install doxyphp2sphinx
```

### Verification

Test that you have the command.

```
doxyphp2sphinx --help
```

## Command-line use

This package provides the `doxyphp2sphinx` command, which generates `.rst` files as output, given a directory
of `doxygen` XML files.

```bash
usage: doxyphp2sphinx [-h] [--xml-dir XML_DIR] [--out-dir OUT_DIR] [--verbose]
                      [--quiet]
                      root_namespace

Generate Sphinx-ready reStructuredText documentation or your PHP project,
using Doxygen XML as an input.

positional arguments:
  root_namespace

optional arguments:
  -h, --help         show this help message and exit
  --xml-dir XML_DIR  directory to read from
  --out-dir OUT_DIR  directory to write to
  --verbose, -v      more output
  --quiet, -q        less output
```

## Example

The `gfx-php` project uses this tool to publish documentation to [readthedocs.org](https://readthedocs.org/), so
we'll use that as an example:

- Code: https://github.com/mike42/gfx-php
- Docs: https://gfx-php.readthedocs.io

```
git clone https://github.com/mike42/gfx-php
cd docs
doxygen
doxyphp2sphinx Mike42::GfxPhp
make html
```

## License

doxyphp2sphinx is released under a BSD 2-Clause License. See LICENSE for the full text.
