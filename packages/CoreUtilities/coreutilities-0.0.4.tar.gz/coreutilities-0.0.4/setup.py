"""
Setup configuration for CoreUtils-Python package.

This setup file enables the package to be installed via pip and published to PyPI.

Installation:
    pip install -e .  # Development mode
    pip install .     # Regular installation

Build distribution:
    python setup.py sdist bdist_wheel

Author: @Ruppert20
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Get version from git tags directly
import subprocess

def get_version_from_git():
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--exact-match'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return '0.0.1'

version = get_version_from_git()

# Read requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            # Skip optional dependencies (commented out)
            if not line.startswith('# '):
                requirements.append(line)

setup(
    name='CoreUtilities',
    version=version,
    author='@Ruppert20',
    author_email='',  # Add email if desired
    description='A comprehensive collection of Python utility functions for data science, file operations, and general-purpose programming',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Ruppert20/CoreUtils-Python',
    project_urls={
        'Bug Tracker': 'https://github.com/Ruppert20/CoreUtils-Python/issues',
        'Documentation': 'https://github.com/Ruppert20/CoreUtils-Python',
        'Source Code': 'https://github.com/Ruppert20/CoreUtils-Python',
    },
    packages=['CoreUtilities'],
    package_dir={'CoreUtilities': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
    ],
    python_requires='>=3.13.2',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=8.4.2',
            'pytest-cov>=4.1.0',
            'black>=24.0.0',
            'mypy>=1.8.0',
            'flake8>=7.0.0',
        ],
        'optional': [
            'polars>=1.33.0',
            'pyarrow>=21.0.0',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        'utilities',
        'data-science',
        'pandas',
        'numpy',
        'encryption',
        'serialization',
        'testing',
        'helpers',
    ],
)
