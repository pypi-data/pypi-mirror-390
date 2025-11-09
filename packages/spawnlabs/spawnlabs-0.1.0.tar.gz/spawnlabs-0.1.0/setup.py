from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="spawnlabs",
    version="0.1.0",
    author="SpawnLabs",
    author_email="contact@spawnlabs.ai",
    description="Intelligent platform for building, running, and maintaining autonomous systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://spawnlabs.ai",
    project_urls={
        "Bug Tracker": "https://github.com/teddyoweh/spawn-frontend-temp/issues",
        "Documentation": "https://spawnlabs.ai/docs",
        "Source Code": "https://github.com/teddyoweh/spawn-frontend-temp",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies needed for basic git clone functionality
    ],
    entry_points={
        "console_scripts": [
            "spawn=spawnlabs.cli:main",
        ],
    },
    keywords="frontend, ui, development, ai, spawn, spawnlabs",
    include_package_data=True,
)

