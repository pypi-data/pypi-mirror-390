"""
Setup script for Interpals Python Library.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='interpal',
    version='1.1.4',
    description='A comprehensive Python library for the Interpals API with sync/async support',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Interpals Python Library Contributors',
    author_email='',
    url='https://github.com/yourusername/interpal-python-lib',
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'aiohttp>=3.8.0',
        'websockets>=10.0',
        'requests-toolbelt>=1.0.0',
        
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.20.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.990',
        ],
        'validation': [
            'pydantic>=2.0.0',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
    ],
    keywords='interpals api client async websocket social',
    project_urls={
        'Documentation': 'https://github.com/yourusername/interpal-python-lib/wiki',
        'Source': 'https://github.com/yourusername/interpal-python-lib',
        'Tracker': 'https://github.com/yourusername/interpal-python-lib/issues',
    },
)

