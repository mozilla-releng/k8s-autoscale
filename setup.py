#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("version.txt") as f:
    version = f.read().rstrip()

with open("requirements/base.in") as f:
    install_requires = f.readlines()

setup(
    author="Rail Aliiev",
    author_email="rail@mozilla.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)"
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Autoscale scriptworkers in Kubernetes",
    install_requires=install_requires,
    license="MPL2.0",
    long_description=readme,
    include_package_data=True,
    keywords="k8s-autoscale",
    name="k8s_autoscale",
    packages=find_packages(),
    test_suite="tests",
    url="https://github.com/mozilla-releng/k8s-autoscale",
    version=version,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "k8s_autoscale=k8s_autoscale.cli:main",
            "k8s_autoscale-verify=k8s_autoscale.cli:verify",
        ],
    },
)
