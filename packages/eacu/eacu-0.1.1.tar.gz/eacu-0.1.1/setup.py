#!/usr/bin/env python
# coding:utf-8
import os
from setuptools import setup, find_packages

setup(
    name='eacu',
    version='0.1.1',
    description="Coder utils library for [Eagle's Baby]. *Do not install mammal.*",
    author_email='2229066748@qq.com',
    maintainer="Eagle'sBaby",
    maintainer_email='2229066748@qq.com',
    packages=find_packages(),
    # package_data={
    #     '': ['*.7z'],
    # },
    license='Apache Licence 2.0',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    # entry_points={
    #     'console_scripts': [
    #         'pyscreeps-arena=pyscreeps_arena:CMD_NewProject',
    #     ]
    # },
    keywords=['python'],
    python_requires='>=3.10',
    install_requires=[
        'art>=6.5',
        'loguru',
        'onion-arch>=0.4.2',
    ],
)
