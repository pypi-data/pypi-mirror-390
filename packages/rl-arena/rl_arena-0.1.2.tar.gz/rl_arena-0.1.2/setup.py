"""Setup configuration for rl-arena package."""

from setuptools import setup, find_packages
import os

# Read version from version.py
version = {}
with open(os.path.join("rl_arena", "version.py")) as f:
    exec(f.read(), version)

# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rl-arena",
    version=version["__version__"],
    author="RL Arena Contributors",
    author_email="kwaklloyd@gmail.com",
    description="A Python library for competitive reinforcement learning environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rl-arena/rl-arena-env",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20.0",
        "gymnasium>=0.28.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "mypy>=0.990",
            "flake8>=5.0.0",
        ],
        "training": [
            "stable-baselines3>=2.0.0",
        ],
        "interactive": [
            "pygame>=2.0.0",
        ],
        "visualization": [
            "matplotlib>=3.5.0",
        ],
        "all": [
            "stable-baselines3>=2.0.0",
            "pygame>=2.0.0",
            "matplotlib>=3.5.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
