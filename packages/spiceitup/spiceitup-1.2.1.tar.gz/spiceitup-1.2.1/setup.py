import os

from importlib_metadata import entry_points
from setuptools import setup, find_packages

setup(
    name='spiceitup',
    version='1.2.1',
    description='Quicklook tool for level 2 SPICE imaging',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='David Picard',
    author_email='david.picard@universite-paris-saclay.fr',
    url='https://git.ias.u-psud.fr/spice/data_quicklook',
    packages=['spiceitup'],
    install_requires='requirements.txt',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'spiceitup=spiceitup.__main__:main'
        ]
    }
)
