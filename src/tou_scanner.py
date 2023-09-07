import customtkinter
import tkinter
import logging
import typing
import os
import time
import natsort

import ui_helpers
from tou_reader import TouFile
from components import ComponentsDB
from config import Config

# -----------------------------------------------------------------------------

class TouScanner(customtkinter.CTkToplevel):
    TAB_SCAN_RESULTS = "Scan results"
    TAB_COMPONENTS = "Components"

    def __init__(self, *args, **kwargs):
        """
        callback=typing.Callable[[str, ComponentDB], None] - function receiving "y", "n", "o", "c"
        """
        assert "callback" in kwargs
        self.callback: typing.Callable[[str, ComponentsDB], None] = kwargs.pop("callback")

        super().__init__(*args, **kwargs)
        self.geometry("700x600")

        self.components_dict: dict[str, set[str]] = {}

        #
        self.btn_browse = customtkinter.CTkButton(self, text="Browse...", command=self.button_browse_event)
        self.btn_browse.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        self.entry_tou_folder = customtkinter.CTkEntry(self, placeholder_text="Yamaha *.Tou files folder")
        self.entry_tou_folder.grid(row=1, column=1, pady=5, padx=5, columnspan=2, sticky="we")

        #
        self.btn_scan = customtkinter.CTkButton(self, text="S C A N", command=self.button_scan_event)
        self.btn_scan.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.btn_scan.configure(state=tkinter.DISABLED)

        self.prgrbar_scan = customtkinter.CTkProgressBar(self)
        self.prgrbar_scan.grid(row=2, column=1, pady=5, padx=5, columnspan=2, sticky="we")
        self.prgrbar_scan.set(0)

        self.lbl_scan_time = customtkinter.CTkLabel(self, text="Took: 0s")
        self.lbl_scan_time.grid(row=2, column=3, pady=5, padx=5, sticky="we")

        #
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="wens")

        #
        tab_scan_results = self.tabview.add(self.TAB_SCAN_RESULTS)
        tab_scan_results.grid_columnconfigure(0, weight=1)
        tab_scan_results.grid_rowconfigure(0, weight=1)
        self.textbox_scanresult = customtkinter.CTkTextbox(tab_scan_results,
                                                font=customtkinter.CTkFont(size=13, family="Consolas"),
                                                activate_scrollbars=True,
                                                wrap='none')
        self.textbox_scanresult.grid(row=0, column=0, padx=5, pady=5, sticky="wens")

        #
        tab_components = self.tabview.add(self.TAB_COMPONENTS)
        tab_components.grid_columnconfigure(0, weight=1)
        tab_components.grid_rowconfigure(0, weight=1)
        self.textbox_components = customtkinter.CTkTextbox(tab_components,
                                                font=customtkinter.CTkFont(size=12, family="Consolas"),
                                                activate_scrollbars=True,
                                                wrap='none')
        self.textbox_components.grid(row=0, column=0, padx=5, pady=5, sticky="wens")

        self.btn_savecomponents = customtkinter.CTkButton(tab_components,
                                                          text="Save components as CSV...",
                                                          command=self.btn_savecomponents_event)
        self.btn_savecomponents.grid(row=1, column=0, pady=2, padx=5, sticky="e")

        #
        sep_h = tkinter.ttk.Separator(self, orient='horizontal')
        sep_h.grid(row=4, column=0, columnspan=4, pady=1, padx=5, sticky="we",)

        self.btn_ok = customtkinter.CTkButton(self, text="Save new components to DB", command=self.button_ok_event)
        self.btn_ok.grid(row=5, column=1, pady=5, padx=5, sticky="we")
        self.btn_ok.configure(state=tkinter.DISABLED)

        self.btn_cancel = customtkinter.CTkButton(self, text="Cancel", command=self.button_cancel_event)
        self.btn_cancel.grid(row=5, column=2, pady=5, padx=5, sticky="we")

        #
        sizegrip = tkinter.ttk.Sizegrip(self)
        sizegrip.grid(row=5, column=3, pady=3, padx=3, sticky="es")

        #
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

        #
        tou_folder = Config.instance().tou_directory_path
        if os.path.isdir(tou_folder):
            self.btn_scan.configure(state=tkinter.NORMAL)
            ui_helpers.entry_set_text(self.entry_tou_folder, tou_folder)

    def button_ok_event(self):
        logging.debug("Ok")

        if self.components_dict:
            # make DB from self.components_dict
            components = ComponentsDB(components_dict=self.components_dict)
            self.callback("o", components)
        else:
            self.callback("c", None)
        self.destroy()

    def button_cancel_event(self):
        logging.debug("Cancel")
        self.callback("c", None)
        self.destroy()

    def btn_savecomponents_event(self):
        if self.components_dict:
            logging.debug("Saving an CSV")
            self.attributes('-topmost', False)
            file = tkinter.filedialog.asksaveasfile(
                    title="Save components in a CSV file",
                    initialdir=None,
                    filetypes = [("Comma separated values", ".csv")],
                    defaultextension = ".csv"
                )
            if file:
                # sort naturally: https://pypi.org/project/natsort/
                components_keys_sorted = natsort.natsorted(list(self.components_dict))

                for component_key in components_keys_sorted:
                    components_str = ""
                    for cmp_name in self.components_dict[component_key]:
                        components_str += cmp_name + ";"
                    components_str += "\n"
                    file.write(components_str)

            self.attributes('-topmost', True)

    def button_browse_event(self):
        # https://docs.python.org/3/library/dialog.html
        self.attributes('-topmost', False)
        tou_folder = tkinter.filedialog.askdirectory(
            title="Select Yamaha *.Tou files folder",
            mustexist=True,
            initialdir=None,
        )
        self.attributes('-topmost', True)
        logging.info(f"Selected folder: {tou_folder}")
        ui_helpers.entry_set_text(self.entry_tou_folder, tou_folder)
        self.btn_scan.configure(state=tkinter.NORMAL)
        Config.instance().tou_directory_path = tou_folder
        Config.instance().save()

    def button_scan_event(self):
        self.scan_folder()

    def scan_folder(self):
        self.prgrbar_scan.set(0)
        self.textbox_scanresult.delete("0.0", tkinter.END)
        self.textbox_components.delete("0.0", tkinter.END)
        self.lbl_scan_time.configure(text="?s")
        self.tabview.set(self.TAB_SCAN_RESULTS)
        started_at = time.monotonic()

        try:
            self.btn_scan.configure(state=tkinter.DISABLED)
            tou_folder = self.entry_tou_folder.get()
            tou_filenames = []
            tou_longest_filename = 0

            for de in os.scandir(tou_folder):
                if de.name.endswith(".Tou"):
                    tou_filenames.append(de.name)
                    tou_longest_filename = max(tou_longest_filename, len(de.name))

            if len(tou_filenames):
                logging.info(f"Scanning {len(tou_filenames)} files in {tou_folder}")
                tou_files: list[TouFile] = []

                for i, tou_fname in enumerate(tou_filenames):
                    tou = TouFile(os.path.join(tou_folder, tou_fname))
                    logging.debug(f"  {tou_fname} -> {len(tou.items)} items")
                    tou_files.append(tou)
                    self.prgrbar_scan.set((i+1) / len(tou_filenames))
                    self.update()
                    time.sleep(0.01) # for effect only :)

                delta = time.monotonic() - started_at
                self.btn_ok.configure(state=tkinter.NORMAL)
                self.scan_report(tou_files, tou_longest_filename)
                self.components_report(tou_files)
        except Exception as e:
            delta = 0
            logging.error(f"Error occured: {e}")
        finally:
            delta = f"{delta:.03f}s"
            logging.info(f"{len(tou_filenames)} files scanned in {delta}")
            self.lbl_scan_time.configure(text=delta)
            self.btn_scan.configure(state=tkinter.NORMAL)

    def scan_report(self, tou_files: list[TouFile], tou_longest_filename: int):
        tou_files_report = ""
        for i, tf in enumerate(tou_files):
            spacing = " " * (tou_longest_filename - len(tf.file_name))
            tou_files_report += f"{(i+1):3}. {tf.file_name}{spacing} | {len(tf.items)} components\n"
        self.textbox_scanresult.insert("0.0", tou_files_report)

    def components_report(self, tou_files: list[TouFile]):
        logging.debug("Merge components from all Tou files")
        self.components_dict = {}

        for tf in tou_files:
            for key in tf.items:
                # make the items under each key unique thanks to the set{}
                if items := self.components_dict.get(key):
                    items |= set(tf.items[key])
                else:
                    self.components_dict[key] = set(tf.items[key])

        logging.debug("Prepare report")
        components_report = ""
        components_keys_sorted = list(self.components_dict)
        components_keys_sorted.sort()

        for i, component_key in enumerate(components_keys_sorted):
            components_str = f"{self.components_dict[component_key]}".strip("{}")
            components_report += f"{(i+1):3}. {components_str}\n"

        logging.info(f"Total {len(self.components_dict)} components")
        self.textbox_components.insert("0.0", components_report)
