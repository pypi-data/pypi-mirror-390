from setuptools import setup, find_packages

setup(
    name="crystalwindow",        # this is the name ppl will pip install
    version="1.8",                # update when u change stuff
    packages=find_packages(include=["CrystalWindow", "CrystalWindow.*"]),
    include_package_data=True,
    install_requires=["pygame>=2.3.0"],  # cuz ur lib uses pygame
    author="CrystalBallyHereXD",
    description="Easier Pygame!, Made by Crystal!!",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.1',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
