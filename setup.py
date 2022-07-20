import os

from setuptools import find_packages, setup

version = "0.1"

try:
    readme = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()
except:
    readme = ""

install_requires = []

extras_require = []

tests_require = [
    "pytest",
    "pytest-cov",
    "pytest-pythonpath",
    "tox",
]

setup(
    name="anysearch",
    version=version,
    description="Elasticsearch and OpenSearch compatibility library.",
    long_description=readme,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/barseghyanartur/anysearch/issues",
        "Documentation": "https://anysearch.readthedocs.io/",
        "Source Code": "https://github.com/barseghyanartur/anysearch/",
        "Changelog": "https://anysearch.readthedocs.io/"
        "en/latest/changelog.html",
    },
    keywords="django, elasticsearch, elasticsearch-dsl, opensearch, "
    "opensearch-dsl",
    author="Artur Barseghyan",
    author_email="artur.barseghyan@gmail.com",
    url="https://github.com/barseghyanartur/anysearch/",
    py_modules=["anysearch"],
    license="MIT",
    python_requires=">=3.7",
    install_requires=(install_requires + extras_require),
    tests_require=tests_require,
    include_package_data=True,
)
