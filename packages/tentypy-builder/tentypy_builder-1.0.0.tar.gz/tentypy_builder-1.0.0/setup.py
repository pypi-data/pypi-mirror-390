"""
TentyPy Builder Setup
Author: Keniding
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='tentypy-builder',
    version='1.0.0',
    author='Keniding',
    author_email='kenidingh@gmail.com',
    description='Professional project structure generator with template support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Keniding/tentypy-builder',

    packages=find_packages(exclude=['tests*', 'docs*']),
    include_package_data=True,

    package_data={
        'tentypy': ['builder/templates/*.json'],
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],

    python_requires='>=3.8',

    install_requires=[
        'rich>=10.0.0',
    ],

    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.990',
        ],
        'yaml': [
            'pyyaml>=6.0',
        ],
        'all': [
            'pyyaml>=6.0',
        ],
    },

    entry_points={
        'console_scripts': [
            'tentypy-builder=tentypy.builder.cli:main',
        ],
    },

    keywords='project-generator template builder architecture clean-architecture',

    project_urls={
        'Bug Reports': 'https://github.com/Keniding/tentypy-builder/issues',
        'Source': 'https://github.com/Keniding/tentypy-builder',
        'Documentation': 'https://github.com/Keniding/tentypy-builder#readme',
    },
)
