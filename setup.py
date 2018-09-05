#-*- coding: utf-8 -*-
import re
from distutils.core import setup
import setuptools

def version():
    verstrline = open('inapp_purchases/__init__.py', "rt").read()
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
    # Application name
    name='inapp-purchases',

    # Version number
    version=version(),

    # Application author details
    author='Adán Mauri Ungaro',
    author_email='adan.mauri@gmail.com',

    # Licence
    license='Apache License Version 2.0',

    # Packages
    packages=setuptools.find_packages(),

    # Details
    url='https://github.com/adanmauri/inapp-purchases.git',
    description='Manage in-app purchases for Apple AppStore and Google Play',
    long_description=long_description(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords=('python in-app payment payments purchase purchases google play apple '
              'appstore iphone android '),

    # Dependent packages
    install_requires=requirements(),
)
