from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent

setup(
    name="jugopy",
    version="1.0.6",
    author="Jean Junior LOGBO",
    author_email="jeanjuniorlogbo94@gmail.com",
    description="jugopy v 1.0.6",
    long_description= (HERE / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
