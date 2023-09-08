import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "Yedytor",
    version = "0.4.2",
    author = "Mariusz Midor",
    author_email = "",
    description = "PnP files editor, using a footprints defined in the Yamaha .Tou files.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/marmidr/yedytor",
    project_urls = {
        "Bug Tracker": "package issues URL",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.9",
    install_requires=['xlrd', 'openpyxl', 'odfpy', 'customtkinter', 'requests', 'pillow', 'natsort']
)
