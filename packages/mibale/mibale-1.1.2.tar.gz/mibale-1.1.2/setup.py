from setuptools import setup, find_packages
import os

# Lit le README pour la description longue
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lit les requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

# Version du package
__version__ = "1.1.2"

setup(
    name="mibale",
    version=__version__,
    author="gedeon-kay",
    author_email="anikay59@gmail.com",
    description="Vue.js-like mobile framework in Python - Build native mobile apps with Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/votre-username/mibale",
    project_urls={
        "Documentation": "https://mibale.readthedocs.io",
        "Source Code": "https://github.com/votre-username/mibale",
        "Bug Tracker": "https://github.com/votre-username/mibale/issues",
    },
    packages=find_packages(include=["mibale", "mibale.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Android",
        "Operating System :: iOS",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mibale=mibale.cli.mibale_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mibale": [
            "templates/default/**/*",
            "templates/default/**/.*",
            "android/*.py",
            "ios/*.py",
        ],
    },
    keywords=[
        "mobile",
        "framework", 
        "vuejs",
        "android",
        "ios",
        "cross-platform",
        "native",
        "python",
        "mobile-development",
    ],
    license="MIT",
    platforms=["Android", "iOS", "Linux", "macOS", "Windows"],
)