from setuptools import setup, find_packages

setup(
    name="atlas-runtime",
    version="0.1.0",
    packages=find_packages(include=["atlas_runtime", "atlas_runtime.*"]),
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "tiktoken>=0.5.0",
    ],
    entry_points={
        "console_scripts": [
            "atlas=atlas_runtime.cli:cli",
        ],
    },
)
