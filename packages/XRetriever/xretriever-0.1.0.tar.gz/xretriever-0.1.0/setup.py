#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XRetriever: X-ray Diffraction Pattern Matching and Crystal Structure Retrieval
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Package metadata
NAME = 'XRetriever'
VERSION = '0.1.0'
DESCRIPTION = 'X-ray Diffraction Pattern Matching and Crystal Structure Retrieval'
AUTHOR = 'Bin Cao'
AUTHOR_EMAIL = 'bcao686@connect.hkust-gz.edu.cn'
URL = 'https://github.com/Bin-Cao/XRetriever'
LICENSE = 'MIT'
PYTHON_REQUIRES = '>=3.8'

# Package dependencies
INSTALL_REQUIRES = [
    'numpy>=1.19.0',
    'scipy>=1.5.0',
    'pandas>=1.1.0',
    'matplotlib>=3.3.0',
    'tqdm>=4.50.0',
]

# Optional dependencies for development
EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=6.0.0',
        'pytest-cov>=2.10.0',
        'black>=20.8b1',
        'flake8>=3.8.0',
        'sphinx>=3.2.0',
    ],
    'database': [
        'ase>=3.20.0',
        'pymatgen>=2022.0.0',
    ],
}

# Classifiers for PyPI
CLASSIFIERS = [
    # Development Status
    'Development Status :: 4 - Beta',
    
    # Intended Audience
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    
    # Topic
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Chemistry',
    'Topic :: Scientific/Engineering :: Physics',
    'Topic :: Scientific/Engineering :: Information Analysis',
    
    # License
    'License :: OSI Approved :: MIT License',
    
    # Programming Language
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    
    # Operating System
    'Operating System :: OS Independent',
    'Operating System :: POSIX :: Linux',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    
    # Natural Language
    'Natural Language :: English',
]

# Keywords for PyPI search
KEYWORDS = [
    'xrd',
    'x-ray diffraction',
    'crystallography',
    'materials science',
    'pattern matching',
    'phase identification',
    'crystal structure',
    'materials characterization',
    'powder diffraction',
    'peak detection',
]

# Project URLs
PROJECT_URLS = {
    'Bug Reports': 'https://github.com/Bin-Cao/XRetriever/issues',
    'Source': 'https://github.com/Bin-Cao/XRetriever',
    'Documentation': 'https://github.com/Bin-Cao/XRetriever#readme',
}

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    project_urls=PROJECT_URLS,
    license=LICENSE,
    
    # Package discovery
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    
    # Include package data
    include_package_data=True,
    package_data={
        'XRetriever': ['*.txt', '*.md'],
    },
    
    # Dependencies
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    
    # Metadata
    classifiers=CLASSIFIERS,
    keywords=' '.join(KEYWORDS),
    
    # Entry points (optional - for command-line tools)
    # entry_points={
    #     'console_scripts': [
    #         'xretriever=XRetriever.cli:main',
    #     ],
    # },
    
    # Zip safe
    zip_safe=False,
)

