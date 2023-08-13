# Changelog

See the [keepachangelog.com description](https://keepachangelog.com/en/1.0.0/).

## 0.3.0 - 2023-08-14

* Added
  * keeping list of components in db/components__<date_time>.csv
  * DB info on home screen
* Changed
* Deprecated
* Removed
* Fixed
  * handle situation when user selects no file in SaveDialog

## 0.2.1 - 2023-08-02

* Added
  * saving components list as a CSV file
  * PnP columns selector
* Changed
* Deprecated
* Removed
* Fixed
  * extracted component name stripped on NUL character if occured in the middle:
    `'evo4<NUL>ucial_' -> 'evo4'`

## 0.2.0 - 2023-08-02

* Added
  * Yamaha files scanner window
  * .Tou files reader
* Changed
* Deprecated
* Removed
* Fixed

## 0.1.0 - 2023-07-31

* Added
  * application window build with customtkinter
  * PnP parser and preview from the Boomer project
* Changed
* Deprecated
* Removed
* Fixed
