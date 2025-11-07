from setuptools import setup, find_packages

# Lendo o README.md para o PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="HeroLIBmagnagomatheus",  # ⚡ Nome com hífen para o PyPI
    version="0.1.0",
    description="Biblioteca com model de Heros and Teams + generics and database in memory.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matheus de Oliveira Magnago",
    author_email="magnagomatheus7@gmail.com",
    url="https://github.com/magnagomatheus/HeroLib.git",   
    packages=[
        'lib_hero',
        'lib_hero.model',
        'lib_hero.repository',
        'lib_hero.service',
        'lib_hero.util'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)