"""Setup script for facebook"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bachai-facebook",
    version="1.0.3",
    author="BACH Studio",
    author_email="contact@bachstudio.com",
    description="Facebook Scraper MCP Server - 提供8个Facebook搜索工具的Model Context Protocol服务器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BACH-AI-Tools/facebook",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "mcp>=0.9.0",
        "httpx>=0.27.0",
    ],
    entry_points={
        "console_scripts": [
            "bachai-facebook=server:run_server",
        ],
    },
    py_modules=["server"],
)
