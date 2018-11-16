#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="smellycat",
    url="https://github.com/logitank/smellycat",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["smellycat = smellycat.main:main"]},
    install_requires=["rtmbot", "requests"],
)
