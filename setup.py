#!/usr/bin/env python
"""The setup script."""

import os
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['tqdm', 'numpy', 'scipy']

setup_requirements = [
    'pytest-runner',
    'numpy',
    'pandas',
]

test_requirements = [
    'pytest>=3',
]

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    author="Bo Peng",
    author_email='ben.bob@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Population-based Forward-time Simulator for the Outbreak of COVID-19",
    entry_points={
        'console_scripts': [
            'outbreak_simulator=covid19_outbreak_simulator.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='covid19_outbreak_simulator',
    name='covid19-outbreak-simulator',
    packages=find_packages(
        include=['covid19_outbreak_simulator', 'covid19_outbreak_simulator.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ictr/covid19-outbreak-simulator',
    version=get_version('covid19_outbreak_simulator/__init__.py'),
    zip_safe=False,
)
