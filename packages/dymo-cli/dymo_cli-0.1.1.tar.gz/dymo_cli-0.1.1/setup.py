from setuptools import setup, find_packages

setup(
    name="dymo-cli",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "rich",
        "prompt_toolkit",
        "requests",
        "dymoapi"
    ],
    entry_points={
        "console_scripts": [
            "dymo-cli=dymo_cli.cli:main"
        ]
    }
)