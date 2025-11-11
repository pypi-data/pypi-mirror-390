#!/usr/bin/env python3
"""
TNS CLI Setup Script

Installation:
    pip install tnscli

Development Installation:
    pip install -e .

Usage:
    After installation, use 'tns' command from anywhere:
    $ tns --help
    $ tns stats
    $ tns check mydomain
"""

from setuptools import setup, find_packages
import os

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tnscli',
    version='1.0.0',
    description='Command-line interface for TAO Name Service - Similar to btcli for Bittensor',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='TNS Team',
    author_email='contact@taonames.com',
    url='https://github.com/taonames/tns-cli',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'tns=tns_cli.cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='tao bittensor blockchain cli domain-names tns',
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
    project_urls={
        'Bug Reports': 'https://github.com/taonames/tns-cli/issues',
        'Source': 'https://github.com/taonames/tns-cli',
    },
)
