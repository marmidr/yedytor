import setuptools
import sys

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

sys.path.append('')
import yedytor

setuptools.setup(
    name = "yedytor",
    version = "1",
    # version = yedytor.app.VERSION,
    author = "Mariusz Midor",
    description = "PnP files editor, using a footprints defined in the Yamaha .Tou files.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/marmidr/yedytor",
    project_urls = {
        "Documentation": "https://github.com/marmidr/yedytor",
        "Source": "https://github.com/marmidr/yedytor",
        "Tracker": "https://github.com/marmidr/yedytor/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    py_modules=['yedytor.__main__'],
    python_requires = ">=3.9",
    install_requires=['xlrd', 'openpyxl', 'odfpy', 'customtkinter', 'requests', 'pillow', 'natsort']
)
