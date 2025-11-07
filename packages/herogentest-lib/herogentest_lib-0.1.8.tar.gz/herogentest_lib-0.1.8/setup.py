from setuptools import setup, find_packages

# Lendo o README.md para o PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="herogentest-lib",  # ⚡ Nome com hífen para o PyPI
    version="0.1.8",
    description="Lib de heroes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pedro Renã da Silva Moreira",
    author_email="pedrorenanmoreira@gmail.com",
    url="https://github.com/Pedrordsm/FastAPI_learn.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)