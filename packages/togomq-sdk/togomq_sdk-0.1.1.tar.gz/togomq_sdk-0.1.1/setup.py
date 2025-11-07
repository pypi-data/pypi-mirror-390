"""Setup script for togomq-sdk package."""
import re
from pathlib import Path
from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __init__.py
init_file = Path("togomq/__init__.py").read_text(encoding="utf-8")
version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', init_file, re.MULTILINE)
if version_match:
    version = version_match.group(1)
else:
    raise RuntimeError("Unable to find version string in togomq/__init__.py")

setup(
    name="togomq-sdk",
    version=version,
    author="TogoMQ",
    author_email="info@togomq.io",
    description="Official Python SDK for TogoMQ - a modern, high-performance message queue service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TogoMQ/togomq-sdk-python",
    project_urls={
        "Homepage": "https://togomq.io",
        "Documentation": "https://togomq.io/docs",
        "Repository": "https://github.com/TogoMQ/togomq-sdk-python",
        "Issues": "https://github.com/TogoMQ/togomq-sdk-python/issues",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.9",
    install_requires=[
        "togomq-grpc>=0.1.11",
        "grpcio>=1.60.0",
        "protobuf>=4.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "ruff>=0.0.285",
            "mypy>=1.5.0",
        ],
    },
    keywords="togomq message-queue grpc pubsub messaging",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)
