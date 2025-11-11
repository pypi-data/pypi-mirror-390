from setuptools import setup, find_packages

setup(
    name="nati_log",
    version="1.5.1",
    author="Natalí",
    install_requires=["requests>=2.25.1"],
    packages=find_packages(),
    description="Librería para interactuar con la API de NatiLog",
)
