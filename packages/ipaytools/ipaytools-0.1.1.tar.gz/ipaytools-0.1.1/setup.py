from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ipaytools",
    version="0.1.1",  # ⬅️ Naikkan version
    author="Benny Harianto",
    author_email="creatoropensource@gmail.com", 
    description="Python SDK for iPayTools - Ethereum smart contract integration for payment processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bennyharianto/ipaytools-python",  # ⬅️ Ganti dengan repo Anda
    project_urls={
        "Bug Tracker": "https://github.com/bennyharianto/ipaytools-python/issues",
        "Documentation": "https://github.com/bennyharianto/ipaytools-python#readme",
        "Source Code": "https://github.com/bennyharianto/ipaytools-python",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry", 
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=["web3>=6.0.0"],
    keywords=[
        "ethereum",
        "web3", 
        "smart-contract",
        "blockchain",
        "payments",
        "defi",
        "ipaytools",
    ],
)
