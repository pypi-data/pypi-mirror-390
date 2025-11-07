"""Setup configuration for togomq-grpc package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="togomq-grpc",
    version="0.1.11",
    author="Enter Pages Pro Ltd",
    author_email="dev@enterpages.co.uk",
    description="Auto-generated gRPC Python client for TogoMQ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TogoMQ/togomq-grpc-python",
    project_urls={
        "Bug Tracker": "https://github.com/TogoMQ/togomq-grpc-python/issues",
        "Documentation": "https://togomq.io",
        "Source Code": "https://github.com/TogoMQ/togomq-grpc-python",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "grpcio>=1.60.0",
        "protobuf>=5.29.0",
    ],
    extras_require={
        "dev": [
            "grpcio-tools>=1.60.0",
        ],
    },
)
