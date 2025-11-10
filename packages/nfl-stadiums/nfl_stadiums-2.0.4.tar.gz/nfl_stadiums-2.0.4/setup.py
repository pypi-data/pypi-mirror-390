from setuptools import setup, find_packages

setup(
    name="nfl_stadiums",
    version="2.0.4",
    description="A simple python package that provides easy access to NFL stadium data",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="lukhed",
    author_email="lukhed.mail@gmail.com",
    url="https://github.com/lukhed/nfl_stadiums",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "lukhed-basic-utils>=1.4.0"
    ],
)