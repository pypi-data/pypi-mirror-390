"""
Configuration du package quantfinance
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="quantfinance",
    version="0.1.2",
    author="Marcel ALOEKPO",
    author_email="marcelaloekpo@gmail.com",
    description="Package Python pour la finance quantitative",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mafoya1er/quantfinance",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "sphinx>=4.5.0",
        ],
        "data": [
            "yfinance>=0.2.0",
            "pandas-datareader>=0.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "quantfinance=quantfinance.cli:main",
        ],
    },
)