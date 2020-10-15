#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

with open("LICENSE", "r") as f:
    license = f.read()

setup(
    name="jason",
    description="yet another json parser",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Victor Franzi",
    author_email="victor.franzi@gmail.com",
    url="https://github.com/rotsix/jason",
    license=license,
    packages=find_packages(),
    entry_points={"console_scripts": ["jason=jason.__init__:main"]},
)
