from setuptools import setup, find_packages

# Lendo o README.md para o PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="HeroTeams1103",
    version="0.1.1",
    description="Biblioteca de criação de heróis e times com fastapi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gustavo Firme Fiorot",
    author_email="gffiorot@gmail.com",
    url="https://github.com/gffiorot/HeroLib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlmodel",
        "pydantic",
        "python-dotenv",
        "email-validator",
    ],
    python_requires=">=3.8",
)