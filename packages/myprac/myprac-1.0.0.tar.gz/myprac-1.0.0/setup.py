from setuptools import setup, find_packages

setup(
    name="myprac",                        # must be unique on PyPI
    version="1.0.0",
    author="Mine",
    author_email="your_email@example.com",
    description="A Python library containing 5 AI & DS practical programs.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
)
