from setuptools import setup, find_packages

setup(
    name="fragua",
    version="0.1.0",
    author="SagoDev",
    description="Package for creating ETL environments for data analysis",
    packages=find_packages(where=".", include=["fragua", "fragua.*"]),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    url="https://github.com/SagoDev/Fragua",
    install_requires=[
        "numpy",
        "pandas",
        "pytest",
        "typing_extensions",
    ],
)
