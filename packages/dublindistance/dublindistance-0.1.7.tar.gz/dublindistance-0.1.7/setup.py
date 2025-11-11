from setuptools import setup, find_packages

setup(
    name="dublindistance",
    version="0.1.7",
    packages=find_packages(),
    install_requires=["geopy"],
    description="Simple Dublin area distance and transport suggestion tool",
    author="Jeevanjot Singh",
    license="MIT",
)
