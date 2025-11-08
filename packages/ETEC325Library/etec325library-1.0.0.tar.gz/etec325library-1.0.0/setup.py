#!/usr/bin/env python3
import os
import sys
import site
import setuptools
from distutils.core import setup


# Editable install in user site directory can be allowed with this hack:
# https://github.com/pypa/pip/issues/7953.
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

setup(
    name="ETEC325Library",
    version="1.0.0",
    description="Library functions for ETEC 325",
    author="R. Duke",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Education",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        "scipy",
        "matplotlib",
        "openpyxl",
        "pandas",
        "scikit-learn",
        "XlsxWriter",
        "numpy",
        "python-docx"
    ],
    python_requires=">=3.9",
)

