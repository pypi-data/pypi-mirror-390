"""
Setup configuration for KardoCSS
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Leer versión
version = "1.1.4"

setup(
    name="kardocss",
    version=version,
    author="Juan Quezada",
    author_email="",
    description="Framework CSS 100% Mobile-First, Modular y Optimizado",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/webcien/KardoCSS",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Sin dependencias externas
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "black>=24.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kardocss=kardocss.cli.build:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

