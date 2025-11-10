from setuptools import setup, find_packages

setup(
    name="vizpot",
    version="0.1.2",
    description="Collection of visualization notebooks",
    packages=find_packages(),
    include_package_data=True,
    package_data={"vizpot": ["**/*.ipynb"]},
)
