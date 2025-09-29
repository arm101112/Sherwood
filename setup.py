from setuptools import setup, find_packages

setup(
    name="sherwood",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
)
