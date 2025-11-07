from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="ipaytools",
    version="0.3.4",
    author="Benny Harianto",
    author_email="creatoropensource@gmail.com",
    description="Python SDK for iPayTools - Ethereum smart contract integration with BRICS multi-currency support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bennyharianto/ipaytools-python",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ipaytools-demo=ipaytools.core:quick_start_demo",
        ],
    },
)
