#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'schedule==0.5.0' ]

setup_requirements = [ ]

test_requirements = [ 'schedule==0.5.0' ]

setup(
    author="Aleksandar Nikolaev Dinkov",
    author_email='alexander.n.dinkov@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="A framework for easy automation of Bitcoin related tasks. PipeCash is flexible due to it's plugin system and configuration options. Read more at http://pipe.cash/",
    entry_points={
        'console_scripts': [
            'pipecash=pipecash.cli:main',
        ],
    },
    install_requires=requirements,
    license="OPEN BLOCKCHAIN-SPECIFIC LICENSE",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pipecash',
    name='pipecash',
    packages=find_packages(include=['pipecash']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Pipe-Cash/pipecash',
    version='0.1.0.1',
    zip_safe=False,
)
