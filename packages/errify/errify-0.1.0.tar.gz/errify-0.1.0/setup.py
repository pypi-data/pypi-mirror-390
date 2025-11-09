from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="errify",
    version="0.1.0",
    author="Divakar Babu M P",
    author_email="divakarbabu369@gmail.com",
    description="Human-readable error messages for Python beginners",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DivakarBabuMP/errify",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    keywords="error-handling education debugging beginner-friendly",
    project_urls={
        "Bug Reports": "https://github.com/DivakarBabuMP/errify/issues",
        "Source": "https://github.com/DivakarBabuMP/errify",
    },
    entry_points={
        "console_scripts": [
            "errify=errify:main",
        ],
    },
)