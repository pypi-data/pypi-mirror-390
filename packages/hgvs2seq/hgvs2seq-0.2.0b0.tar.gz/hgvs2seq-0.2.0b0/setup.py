#!/usr/bin/env python3

import setuptools
from hgvs2seq import info

setuptools.setup(
    name = 'hgvs2seq',
    version = info.VERSION,
    author = info.AUTHOR,
    author_email = info.AUTHOR_EMAIL,
    description = info.SHORTDESC,
    long_description = open('README.md').read(),
    long_description_content_type = "text/markdown",
    url="https://github.com/bio2m/hgvs2seq",
    packages = setuptools.find_packages(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        # ~ "Programming language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
    ],
    entry_points = {
        'console_scripts': [
            'hgvs2seq = hgvs2seq.hgvs2seq:main',
        ],
    },
    include_package_data = True,
    install_requires=['biopython'],
    python_requires = ">=3.7",
    licence = "GPLv3"
)
