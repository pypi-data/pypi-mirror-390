"""
Setup script for the Graphora client library.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="graphora",
    version="0.4.1",
    author="Graphora Team",
    author_email="support@graphora.io",
    description="Python client for the Graphora API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/graphora/graphora-client",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.8.0",
        "pyyaml>=5.4.0",
    ],
)
