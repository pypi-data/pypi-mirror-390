from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cleantextify-neal",
    version="0.1.0",
    author="Neal Salian",
    author_email="nealsalian4@gmail.com",
    description="A lightweight text preprocessing tool for NLP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Neal-Salian/clean-textify",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
