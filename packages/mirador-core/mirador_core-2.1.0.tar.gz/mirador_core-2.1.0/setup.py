from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mirador-core",
    version="2.1.0",
    author="Matthew David Scott",
    author_email="matthewdscott7@gmail.com",
    description="Unified core library for the Mirador AI ecosystem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guitargnarr/mirador",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core package uses only Python stdlib - no external dependencies required
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "ui": [
            "streamlit>=1.28.0",
            "plotly>=5.18.0",
        ],
        "web": [
            "gradio>=3.50.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
        "vector": [
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
        ],
        "all": [
            "streamlit>=1.28.0",
            "plotly>=5.18.0",
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
            "gradio>=3.50.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ]
    },
)