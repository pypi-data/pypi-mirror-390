from setuptools import setup, find_packages

setup(
    name="animepixels",
    version="2.0.1",
    author="Manas",
    author_email="manaskhurana90@gmail.com",
    description="Python wrapper for the AnimePixels API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Manaskhurana",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
