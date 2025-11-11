"""
BoundedTest: GLS-based unit root tests for bounded processes

Implementation based on Carrion-i-Silvestre and Gadea (2013)
"GLS-based unit root tests for bounded processes"
Economics Letters 120 (2013) 184-187
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="boundedtest",
    version="1.0.0",
    author="Merwan Roudane",
    author_email="merwanroudane920@gmail.com",
    description="GLS-based unit root tests for bounded time series",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/merwanroudane/boundedtest",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "statsmodels>=0.13.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    include_package_data=True,
    package_data={
        "boundedtest": ["data/*.csv"],
    },
)
