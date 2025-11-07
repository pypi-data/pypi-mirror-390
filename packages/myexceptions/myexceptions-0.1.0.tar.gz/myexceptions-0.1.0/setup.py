from setuptools import find_packages, setup

with open("app/README.md", "r") as f:
    long_description = f.read()

setup(
    name="exceptions",
    version="0.0.1",
    description="Exception classes",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    author="abrun",
    install_requires={},
    extras_require={},
    python_requires=">=3.10",
)
