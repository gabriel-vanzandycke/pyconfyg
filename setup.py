from setuptools import setup, find_packages

setup(
    name='pyconfyg',
    author='Gabriel Van Zandycke',
    author_email="gabriel.vanzandycke@hotmail.com",
    url="https://github.com/gabriel-vanzandycke/pyconfyg",
    licence="LGPL",
    python_requires='>=3.8',
    description="My configuration framework",
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        "astunparse",
    ],
)
