"""
Kapetanios Unit Root Test Package
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/kapetanios
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kapetanios-test",
    version="1.0.0",
    author="Dr. Merwan Roudane",
    author_email="merwanroudane920@gmail.com",
    description="Unit root test with up to m structural breaks (Kapetanios, 2005)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/merwanroudane/kapetanios",
    project_urls={
        "Bug Tracker": "https://github.com/merwanroudane/kapetanios/issues",
        "Documentation": "https://github.com/merwanroudane/kapetanios",
        "Source Code": "https://github.com/merwanroudane/kapetanios",
    },
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
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "statsmodels>=0.13.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    keywords="econometrics unit-root structural-breaks time-series kapetanios",
    license="MIT",
)
