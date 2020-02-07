#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os

from setuptools import setup

with open('README.MD') as readme_file:
    readme = readme_file.read()


def get_req(file: str) -> list:
    _r = []
    with open(os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        file
    )) as f:
        _r.extend([l for l in f.read().splitlines() if not l.startswith('#')])
    return _r


setup_requirements = []

setup(
    install_requires=get_req('requirements.txt'),
)
