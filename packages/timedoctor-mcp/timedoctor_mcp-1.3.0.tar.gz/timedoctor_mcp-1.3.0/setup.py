"""
Setup script for Time Doctor Scraper
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='timedoctor-scraper',
    version='1.0.0',
    description='Web scraper for Time Doctor time tracking reports with MCP integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Time Doctor Scraper',
    author_email='',
    url='',
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='timedoctor scraper time-tracking mcp automation',
    entry_points={
        'console_scripts': [
            'timedoctor-scraper=src.mcp_server:main',
        ],
    },
)
