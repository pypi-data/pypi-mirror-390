from setuptools import setup, find_packages

setup(
    name="exsite",
    version="1.0.1",
    author="Tm",
    description="A simple offline site builder for Android and PC (no server needed)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/exsite/",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)