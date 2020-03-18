import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bnfparser",
    version="0.1.0",
    author="biowpn",
    description="A simple BNF parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biowpn/bnfparser",
    packages=setuptools.find_packages()
)
