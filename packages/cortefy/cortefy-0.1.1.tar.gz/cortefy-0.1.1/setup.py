"""
Setup configuration for Cortefy Python package
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "cortefy" / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = "Python client library for the Cortefy API"

setup(
    name="cortefy",
    version="0.1.1",
    author="Cortefy",
    license="MIT",
    description="Python client library for the Cortefy API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cortefy.com",
    project_urls={
        "Documentation": "https://cortefy.com/docs",
        "Homepage": "https://cortefy.com",
    },
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license_files=(),  # Don't include LICENSE file in package
)

