from setuptools import setup, find_packages

setup(
    name="goonman",
    version="0.1.0",
    description="gooners library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="imagoodmanloll",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    install_requires=[],
)
