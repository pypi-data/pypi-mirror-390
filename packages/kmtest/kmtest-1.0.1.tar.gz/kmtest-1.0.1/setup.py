"""
Setup script for kmtest package
"""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='kmtest',
    version='1.0.0',
    author='Dr. Merwan Roudane',
    author_email='merwanroudane920@gmail.com',
    description='Kobayashi-McAleer tests for linear and logarithmic transformations of integrated processes',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/merwanroudane/kmtest',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Office/Business :: Financial',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='econometrics time-series cointegration unit-root transformation',
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.19.0',
        'scipy>=1.5.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
            'black>=20.8b1',
            'flake8>=3.8',
            'mypy>=0.900',
        ],
        'examples': [
            'matplotlib>=3.3.0',
            'pandas>=1.1.0',
        ],
    },
    project_urls={
        'Documentation': 'https://github.com/merwanroudane/kmtest',
        'Source': 'https://github.com/merwanroudane/kmtest',
        'Bug Reports': 'https://github.com/merwanroudane/kmtest/issues',
    },
)
