from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simple-colortext",
    version="0.1.1",
    author="Anany Doneria",
    author_email="ananydoneria47@gmail.com",
    description="A simple package to print colored text in terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ananydoneria/simple-colortext",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
