# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from setuptools import setup, find_packages
import os

def read_requirements():
    here = r"C:\Users\aceofspades\ife_surrogate_model\requirements.txt"
    with open(here, encoding="utf-8") as f:
        return [line for line in f.read().splitlines() if "@" not in line]

setup(
    name="IFE_Surrogate",
    version="0.1.2",
    description="A machine learning library intended for surrogate modeling.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your-repo",
    packages=find_packages(),
    install_requires=read_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)