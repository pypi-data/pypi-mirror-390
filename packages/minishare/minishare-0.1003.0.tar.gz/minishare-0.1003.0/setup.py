from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="minishare",
    version="0.1003.0",
    author="MiniShare Team",
    author_email="team@minishare.com",
    description="A lightweight wrapper for financial data API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jasonmin/minishare.git",
    packages=find_packages(),
    package_data={
        "minishare": ["*/*.pyc", "*.pyc"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "requests>=2.20.0",
    ],
    keywords="finance, stock, data, api",
    zip_safe=False,
)