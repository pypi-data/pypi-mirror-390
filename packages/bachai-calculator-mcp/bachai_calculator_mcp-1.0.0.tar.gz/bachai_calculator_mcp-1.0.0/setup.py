"""Setup script for calculator-mcp"""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bachai-calculator-mcp",
    version="1.0.0",
    author="BACH Studio",
    author_email="contact@bachstudio.com",
    description="Calculator MCP Server - Basic math operations via Model Context Protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BACH-AI-Tools/calculator-mcp",
    py_modules=["main"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "bachai-calculator-mcp=main:main",
        ],
    },
)

