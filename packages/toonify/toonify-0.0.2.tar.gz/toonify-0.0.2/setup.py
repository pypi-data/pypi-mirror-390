"""Setup script for TOON format library."""
from setuptools import setup, find_packages

setup(
    name="toon-format",
    version="1.0.0",
    description="TOON (Token-Oriented Object Notation) - A compact, human-readable serialization format for LLMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="TOON Format Contributors",
    license="MIT",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[
        "tiktoken>=0.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "toon=toon.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="serialization toon json csv llm token-efficient",
)
