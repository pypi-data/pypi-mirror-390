#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = []

test_requirements = [
    "pytest>=3",
]

pkg_vars = {}

with open("scim_client/_version.py") as f:
    exec(f.read(), pkg_vars)

setup(
    author="Mitratech Development Team",
    author_email="devs@mitratech.com",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    description="SCIM v2 API client",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="scim_client",
    name="scim_client",
    packages=find_packages(include=["scim_client", "scim_client.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/Aplopio/python-scim-client",
    version=pkg_vars["__version__"],
    zip_safe=False,
)
