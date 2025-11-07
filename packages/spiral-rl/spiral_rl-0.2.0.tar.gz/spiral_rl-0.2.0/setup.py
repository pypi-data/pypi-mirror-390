#!/usr/bin/env python3
# Copyright 2025 SPIRAL Team. All Rights Reserved.

"""Setup script for SPIRAL-on-Tinker."""

from setuptools import find_packages, setup

# Read requirements
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="spiral-tinker",
    version="0.1.0",
    author="SPIRAL Team",
    author_email="",
    description="SPIRAL self-play RL training framework with Tinker integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spiral-rl/spiral-on-tinker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "spiral-tinker-train=train_spiral_tinker:main",
        ],
    },
)
