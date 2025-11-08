from setuptools import setup, find_packages

setup(
    name="primerD",
    version="0.1.1",
    author="Sarah Ali",
    author_email="alsayedsarah01@gmail.com",
    description="A Python package for designing PCR primers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sarahbiotech/primerD.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
