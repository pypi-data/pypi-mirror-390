"""Setup script for sber-tunnel."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sber-tunnel",
    version="1.0.3",
    author="apaem",
    description="File synchronization service using Confluence API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "click>=8.1.0",
        "atlassian-python-api>=3.41.0",
        "pydantic>=2.5.0",
        "watchdog>=3.0.0",
        "requests>=2.31.0",
        "cryptography>=41.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sber-tunnel=sber_tunnel.cli.main:cli",
        ],
    },
)
