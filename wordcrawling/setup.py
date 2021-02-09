"""https://setuptools.readthedocs.io/en/latest/setuptools.html

how to clear pip-egg-info
"""
import setuptools


#! command errored out with exit status 1...
# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="wordcrawling", # Replace with your own username. no upper case? x
    version="0.0.1",
    author="wbfw109",
    author_email="wbfw109@gmail.com",
    description="A small test package",
    long_description="...",
    long_description_content_type="text/markdown",
    url="https://github.com/test",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
