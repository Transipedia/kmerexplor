#!/usr/bin/env python3
# -*- coding:utf8 -*-

import setuptools
from kmerexplor import info

setuptools.setup(
    name = 'kmerexplor',
    version = info.VERSION,
    author = info.AUTHOR,
    author_email = info.AUTHOR_EMAIL,
    description = info.SHORTDESC,
    long_description = open('README.md').read(),
    long_description_content_type = "text/markdown",
    url="https://github.com/Transipedia/KmerExploR",
    packages = setuptools.find_packages(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
    ],
    entry_points = {
        'console_scripts': [
            'kmerexplor = kmerexplor.core:main',
        ],
    },
    include_package_data = True,
    install_requires=['PyYAML'],
    python_requires = ">=3.6",
    licence = "GPLv3"
)
