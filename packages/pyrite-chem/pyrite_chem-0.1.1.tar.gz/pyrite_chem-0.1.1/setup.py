from setuptools import setup, find_packages

setup(
    name="pyrite_chem",                # must match the name in pyproject.toml
    version="0.1.1",
    description="Pyrite: utilities for molecular docking",
    author="Daan_Geerke_Lab",
    license="MIT",
    packages=find_packages(include=["pyrite", "pyrite.*"]),
    python_requires=">=3.10",
    install_requires=[
        # list dependencies if any, for example:
        # "numpy>=1.26",
        # "pandas>=2.0",
    ],
    include_package_data=True,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tcobanoglu/Pyrite",
    project_urls={
        "Bug Tracker": "https://github.com/tcobanoglu/Pyrite/issues",
    },
)
