# Changelog

See the [keepachangelog.com description](https://keepachangelog.com/en/1.0.0/).

## 0.6.1 - 2023-10-13

* Added
  * Column selector - stores selections per file, restore last selection if the same file is opened
* Changed
* Deprecated
* Removed
* Fixed
  * after coponent scanner finished work, the db components view is reloaded

## 0.6.0 - 2023-10-12

* Added
  * added component scanner for DevLibEd.Lib file
* Changed
* Deprecated
* Removed
* Fixed

## 0.5.2 - 2023-10-12

* Added
* Changed
  * output document: extra empty column between original and added columns
* Deprecated
* Removed
* Fixed
  * XLS reader does not convert 0603 string to 603 number

## 0.5.1 - 2023-10-11

* Added
* Changed
  * output document: original document columns + yamaha-expected columns
* Deprecated
* Removed
* Fixed

## 0.5.0 - 2023-10-09

* Added
  * DB components editor - filter
  * Columns editor - select all columns required in the output document
* Changed
  * in PnP editor, show component ID instead of record index
  * output document is no longer a mirror if input, but a set of user-selected columns
* Deprecated
* Removed
* Fixed

## 0.4.2 - 2023-09-07

* Added
  * in case of the output file encoding exception, saving the output will continue with the remaining rows
  * history:
    * keeps the last opened PnP file
    * keeps the Tou files folder
* Changed
  * updated README and screenshots
* Deprecated
* Removed
* Fixed
  * encoding problem when writing output CSV file

## 0.4.1 - 2023-09-05

* Added
  * yedytor.in config file
  * PnP editor: font size 12px or 16px
* Changed
  * PnP editor: dropdown background color set to light blue to distinguish it from the background
  * PnP editor: set edited item font weight=Bold to distinguish it among the others
  * PnP editor: if filtered components returned 0 items, the filter is removed and full components list is restored
  * Tou scanner: items are now sorted naturally (like in Excel), not alphabetically
* Deprecated
* Removed
* Fixed

## 0.4.0 - 2023-09-02

* Added
  * PnP editor: after manual selection, the component is appliet to all items where Comment and Footprint matches the current item
  * PnP editor: item details order changed to: <index> | <footprint> | <comment>
  * PnP editor: automatically select component if "<footprint>_<comment>" found
  * PnP editor: components list narrowing: enter "603" for footprint or "603 10k" for better match
  * PnP editor: colored items: lime->matched automatically, green->selected manually
  * PnP editor: each combobox is assigned filtered list of all components upon loading
  * PnP editor: progress bar - how many items have aleady selected a PnP component
  * PnP editor: before saving, check if all items are set
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
