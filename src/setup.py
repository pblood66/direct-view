from setuptools import setup

setup(
    name="dv",
    version="1.0.0",
    py_modules=["dv"],
    install_requires=["click"],
    entry_points={
        "console_scripts": [
            "dv=dv:cli",
        ],
    },
)