from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ipaytools",
    version="0.1.0",
    author="iPayTools Team",
    author_email="team@ipaytools.com",
    description="Python SDK for iPayTools - Ethereum smart contract integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ipaytools/ipaytools-python",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=["web3>=6.0.0"],
)
