"""
Setup configuration for cointhatemij package
"""

from setuptools import setup, find_packages
import os

def read_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    readme_path = os.path.join(here, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name='cointhatemij',
    version='0.1.0',
    author='Dr. Merwan Roudane',
    author_email='merwanroudane920@gmail.com',
    description='Hatemi-J Cointegration Test with Two Unknown Regime Shifts',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/merwanroudane/cointhatemij',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    keywords='econometrics cointegration structural-breaks time-series hatemi-j regime-shifts',
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.19.0',
        'scipy>=1.5.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/merwanroudane/cointhatemij/issues',
        'Source': 'https://github.com/merwanroudane/cointhatemij',
    },
)
