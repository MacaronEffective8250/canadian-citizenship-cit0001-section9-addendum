#!/usr/bin/env python3
"""Setup script for CIT0001 Section 9 Grandparent Addendum Generator."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cit0001-grandparent-addendum",
    version="1.0.0",
    author="MacaronEffective",
    author_email="noreply@users.noreply.github.com",
    description="Generate editable PDF addendum for CIT 0001 Section 9 grandparent citizenship information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MacaronEffective8250/canadian-citizenship-cit0001-section9-addendum",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "reportlab>=3.6.0",
    ],
    entry_points={
        "console_scripts": [
            "cit0001-addendum=cit0001_addendum:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md"],
    },
)