from setuptools import setup, find_packages
import os 



setup(
    name="defoldsdk",
    version="1.3.7",
    author="issam Mhadhbi",
    author_email="mhadhbixissam@gmail.com",
    description="Defold protobuff compiled to python package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MhadhbiXissam/defoldsdk.git",
    packages=find_packages(),
    install_requires=[
        "protobuf","requests"
    ],
    project_urls={
        "Documentation": "https://github.com/MhadhbiXissam/defoldsdk/tree/main/doc",
        "Source": "https://github.com/MhadhbiXissam/defoldsdk.git"
    } , 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
