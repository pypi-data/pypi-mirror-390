from setuptools import setup, find_packages

setup(
    name="natilog-lib",
    version="0.1.0",
    author="Natalí",
    install_requires=["requests>=2.25.1"],
    packages=find_packages(),
    description="Librería para interactuar con la API de NatiLog",
)