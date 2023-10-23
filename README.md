# Yedytor

PnP files editor, using a footprints defined in the Yamaha .Tou files.

![ss2](doc/sshot2.png)
![ss3](doc/sshot3.png)
![ss4](doc/sshot4.png)
![ss5](doc/sshot5.png)

## Supported formats

* Yamaha project file
  * .Tou
  * DevLibEd.Lib
* [PnP](. "Pick And Place")
  * .xls
  * .xlsx
  * .ods
  * any other extension - considered as a CSV file

> NOTE
>
> If xls/xlsx/ods file contains several sheets, only the first one will be used.

## Prerequisites

### Python

[Python for Windows with addons](https://www.python.org/).
Remember to check these options:

* pip
* tcl\tk
* Add Python to environment variables

Minimum required version is **Python 3.9**.

### Libraries

To install required libraries, open the PowerShell and:

```ps1
# .xls reader, .xlsx reader, .ods reader, UI lib, http requests, image formats, natural sorting,
pip install xlrd openpyxl odfpy customtkinter requests pillow natsort
```

## How to run

From PowerShell:

```ps1
python.exe src/app.py
```

To get colored logs, use Linux-like terminal, eg. [MSys2](msys2.org/), but still using the Windows installation of the Python:

```sh
$ /c/Program\ Files/Python39/python.exe src/app.py
```

![msys2con](doc/msys2-console.png)

## Trouble shooting

* *ModuleNotFoundError: No module named 'tkinter'*

  `tkinter` was not installed together with the Python -
  follow the instructions [here](https://bobbyhadz.com/blog/python-no-module-named-tkinter).
* *ERROR: Cannot load BOM: 'utf-8' codec can't decode byte*

  Only UTF-8 files are accepted; if the BOM or PnP file uses ANSI or WINDOWS encoding, use `Notepad++` or other editor to change the encoding to UTF-8
*
