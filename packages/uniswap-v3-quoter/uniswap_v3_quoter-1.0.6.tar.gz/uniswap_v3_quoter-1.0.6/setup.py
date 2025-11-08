"""
Setup script for uniswap-v3-quoter
This file exists for backward compatibility with older pip versions
"""

from setuptools import setup
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="uniswap-v3-quoter",
    version="1.0.6",
    author="V3 Python Quoter Contributors",
    description="Python implementation of Uniswap V3 QuoterV2 for high-frequency trading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/v3-python-quoter",
    packages=[
        "uniswap_v3_quoter",
        "uniswap_v3_quoter.state",
        "uniswap_v3_quoter.uniswap_math",
    ],
    package_dir={
        "uniswap_v3_quoter": ".",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "web3>=6.0.0",
        "eth-abi>=4.0.0",
        "eth-utils>=2.0.0",
        "eth-typing>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.1",
        ],
        "performance": [
            "orjson>=3.9.0",
            "cytoolz>=0.12.0",
        ],
    },
    keywords="uniswap uniswap-v3 pancakeswap defi dex quoter trading ethereum bsc web3",
)

