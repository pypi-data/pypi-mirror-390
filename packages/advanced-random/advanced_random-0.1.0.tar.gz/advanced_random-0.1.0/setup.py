# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="advanced-random",
    version="0.1.0",
    author="DarkIce",
    author_email="mygopgopich@gmail.com",
    description="Расширенная библиотека для генерации случайных значений в Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Timer-sigma/AdvancedRandom",  # замени на свой (если будет)
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords="random, advanced, utility, generator, weighted, password",
    project_urls={
        "Source": "https://github.com/Timer-sigma/AdvancedRandom",
        "Bug Reports": "https://github.com/Timer-sigma/AdvancedRandom",
    },
)
