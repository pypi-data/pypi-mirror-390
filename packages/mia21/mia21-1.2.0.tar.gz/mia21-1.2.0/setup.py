"""Setup file for Mia21 Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mia21",
    version="1.2.0",
    author="Mia21",
    author_email="hello@mia21.com",
    description="Official Python SDK for Mia21 Chat API - Build AI chatbots in minutes with tool calling support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mia21/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ]
    },
    keywords="mia21 chat ai chatbot sdk api",
    project_urls={
        "Documentation": "https://docs.mia21.com",
        "Source": "https://github.com/mia21/python-sdk",
        "Bug Reports": "https://github.com/mia21/python-sdk/issues",
    },
)


