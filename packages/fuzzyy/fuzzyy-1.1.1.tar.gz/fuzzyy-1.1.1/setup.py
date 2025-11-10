from setuptools import setup, find_packages
import io
import os

def read(fname):
    return io.open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()

setup(
    name="fuzzyy",
    version="1.1.1",
    author="Spoof",
    author_email="xyz@gmail.com",
    description="Hi How Are You Doing",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="",  
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    license="MIT",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
