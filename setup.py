import os
import shutil
import setuptools

setuptools.setup(
    name='parsyc',
    version='1.0',
    author="Mustafa Quraish",
    license="MIT",
    author_email="mustafa@cs.toronto.edu",
    description="A Haskell/Parsec inspired Parser Combinator library",
    url="https://github.com/mustafaquraish/marker",
    packages=setuptools.find_packages(),
    py_modules=[
        'parsyc'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
