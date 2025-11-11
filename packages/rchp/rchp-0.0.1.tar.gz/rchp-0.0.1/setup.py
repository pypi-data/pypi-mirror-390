from setuptools import setup, find_packages,Extension
import pybind11
import os
project_root = os.path.abspath(os.path.dirname(__file__))
ext_module = Extension(
    "core",
    sources=["rchp/core.cc"],
    include_dirs=[pybind11.get_include()],
    language="c++",
    extra_compile_args=["/std:c++23", "/O2","/utf-8"],
)
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="rchp",
    version="0.0.1",
    packages=find_packages(),
    author="enstarep",
    author_email="enstarep@rncyk.org",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    readme = "README.md",
    url="https://github.com/enstarep/rchp",
    ext_modules=[ext_module],
    python_requires='>=3.10',
)