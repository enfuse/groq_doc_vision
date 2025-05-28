#!/usr/bin/env python3
"""
Setup script for Groq PDF Vision Extraction SDK
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Groq PDF Vision Extraction SDK - Comprehensive PDF processing with image analysis and custom schemas"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "groq>=0.4.0",
            "pypdfium2>=4.0.0",
            "Pillow>=9.0.0",
            "asyncio-compat>=0.1.0"
        ]

setup(
    name="groq-pdf-vision",
    version="1.0.0",
    author="SDAIA Team",
    author_email="contact@sdaia.gov.sa",
    description="Comprehensive PDF processing with Groq's vision models, image analysis, and custom schemas",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/enfuse/groq-humain",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Office Suites",
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
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "streamlit": [
            "streamlit>=1.28.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "groq-pdf=groq_pdf_vision.cli:cli_main",
        ],
    },
    include_package_data=True,
    package_data={
        "groq_pdf_vision": ["schemas/*.json", "examples/*.pdf"],
    },
    keywords="pdf, vision, groq, extraction, ai, ocr, document-processing, image-analysis",
    project_urls={
        "Bug Reports": "https://github.com/enfuse/groq-humain/issues",
        "Source": "https://github.com/enfuse/groq-humain",
        "Documentation": "https://github.com/enfuse/groq-humain/blob/main/README.md",
    },
) 