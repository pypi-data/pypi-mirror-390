from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gspread_datarame",
    version="0.1.0",
    author="Data Tools Dev",
    author_email="dev@datatools.example",
    description="Simple data utilities for spreadsheet operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datatools/gspread_datarame",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[],
    keywords="spreadsheet data utilities helper",
)
