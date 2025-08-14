"""
Setup script for Rudderstack SDET Assignment Framework
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rudderstack-sdet-framework",
    version="1.0.0",
    author="SDET Candidate",
    author_email="candidate@example.com",
    description="Comprehensive test automation framework for Rudderstack flows",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/rudderstack-sdet-assignment",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "black",
            "flake8",
            "mypy",
            "isort",
            "pre-commit",
        ],
        "test": [
            "pytest-cov",
            "pytest-mock",
            "pytest-html",
            "allure-pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "rudderstack-test=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.json", "*.md"],
    },
    keywords="testing, automation, selenium, webdriverio, playwright, rudderstack",
    project_urls={
        "Bug Reports": "https://github.com/your-username/rudderstack-sdet-assignment/issues",
        "Source": "https://github.com/your-username/rudderstack-sdet-assignment",
        "Documentation": "https://github.com/your-username/rudderstack-sdet-assignment/blob/main/README.md",
    },
) 