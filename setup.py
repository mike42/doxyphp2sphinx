"""API Documentation generator for PHP projects which use Sphinx.
See:
https://github.com/mike42/doxyphp2sphinx
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='doxyphp2sphinx',
    version='1.0.1',
    description='API Documentation generator for PHP projects which use Sphinx.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mike42/doxyphp2sphinx',
    author='Michael Billington',
    author_email='michael.billington@gmail.com',
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Framework :: Sphinx',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Documentation',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities'
    ],

    keywords='doxygen sphinx restructuredtext readthedocs php documentation',  # Optional

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=['enum34'],  # Optional

    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    entry_points={
        'console_scripts': [
            'doxyphp2sphinx=doxyphp2sphinx.cli:Cli.run',
        ],
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/mike42/doxyphp2sphinx/issues',
        'Source': 'https://github.com/mike42/doxyphp2sphinx',
    },
)
