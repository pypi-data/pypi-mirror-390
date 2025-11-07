"""
Setup file for bedrock-limiter-sdk package.

This allows teammates to install via:
    pip install git+https://github.com/yourorg/token-limiter-cloudfront-alb.git

Or from local directory:
    pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bedrock-limiter-sdk",
    version="1.0.0",
    author="Tire Rack",
    author_email="dherthoge@tirerack.com",
    description="Drop-in replacement for boto3 bedrock-runtime client with token limiting and API key authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tire-Rack-Innovation/token-limiter",
    py_modules=["bedrock_limiter_sdk"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.28.0",
        "botocore>=1.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "langchain": [
            "langchain>=0.1.0",
            "langchain-aws>=0.1.0",
        ],
    },
)
