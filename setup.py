# setup.py
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="bambot",
    version="0.4.2",
    author="Bam Corp",
    author_email="spencer@bam.bot",
    description="Containers for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bam-Corp/bambot",
    packages=find_packages(),
    package_data={'bambot': ['templates/*']},
    install_requires=["click", "docker", "tqdm", "python-dotenv"],
    entry_points={
        "console_scripts": ["bam=bambot.cli:main"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.6",
)