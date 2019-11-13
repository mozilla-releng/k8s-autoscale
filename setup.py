#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from glob import glob
from os.path import abspath, basename, dirname, join, splitext

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("version.txt") as f:
    version = f.read().rstrip()

here = abspath(dirname(__file__))
# We're using a pip8 style requirements file, which allows us to embed hashes
# of the packages in it. However, setuptools doesn't support parsing this type
# of file, so we need to strip those out before passing the requirements along
# to it.
with open(join(here, "requirements", "base.txt")) as f:
    requirements = []
    for line in f:
        # Skip empty and comment lines
        if not line.strip() or line.strip().startswith("#"):
            continue
        # Skip lines with hash values
        if not line.strip().startswith("--"):
            requirements.append(line.split(";")[0].split()[0])
            requirement_without_python_filter = line.split(";")[0]
            requirement_without_trailing_characters = requirement_without_python_filter.split()[0]

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
    install_requires=requirements,
    license="MPL2.0",
    long_description=readme,
    include_package_data=True,
    keywords="k8s-autoscale",
    name="k8s_autoscale",
    packages=find_packages("src"),
    package_dir={"": "src"},
    test_suite="tests",
    url="https://github.com/mozilla-releng/k8s-autoscale",
    version=version,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "k8s_autoscale=k8s_autoscale.cli:main",
            "k8s_autoscale-verify=k8s_autoscale.cli:verify",
        ]
    },
)
