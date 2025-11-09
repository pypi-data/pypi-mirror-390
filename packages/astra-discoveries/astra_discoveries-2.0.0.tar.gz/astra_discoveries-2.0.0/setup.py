#!/usr/bin/env python3
"""
ASTRA: Autonomous System for Transient Research & Analysis
Setup script for pip installation
"""

from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='astra-discoveries',
    version='2.0.0',
    author='ASTRA Collaboration',
    author_email='astra@shannonlabs.io',
    description='Autonomous System for Transient Research & Analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Shannon-Labs/astra',
    project_urls={
        'Documentation': 'https://github.com/Shannon-Labs/astra/docs',
        'Source': 'https://github.com/Shannon-Labs/astra',
        'Tracker': 'https://github.com/Shannon-Labs/astra/issues',
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
    python_requires='>=3.8',
    install_requires=[
        'astroquery>=0.4.11',
        'astropy>=5.0',
        'numpy>=1.20.0',
        'pandas>=1.3.0',
        'scipy>=1.7.0',
        'matplotlib>=3.4.0',
        'requests>=2.25.0',
        'beautifulsoup4>=4.9.0',
        'lxml>=4.6.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.9',
        ],
    },
    entry_points={
        'console_scripts': [
            'astra-discover=scripts.run_discovery:main',
            'astra=scripts.run_advanced:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)