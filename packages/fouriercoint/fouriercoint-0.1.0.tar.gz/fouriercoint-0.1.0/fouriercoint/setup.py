"""
Setup script for fouriercoint package

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/fouriercoint
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fouriercoint",
    version="1.0.0",
    author="Dr. Merwan Roudane",
    author_email="merwanroudane920@gmail.com",
    description="Fourier Cointegration Test - Tsong et al. (2016) implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/merwanroudane/fouriercoint",
    project_urls={
        "Bug Tracker": "https://github.com/merwanroudane/fouriercoint/issues",
        "Documentation": "https://github.com/merwanroudane/fouriercoint#readme",
        "Source Code": "https://github.com/merwanroudane/fouriercoint",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "examples": [
            "pandas>=1.1.0",
            "matplotlib>=3.3.0",
        ],
    },
    keywords=[
        "cointegration",
        "econometrics",
        "time series",
        "fourier approximation",
        "structural breaks",
        "unit root",
        "DOLS",
        "long-run equilibrium",
    ],
    include_package_data=True,
    zip_safe=False,
)
