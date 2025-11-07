"""Setup script for data-analysis-mcp"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bachai-data-analysis-mcp",
    version="1.1.5",
    author="BACH Studio",
    author_email="contact@bachstudio.com",
    description="Data Analysis MCP Server - Model Context Protocol server for data analysis (stdio and SSE modes)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BACH-AI-Tools/data-analysis-mcp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "openpyxl>=3.1.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sse-starlette>=1.8.0",
        "httpx>=0.25.0",
    ],
    entry_points={
        "console_scripts": [
            "bachai-data-analysis-mcp=main:main",
            "bachai-data-analysis-mcp-sse=main:main_sse",
        ],
    },
)
