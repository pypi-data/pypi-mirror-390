from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyfinancecalc",
    version="0.1.0",
    author="Karan Madhukar Lokhande",
    author_email="karanlokhande2005@gmail.com",
    description="A lightweight, dependency-free finance calculations library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/karanlokhande/pyfinancecalc",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    include_package_data=True,
    install_requires=[],
    project_urls={
        "Source": "https://github.com/karanlokhande/pyfinancecalc",
        "Tracker": "https://github.com/karanlokhande/pyfinancecalc/issues",
    },
)
