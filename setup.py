from setuptools import setup
from os import path

with open(path.join(path.dirname(__file__), 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='database',
    version='0.0.0',
    description='PeP. et al. member databse',
    long_description=long_description,
    packages=['database'],
    install_requires=[
        'flask',
        'flask-admin',
        'flask-mongoengine',
        'pymongo',
    ],
)
