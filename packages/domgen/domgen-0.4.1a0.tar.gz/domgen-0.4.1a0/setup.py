import setuptools

import dom

with open("README.md", "r") as file:
    long_description = file.read()

setuptools.setup(
    name="domgen",
    version=dom.__version__,
    author="Starwort",
    description="A package for generating HTML and CSS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Starwort/domgen",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={},
)
