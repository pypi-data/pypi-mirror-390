from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="metadidomi-server-plus",
    version="0.1.0",
    author="MetadidomiServerPlus Team",
    description="Un serveur avancé pour Metadidomi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/METADIDOMIOFFICIEL/Metadidomi-ServerPlus-Core",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        line.strip()
        for line in open("requirements.txt", "r", encoding="utf-8")
        if line.strip() and not line.startswith("#")
    ],
)