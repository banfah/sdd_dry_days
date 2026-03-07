from setuptools import setup, find_packages

setup(
    name="sdd-dry-days",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sdd=sdd_dry_days.__main__:main",
        ],
    },
    python_requires=">=3.8",
)