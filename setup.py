#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name="honcho",
    version="0.1.3",
    description="Honcho: the AMIGOS III operations program",
    author="Bruce Wallin, Coovi Meha",
    author_email="bruce.wallin@nsidc.org, coovi.meha@colorado.edu",
    url="https://github.com/wallinb/amigos3",
    packages=find_packages(),
    entry_points={"console_scripts": ["honcho=honcho.cli:main"]},
    include_package_data=True,
    zip_safe=False,
)
