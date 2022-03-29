# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ssurgo_provider',
    version='0.1.1',
    description='ssurgo soil data provider',
    long_description=readme,
    author='Dauloudet Olivier',
    url='https://github.com/Smeaol22/ssurgo_provider.git',
    license=license,
    package_dir={'': 'src'},
    packages=find_packages('src')
)
