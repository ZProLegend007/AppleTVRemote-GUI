#!/usr/bin/env python3
"""Setup script for AppleTVRemote-GUI."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="appletv-remote-gui",
    version="1.0.0",
    author="Zac",
    author_email="",
    description="A modern Linux GUI application for controlling Apple TV and HomePod devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZProLegend007/AppleTVRemote-GUI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "appletv-remote-gui=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["resources/*", "resources/*/*"],
    },
)