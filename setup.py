#!/usr/bin/env python3

from setuptools import setup, find_packages


print(find_packages(exclude=["examples"]))

setup(
    name='crownstone-lib-python-uart',
    version='0.0.0',
    packages=find_packages(exclude=["examples"]),
    install_requires=list(package.strip() for package in open('requirements.txt')),
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ]
)