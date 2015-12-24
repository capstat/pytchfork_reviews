"""A setuptools based setup module."""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.txt')) as f:
    long_description = f.read()

setup(
    name='pytchfork',
    version='1.0.0',
    description='602 Final Project',
    long_description=long_description,
    url='https://github.com/capstat/pytchfork',
    author='Nick Capofari',
    author_email='ncapofari@yahoo.com',
    classifiers=['Programming Language :: Python :: 2.7'],
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['fuzzywuzzy'],
    package_data={'pytchfork':['all_pitchfork_albums.csv']},
    entry_points={'console_scripts': ['pytchfork=pytchfork.__main__:main']}    
)
