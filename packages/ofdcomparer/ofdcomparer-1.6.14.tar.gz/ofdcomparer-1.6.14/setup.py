from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ofdcomparer",
    version="1.6.14",
    long_description=long_description,
    description="Библиотека для сравнивания ФД из ФН и ОФД",
    packages=["ofdcomparer"],
    author_email="k.kabisova@atol.ru",
    install_requires=[
        "requests>=2.31.0",
        "requests-toolbelt>=1.0.0",
        "urllib3>=2.0.6",
        "zipp>=3.17.0",
    ],
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
