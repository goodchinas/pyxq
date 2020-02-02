#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from os import path

with open('README.MD') as readme_file:
    readme = readme_file.read()


# with open('HISTORY.rst') as history_file:
#     history = history_file.read()

# todo here
def get_requirements(file):
    with open(path.join(path.dirname(path.realpath(__file__)), file)) as f:
        _r = [i for i in f.read().splitlines() if i and not i.startswith('#')]
    return _r


setup_requirements = []

setup(
    author="tim",
    author_email='goodchinas@qq.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        # 'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="python quant is so easy.",
    install_requires=[],
    license="MIT license",
    long_description_content_type="text/markdown",
    long_description=readme,  # + '\n\n' + history,
    include_package_data=True,
    keywords='pyxq',
    name='pyxq',
    # packages=find_packages(include=['pyxq']),
    packages=find_packages(where='.', exclude=(), include=("pyxq*",), ),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=['numpy', 'pandas'],
    url='https://github.com/goodchinas/pyxq',
    version='0.1.5',
    zip_safe=False,
)
