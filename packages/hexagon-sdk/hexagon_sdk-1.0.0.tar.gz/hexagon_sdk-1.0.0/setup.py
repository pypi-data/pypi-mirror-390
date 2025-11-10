"""
Setup configuration for hexagon-sdk
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hexagon-sdk",
    version="1.0.0",
    author="Hexagon Labs",
    author_email="hello@joinhexagon.com",
    description="Make your website AI-readable by ChatGPT, Perplexity, Claude and other AI platforms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hexagon-labs/hexagon-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Framework :: Django",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "flask": ["flask>=2.0.0"],
        "django": ["django>=3.2.0"],
    },
    keywords="ai gpt chatgpt claude perplexity seo ai-search crawler bot",
)

