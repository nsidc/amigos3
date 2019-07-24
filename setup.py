#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="amigos",
    version="0.1.0",
    description="AMIGOS III operations program",
    author="Bruce Wallin, coovi meha",
    author_email="bruce.wallin@nsidc.org, coovi.meha@colorado.edu",
    url="https://github.com/nsidc/amigos",
    packages=find_packages(exclude=("tasks",)),
    entry_points={"console_scripts": ["amigos=amigos.cli:main"]},
    include_package_data=True,
    zip_safe=False,
)
