from setuptools import setup, find_packages

setup(
    name="crystalwindow",        # this is the name ppl will pip install
    version="2.9.8",                # update when u change stuff
    packages=find_packages(include=["crystalwindow", "crystalwindow.*"]),
    include_package_data=True,
    install_requires=["pygame>=2.3.0"],
    author="CrystalBallyHereXD",
    author_email="mavilla.519@gmail.com",
    description="Easier Pygame!, Made by Crystal!!",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.1',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
