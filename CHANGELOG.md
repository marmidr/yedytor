# Changelog

See the [keepachangelog.com description](https://keepachangelog.com/en/1.0.0/).

## 1.1.1 - 2024-12-06

* Added
* Changed
* Deprecated
* Removed
* Fixed
  * Components editor - fixed filtering (always update Alias field)

## 1.1.0 - 2024-10-26

* Added
  * PnP editor - editor header row
  * PnP editor - new column "Description", added to the output CSV
  * DB editor - messagebox reminding that changed component attributes (alias, hidden) must be saved
* Changed
  * components LRU -> MRU
  * MRU list is kept in the `db/mru.csv`
  * PnP editor - MRU in dropdown list updated after new component was selected
* Deprecated
* Removed
* Fixed
  * while saving the new CSV file, error are catched (eg. "Permission denied")

## 1.0.3 - 2024-10-12

* Added
* Changed
  * use logger module from Boomer - logs to both console and the file
* Deprecated
* Removed
* Fixed

## 1.0.2 - 2024-10-11

* Added
  * logs/ folder for Python logger output
* Changed
* Deprecated
* Removed
* Fixed

## 1.0.1 - 2024-05-11

* Added
  * PnP editor - LRU items separated from other items in drop-down menu
  * LRU list is, on app load, cleaned up from components that are no longer existing or hidden
* Changed
  * PnP editor context menu: "Apply value as an items filter" -> "Update drop-down items (apply filter)"
* Deprecated
* Removed
* Fixed
  * PnP editor - LRU list saving to the CSV file

## 1.0.0 - 2024-05-08

* Added
  * keeps the list of recently used components for given footprint+comment filter
    * components from the LRU list are on the top of of the dropdown combobox list
    * list is kept in the `db/lru.csv`
* Changed
* Deprecated
* Removed
* Fixed

## 0.9.0 - 2024-04-29

* Added
  * support for DevLibEd2.Lib file format
  * support for Non-UTF encoding in Yamaha DevLib components library
  * keep the recent secondary PnP file path in the configuration file
  * ; separated component aliases
  * entry widget with placeholder text (hint)
* Changed
  * components CSV database now uses UTF-8 encoding
  * components DB update: now the new components are added to existing DB,
    instead of replacing the existing DB with a new one
  * components editor uses font size according to the user preferences
* Deprecated
* Removed
* Fixed

## 0.8.3 - 2024-04-02

* Added
  * on project opening/restoring wip: reset the PnP preview 1st row value to 1
  * component matching: cache results (270 items: 21s -> 8s)
  * PnP preview: progress bar for editor preparation progress
* Changed
* Deprecated
* Removed
* Fixed
  * opening a two-file project

## 0.8.2 - 2024-03-23

* Added
* Changed
  * yedytor.ini saved as UTF-8
* Deprecated
* Removed
* Fixed
  * saving edited file to a new CSV
  * multiprocessing disabled due to problems with some files
  * when loading a small project, percents in console does not cross a 100%

## 0.8.1 - 2024-03-23

* Added
  * Option: colorful logs in the console/CMD
  * PnP editor: filter created for "CAPC0805(2012)100_L | 100nF" (unknown footprint):
    * was: "100nf"
    * now: "0805 100nf"
* Changed
* Deprecated
* Removed
* Fixed
  * if WiP file loaded and no original PnP file exists,
    edited CSV is saved in the location of the loaded WiP file
  * number in XLS written as 1.00 is treated as text, not number;
    parser tries to detect such a situations and convert the value to int
  * component matching fixed for records where footprint is empty

## 0.8.0 - 2024-03-22

* Added
  * PnP editor: ComboBox for Rotation
* Changed
  * component filter: happy to have 2 characters, not 3
* Deprecated
* Removed
* Fixed

## 0.7.1 - 2024-03-07

* Added
  * PnP editor: CbxDropdown list recreated for WiP
* Changed
  * use multiprocessing for faster component matching during PnP editor creation
* Deprecated
* Removed
* Fixed
  * Application title is updated when WiP file is loaded

## 0.7.0 - 2024-02-29

* Added
  * PnP editor: button to save Work In Progress;
    a JSON file is created in the folder the PnP file was loaded
* Changed
* Deprecated
* Removed
* Fixed

## 0.6.7 - 2024-02-23

* Added
  * PnP editor: remove component by marking it black (will be skipped when writing the output CSV file)
* Changed
* Deprecated
* Removed
* Fixed
  * ODS reader - take the "repeated" cell atrribute into account when iterating row's cells

## 0.6.6 - 2023-11-26

* Added
* Changed
  * DB Editor: prints the path where the DB is saved
* Deprecated
* Removed
* Fixed
  * PnP column selector: fix for new document cases (no previous column indexes available)

## 0.6.5 - 2023-11-25

* Added
  * CSV reader: detect if ' is used as a quote char instead of "
* Changed
  * PnP editor is not reloaded when PnP file (Preview) is reloaded;
    Click the "Go to editor" to reload editor
* Deprecated
* Removed
* Fixed
  * PnP column selector: improved support for optional Layer column

## 0.6.4 - 2023-11-24

* Added
  * DB components: scroll list to the top when searching by name
* Changed
* Deprecated
* Removed
* Fixed

## 0.6.3 - 2023-10-23

* Added
  * App title - edited PnP file path
  * popups are centered on main App window
  * PnP editor - PPM: Set default
* Changed
* Deprecated
* Removed
* Fixed
  * keeps First Row number after loading another PnP file

## 0.6.2 - 2023-10-20

* Added
  * PnP preview - print progress on terminal while preparing the editor
  * PnP editor - PPM: Force apply selection to all matching components (replaces selection even if already manual selected)
  * PnP editor - PPM: Filter the ComboBox items (just like the Enter key)
  * PnP editor - PPM: Apply to all matching... adds a new component to the database, if needed
  * All Entry widgets with PopupMenu
  * PnP editor - new column showing that the component name is too long
* Changed
* Deprecated
* Removed
* Fixed

## 0.6.1 - 2023-10-14

* Added
  * Column selector - stores selections per file, restore last selection if the same file is opened
  * PnP editor - Popup menu (Copy/Cut/Paste/Select)
  * PnP editor - PPM: apply selection to all matching components
* Changed
* Deprecated
* Removed
* Fixed
  * after coponent scanner finished work, the DB components view is reloaded

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
