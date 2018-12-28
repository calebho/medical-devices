import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="medical_devices",
    version="0.0.1",
    author="Caleb Ho",
    author_email="caleb.yh.ho@gmail.com",
    description="A package for reading medical devices data from the FDA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/calebho/medical-devices",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
