"""Setup for DNACrypt package"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dnacrypt-lang",
    version="1.0.0",
    author="Harshith",
    description="A domain-specific programming language for DNA-based cryptography",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dnacrypt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
    ],
    entry_points={
        'console_scripts': [
            'dnacrypt=dnacrypt.cli:main',
        ],
    },
    include_package_data=True,
)
