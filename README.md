# doxyphp2sphinx
API Documentation generator for PHP priojects which use Sphinx.

It acts as a compatibility layer between Doxygen (which is good at reading PHP),
and Sphinx (which is used by some online services to host HTML docs).

- http://www.sphinx-doc.org/en/master/
- http://www.doxygen.org/

## Example usage

This code was originally written to generate the API documentation for `gfx-php`
so that it could be hosted on [readthedocs.org](https://readthedocs.org/), so
we'll use that as an example:

- Code: https://github.com/mike42/gfx-php
- Docs: https://gfx-php.readthedocs.io


```
git clone https://github.com/mike42/gfx-php
cd docs
doxygen
doxyphp2sphinx.py Mike42::GfxPhp
make html
```

## License

See LICENSE
