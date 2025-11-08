
import setuptools

setuptools.setup() (
    name="srinipdf",
    version=1.0,
    long_description=open("README.md").read(),
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
)