from setuptools import setup, find_packages

setup(
    name="stringmagic",
    version="0.1.4",  # bump version
    author="Priyanshu Modak",
    author_email="priyanshumodak21@gmail.com",
    description="A simple yet powerful Python package providing various string manipulation utilities for text processing.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
