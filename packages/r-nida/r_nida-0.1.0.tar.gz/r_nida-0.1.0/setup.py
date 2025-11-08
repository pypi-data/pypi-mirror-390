from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="r_nida",
    version="0.1.0",
    author="Henrylee",
    author_email="henrydionizi@gmail.com",
    description="A Python package that attempts to reverse engineer how NIDA (National Identification Authority) numbers are generated and extract basic information from National Identification Numbers (NIN) without using the official NIDA API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Henryle-hd/r_nida",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[""],
    include_package_data=True,
    # package_data={
    #     "r_nida": ["requirements.txt"],
    # }
)