#-*- coding: utf-8 -*-
import re
import setuptools

from distutils.core import setup

def version():
    verstrline = open('python_in_app_payments/__init__.py', "rt").read()
    mob = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", verstrline, re.M)
    if mob:
        return mob.group(1)
    else:
        raise RuntimeError("Unable to find version string")

def requirements():
    return open('requirements.txt', "rt").read().splitlines()

def long_description():
    with open("README.md", "r") as readme_file:
        return readme_file.read()

setup(
    name='python-in-app-payments',
    version=version(),
    author='Adán Mauri Ungaro',
    author_email='adan.mauri@gmail.com',
    description='Python in-app payment validator for Apple AppStore and Google Play',
    long_description=long_description(),
    long_description_content_type="text/markdown",
    url='https://github.com/adanmauri/python-in-app-payments.git',
    packages=setuptools.find_packages(),
    license='Apache License Version 2.0',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
