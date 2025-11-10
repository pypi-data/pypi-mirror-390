from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hello-pypi-thalles",  # precisa ser único no PyPI
    version="0.1.0",
    author="Thalles Freitas",
    author_email="thalles@example.com",
    description="A simple Hello World library example",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seuusuario/hello-pypi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
