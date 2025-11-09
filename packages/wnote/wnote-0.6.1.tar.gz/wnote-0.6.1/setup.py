"""Setup configuration for WNote."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="wnote",
    version="0.6.1",
    description="Terminal Note Taking Application with beautiful UI and rich features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="imnahn",
    author_email="",
    url="https://github.com/imnotnahn/wnote",
    project_urls={
        "Bug Reports": "https://github.com/imnotnahn/wnote/issues",
        "Source": "https://github.com/imnotnahn/wnote",
        "Documentation": "https://github.com/imnotnahn/wnote#readme",
    },
    packages=find_packages(include=["wnote", "wnote.*"]),
    include_package_data=True,
    install_requires=[
        "click>=8.1.7",
        "rich>=13.7.0",
        "requests>=2.28.0",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
        "markdown>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wnote=wnote.cli:cli",
        ],
    },
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Utilities",
        "Topic :: Text Processing",
    ],
    keywords="notes note-taking cli terminal productivity organization",
    zip_safe=False,
)
