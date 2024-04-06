# setup.py
from setuptools import setup, find_packages

setup(
    name='bambot',
    version='0.1.0',
    author='Bam Corp.',
    author_email='spencer@bam.bot',
    description='A Python package for interfacing with Bam foundational AI models.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BamCorp/bambot',
    packages=find_packages(),
    install_requires=[
        # deps
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.6, <4',
)