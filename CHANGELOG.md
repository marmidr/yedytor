# Changelog

See the [keepachangelog.com description](https://keepachangelog.com/en/1.0.0/).

## 0.4.0 - 2023-09-02

* Added
  * PnP editor: after manual selection, the component is appliet to all items where Comment and Footprint matches the current item
  * PnP editor: item details order changed to: <index> | <footprint> | <comment>
* Changed
  * DB components editor redesigned - now it's able to handle even 10'000 elements
* Deprecated
* Removed
* Fixed

## 0.3.0 - 2023-08-16

* Added
  * keeping list of components in db/components__<date_time>.csv
  * DB info on home screen
  * PnP preview: columns selector
  * PnP preview: first row number entry
  * PnP editor: Value + Footprint | ComboBox with known Yamaha components (footprints)
  * PnP editor: saving as a new CSV
  * DB editor: list of the available components, ability to mark as 'Hidden'
* Changed
* Deprecated
* Removed
* Fixed
  * "db" folder correctly located no matter from where (cwd) the app was started
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
