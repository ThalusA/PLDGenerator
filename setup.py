import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pld-generator",
    version="0.0.1",
    author="Alexandre MONIER",
    author_email="alexandre.monier@epitech.eu",
    description="A Project Log Document Generator for Epitech",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ThalusA/PLDGenerator",
    project_urls={
        "Bug Tracker": "https://github.com/ThalusA/PLDGenerator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)