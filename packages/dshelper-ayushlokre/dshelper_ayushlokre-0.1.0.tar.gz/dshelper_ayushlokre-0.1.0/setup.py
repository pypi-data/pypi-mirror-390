"""Setup configuration for dshelper library."""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="dshelper-ayushlokre",
    version="0.1.0",
    author="Ayush Lokre",
    author_email="ayushlokre5@gmail.com",
    description="A Quality-of-Life Data Science Helper library for common ML/DS tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ayushlokre/dshelper",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "twine>=4.0.0",
            "build>=0.8.0",
        ],
    },
    keywords="data-science machine-learning preprocessing helper utilities",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/dshelper/issues",
        "Source": "https://github.com/yourusername/dshelper",
        "Documentation": "https://github.com/yourusername/dshelper#readme",
    },
)
