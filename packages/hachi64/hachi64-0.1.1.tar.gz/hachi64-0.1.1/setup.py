from setuptools import setup, find_packages

setup(
    name="hachi64",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="A library for custom Base64 encoding and decoding.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/fengb3/hachi64",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
