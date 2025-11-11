"""Setup script for sber-tunnel."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sber-tunnel",
    version="2.0.0",
    author="apaem",
    author_email="emila1998@yandex.ru",
    description="CLI для передачи файлов между директориями через Confluence API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*", "docs*", ".venv*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "atlassian-python-api>=3.41.0",
        "requests>=2.31.0",
        "cryptography>=41.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sber-tunnel=sber_tunnel.cli.main:cli",
        ],
    },
)
