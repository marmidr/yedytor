# Yedytor
#
# PnP files editor, using a footprints defined in the Yamaha .Tou files.
#
# (c) 2023 Mariusz Midor
# https://github.com/marmidr/yedytor

import customtkinter
import tkinter
from tkinter import tix
import logging
import os
import configparser
import sys

import xls_reader
import xlsx_reader
import csv_reader
import ods_reader
import text_grid
import ui_helpers
import tou_scanner

from column_selector import ColumnsSelector, ColumnsSelectorResult
from msg_box import MessageBox
from tkhtmlview import HTMLLabel
from components import Component, ComponentsDB

# -----------------------------------------------------------------------------

APP_NAME = "Yedytor v0.3.0"

# -----------------------------------------------------------------------------

def get_db_directory() -> str:
    db_path = os.path.dirname(__file__)
    db_path = os.path.join(db_path, "..")
    db_path = os.path.abspath(db_path)
    db_path = os.path.join(db_path, "db")
    return db_path

# -----------------------------------------------------------------------------

class Project:
    CONFIG_FILE_NAME = "yedytor.ini"

    def __init__(self):
        self.pnp_path = "<pnp_fpath>"
        self.pnp2_path = ""
        self.pnp_separator = "SPACES"
        self.pnp_grid: text_grid.TextGrid = None
        self.pnp_grid_dirty = False
        self.pnp_footprint_col = 0
        self.pnp_comment_col = 0
        self.pnp_first_row = 0
        self.pnp_has_column_headers = False

        # https://docs.python.org/3/library/configparser.html
        self.__config = configparser.ConfigParser()

        if os.path.isfile(self.CONFIG_FILE_NAME):
            self.__config.read(self.CONFIG_FILE_NAME)
        else:
            self.__config['common'] = {
                "initial_dir": "",
            }

    def get_name(self) -> str:
        return os.path.basename(self.pnp_path)

    def cfg_get_section(self, sect_name: str) -> configparser.SectionProxy:
        try:
            self.__config[sect_name]
        except Exception:
            self.__config[sect_name] = {}

        return self.__config[sect_name]

    @staticmethod
    def get_separator_names() -> list[str]:
        return ["COMMA", "SEMICOLON", "TAB", "SPACES", "FIXED-WIDTH", "REGEX"].copy()

    @staticmethod
    def translate_separator(sep: str) -> str:
        if sep == "COMMA":
            return ","
        elif sep == "SEMICOLON":
            return ";"
        elif sep == "TAB":
            return "\t"
        elif sep == "SPACES":
            return "*sp"
        elif sep == "FIXED-WIDTH":
            return "*fw"
        elif sep == "REGEX":
            return "*re"
        else:
            raise RuntimeError("Unknown CSV separator")

    def get_pnp_delimiter(self) -> str:
        return self.translate_separator(self.pnp_separator)

    def load_from_file(self, path: str, path2: str):
        path_lower = path.lower()
        delim = self.get_pnp_delimiter()

        if path_lower.endswith("xls"):
            self.pnp_grid = xls_reader.read_xls_sheet(path)
        elif path_lower.endswith("xlsx"):
            self.pnp_grid = xlsx_reader.read_xlsx_sheet(path)
        elif path_lower.endswith("ods"):
            self.pnp_grid = ods_reader.read_ods_sheet(path)
        else: # assume CSV
            self.pnp_grid = csv_reader.read_csv(path, delim)

        log_f = logging.info if self.pnp_grid.nrows > 0 else logging.warning
        log_f(f"PnP: {self.pnp_grid.nrows} rows x {self.pnp_grid.ncols} cols")

        # load the optional second PnP file
        if path2 != "":
            path2_lower = path2.lower()

            if path2_lower.endswith("xls"):
                pnp2_grid = xls_reader.read_xls_sheet(path2)
            elif path2_lower.endswith("xlsx"):
                pnp2_grid = xlsx_reader.read_xlsx_sheet(path)
            elif path2_lower.endswith("ods"):
                pnp2_grid = ods_reader.read_ods_sheet(path2)
            else: # assume CSV
                pnp2_grid = csv_reader.read_csv(path2, delim)

            log_f = logging.info if pnp2_grid.nrows > 0 else logging.warning
            log_f("PnP2: {} rows x {} cols".format(pnp2_grid.nrows, pnp2_grid.ncols))

            # merge
            if pnp2_grid.ncols != proj.pnp_grid.ncols:
                raise ValueError("PnP has {} columns, but PnP2 has {} columns".format(
                    self.pnp_grid.ncols, pnp2_grid.ncols
                ))

            self.pnp_grid.nrows += pnp2_grid.nrows
            self.pnp_grid.rows_raw().extend(pnp2_grid.rows)

# global instance
proj = Project()
components = ComponentsDB()

# -----------------------------------------------------------------------------

class HomeFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        lbl_pnp_path = customtkinter.CTkLabel(self, text="PnP path:")
        lbl_pnp_path.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.var_pnp = customtkinter.StringVar(value="")
        self.entry_pnp_path = customtkinter.CTkEntry(self, textvariable=self.var_pnp)
        self.entry_pnp_path.grid(row=0, column=1, pady=5, padx=5, columnspan=2, sticky="we")
        self.entry_pnp_path.configure(state=tkinter.DISABLED)

        btn_browse = customtkinter.CTkButton(self, text="Browse...", command=self.button_browse_event)
        btn_browse.grid(row=0, column=3, pady=5, padx=5, sticky="e")

        #
        lbl_pnp2_path = customtkinter.CTkLabel(self, text="PnP2 (optional):")
        lbl_pnp2_path.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.var_pnp2 = customtkinter.StringVar(value="")
        self.entry_pnp2_path = customtkinter.CTkEntry(self, textvariable=self.var_pnp2)
        self.entry_pnp2_path.grid(row=2, column=1, pady=5, padx=5, sticky="we")
        self.entry_pnp2_path.configure(state=tkinter.DISABLED)

    def clear_previews(self):
        self.var_pnp.set("")
        self.var_pnp2.set("")
        self.pnp_view.clear_preview()

    def button_browse_event(self):
        logging.debug("Browse for PnP")
        self.clear_previews()

        # https://docs.python.org/3/library/dialog.html
        # TODO: get the initial dir from the proj settings
        pnp_paths = tkinter.filedialog.askopenfilenames(
            title="Select PnP file(s)",
            initialdir=None,
            filetypes = [
                ("All text files", ".*")
            ],
        )
        logging.info(f"Selected PnP(s): {pnp_paths}")

        if len(pnp_paths) > 2:
            mb = MessageBox(dialog_type="o", message="You can only select one or two PnP files of the same type", callback=lambda btn: btn)
            return
        elif len(pnp_paths) == 2:
            # https://docs.python.org/3/library/os.path.html#os.path.splitext
            ext1 = os.path.splitext(pnp_paths[0])[1].lower()
            ext2 = os.path.splitext(pnp_paths[1])[1].lower()
            if ext1 != ext2:
                mb = MessageBox(dialog_type="o", message="You must select two PnP files of the same type", callback=lambda btn: btn)
                return

        if len(pnp_paths) and os.path.isfile(pnp_paths[0]):
            try:
                # reset entire project
                global proj
                sep_backup = proj.pnp_separator
                proj = Project()

                proj.pnp_separator = sep_backup
                proj.pnp_path = pnp_paths[0]
                proj.pnp2_path = pnp_paths[1] if len(pnp_paths) > 1 else ""
                self.var_pnp.set(proj.pnp_path)
                self.var_pnp2.set(proj.pnp2_path)

                self.activate_csv_separator()
            except Exception as e:
                logging.error(f"Cannot open file: {e}")
        else:
            if len(pnp_paths):
                logging.error(f"Cannot access the file '{pnp_paths[0]}'")

    def activate_csv_separator(self):
        pnp_fname = proj.pnp_path.lower()
        if pnp_fname.endswith("xls") or pnp_fname.endswith("xlsx") or pnp_fname.endswith("ods"):
            self.pnp_config.opt_separator.configure(state=tkinter.DISABLED)
        else:
            self.pnp_config.opt_separator.configure(state=tkinter.NORMAL)

# -----------------------------------------------------------------------------

class PnPView(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.textbox = customtkinter.CTkTextbox(self,
                                                font=customtkinter.CTkFont(size=12, family="Consolas"),
                                                activate_scrollbars=True,
                                                wrap='none')
        self.textbox.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.entry_search = customtkinter.CTkEntry(self, placeholder_text="search...")
        self.entry_search.grid(row=1, column=0, padx=5, pady=5, sticky="wens")

        self.btn_search = customtkinter.CTkButton(self, text="Find", command=self.button_find_event)
        self.btn_search.grid(row=1, column=1, pady=5, padx=5, sticky="we")

        self.lbl_occurences = customtkinter.CTkLabel(self, text="Found: 0")
        self.lbl_occurences.grid(row=1, column=2, pady=5, padx=5, sticky="")

    def load_pnp(self, path: str, path2: str):
        self.clear_preview()

        if not os.path.isfile(path):
            raise FileNotFoundError(f"File '{path}' does not exists")

        # check if optional second PnP file exists
        if path2 != "" and not os.path.isfile(path2):
            raise FileNotFoundError(f"File '{path2}' does not exists")

        proj.load_from_file(path, path2)
        pnp_txt_grid = proj.pnp_grid.format_grid(proj.pnp_first_row)
        self.textbox.insert("0.0", pnp_txt_grid)
        proj.pnp_grid_dirty = False
        # refresh editor (if columns were selected)
        if proj.pnp_footprint_col > 0 or proj.pnp_comment_col > 0:
            self.pnp_editor.load()

    def clear_preview(self):
        self.textbox.delete("0.0", tkinter.END)

    def button_find_event(self):
        txt = self.entry_search.get()
        logging.info(f"Find '{txt}'")
        cnt = ui_helpers.textbox_find_text(self.textbox, txt)
        self.lbl_occurences.configure(text=f"Found: {cnt}")

# -----------------------------------------------------------------------------

class PnPConfig(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "pnp_view" in kwargs
        self.pnp_view: PnPView = kwargs.pop("pnp_view")
        assert isinstance(self.pnp_view, PnPView)

        super().__init__(master, **kwargs)

        # initial value
        self.column_selector = None

        #
        lbl_separator = customtkinter.CTkLabel(self, text="CSV\nSeparator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        self.opt_separator_var = customtkinter.StringVar(value=proj.pnp_separator)
        self.opt_separator = customtkinter.CTkOptionMenu(self, values=Project.get_separator_names(),
                                                    command=self.opt_separator_event,
                                                    variable=self.opt_separator_var)
        self.opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        # self.opt_separator.configure(state=tkinter.DISABLED)

        #
        # https://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified
        self.entry_first_row_var = customtkinter.StringVar(value="1")
        self.entry_first_row_var.trace_add("write", lambda n, i, m, sv=self.entry_first_row_var: self.var_first_row_event(sv))
        self.entry_first_row = customtkinter.CTkEntry(self, width=60, placeholder_text="first row", textvariable=self.entry_first_row_var)
        self.entry_first_row.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        #
        self.btn_load = customtkinter.CTkButton(self, text="Reload PnP",
                                                command=self.button_load_event)
        self.btn_load.grid(row=0, column=3, pady=5, padx=5, sticky="e")

        #
        sep_v = tkinter.ttk.Separator(self, orient='vertical')
        sep_v.grid(row=0, column=5, pady=2, padx=5, sticky="ns")

        #
        self.lbl_columns = customtkinter.CTkLabel(self, text="", justify="left")
        self.lbl_columns.grid(row=0, column=6, pady=5, padx=(15,5), sticky="w")
        self.update_lbl_columns()
        #
        self.btn_columns = customtkinter.CTkButton(self, text="Select\ncolumns...",
                                                   command=self.button_columns_event)
        self.btn_columns.grid(row=0, column=7, pady=5, padx=5, sticky="")
        #
        self.btn_edit = customtkinter.CTkButton(self, text="Go to\nEditor →", state=tkinter.DISABLED,
                                                command=self.button_edit_event)
        self.btn_edit.grid(row=0, column=8, pady=5, padx=5, sticky="")

    def opt_separator_event(self, new_sep: str):
        logging.info(f"  PnP separator: {new_sep}")
        proj.pnp_separator = new_sep
        self.button_load_event()

    def var_first_row_event(self, sv: customtkinter.StringVar):
        new_first_row = sv.get().strip()
        try:
            proj.pnp_first_row = int(new_first_row) - 1
            logging.info(f"  PnP 1st row: {proj.pnp_first_row+1}")
            self.button_load_event()
        except Exception as e:
            logging.error(f"  Invalid row number: {e}")

    def button_load_event(self):
        logging.debug("Load PnP...")
        try:
            self.pnp_view.load_pnp(proj.pnp_path, proj.pnp2_path)
        except Exception as e:
            logging.error(f"Cannot load PnP: {e}")

    def update_lbl_columns(self):
        self.lbl_columns.configure(text=f"COLUMNS:\n• Footprint: {proj.pnp_footprint_col}\n• Comment: {proj.pnp_comment_col}")

    def button_columns_event(self):
        logging.debug("Select PnP columns...")
        if proj.pnp_grid:
            columns = list.copy(proj.pnp_grid.rows_raw()[proj.pnp_first_row])
        else:
            columns = ["..."]

        if self.column_selector:
            self.column_selector.destroy()
        self.column_selector = ColumnsSelector(self, columns=columns, callback=self.column_selector_callback)

    def column_selector_callback(self, result: ColumnsSelectorResult):
        logging.debug(f"Selected PnP columns: ftprnt={result.footprint_col}, cmnt={result.comment_col}")
        proj.pnp_footprint_col = result.footprint_col
        proj.pnp_comment_col = result.comment_col
        proj.pnp_has_column_headers = result.has_column_headers
        self.update_lbl_columns()
        self.btn_edit.configure(state=tkinter.NORMAL)

    def button_edit_event(self):
        logging.debug(f"Go to Edit page")
        # refresh editor
        self.pnp_editor.load()
        self.select_editor()

# -----------------------------------------------------------------------------

class PnPEditor(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.btn_save = customtkinter.CTkButton(self, text="Save PnP as new CSV", command=self.button_save_event)
        self.btn_save.grid(row=2, column=0, pady=5, padx=5, sticky="e")
        self.btn_save.configure(state=tkinter.DISABLED)

    #
    def load(self):
        self.btn_save.configure(state=tkinter.DISABLED)
        self.scrollableframe = customtkinter.CTkScrollableFrame(self)
        self.scrollableframe.grid(row=0, column=0, padx=5, pady=1, sticky="wens")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.cb_footprint_list = []

        # if we are here, user already selected the PnP file first row
        proj.pnp_grid.firstrow = max(0, proj.pnp_first_row)
        proj.pnp_grid.firstrow += 1 if proj.pnp_has_column_headers else 0

        if (not proj.pnp_grid) or (proj.pnp_grid.nrows == 0):
            logging.warning("PnP project not loaded")
        else:
            if not self.check_selected_columns():
                logging.warning("Select proper Footprint and Comment columns before editing")
            else:
                component_list = list(item.name for item in components.items if not item.hidden)
                # find the max comment width
                footprint_max_w = 0

                for row in proj.pnp_grid.rows():
                    footprint_max_w = max(footprint_max_w, len(row[proj.pnp_footprint_col]))

                for idx, row in enumerate(proj.pnp_grid.rows()):
                    entry_pnp = tkinter.ttk.Entry(self.scrollableframe, font=customtkinter.CTkFont(family="Consolas"))
                    entry_pnp.grid(row=idx, column=1, padx=5, pady=1, sticky="we")
                    entry_txt = "{idx:03} | {ftprint:{fprint_w}} | {cmnt} ".format(
                        idx=idx+1,
                        ftprint=row[proj.pnp_footprint_col], fprint_w=footprint_max_w,
                        cmnt=row[proj.pnp_comment_col])
                    ui_helpers.entry_set_text(entry_pnp, entry_txt)
                    # entry_pnp.configure(state=tkinter.DISABLED)

                    # https://docs.python.org/3/library/tkinter.ttk.html?#tkinter.ttk.Combobox
                    # https://www.pythontutorial.net/tkinter/tkinter-combobox/
                    combo_footprint = tkinter.ttk.Combobox(self.scrollableframe, values=component_list)
                    self.cb_footprint_list.append(combo_footprint)
                    combo_footprint.grid(row=idx, column=2, padx=5, pady=1, sticky="we")
                    combo_footprint.bind('<<ComboboxSelected>>', self.combobox_selected)
                    combo_footprint.bind('<Key>', self.combobox_key)
                    combo_footprint.bind("<Return>", self.combobox_enter)
                    combo_footprint.bind("<MouseWheel>", self.combobox_wheel)
                    self.try_select_component(combo_footprint, component_list, row[proj.pnp_footprint_col], row[proj.pnp_comment_col])

                self.scrollableframe.grid_columnconfigure(1, weight=2)
                self.scrollableframe.grid_columnconfigure(2, weight=1)

    def try_select_component(self, cb: tkinter.ttk.Combobox, components: list[str], ftprint: str, cmnt: str):
        possible_component = ftprint + "_" + cmnt
        try:
            components.index(possible_component) # may raise exception if not found
            cb.set(possible_component)
            logging.info("Matched component found: {possible_component}")
        except:
            # not found
            pass

    def check_selected_columns(self, ) -> bool:
        return proj.pnp_footprint_col < proj.pnp_grid.ncols \
            and proj.pnp_comment_col < proj.pnp_grid.ncols

    def combobox_selected(self, event):
        selected_component = event.widget.get()
        logging.debug(f"CB selected: {selected_component}")
        try:
            # get the selection details:
            selected_idx = self.cb_footprint_list.index(event.widget)
            comment = proj.pnp_grid.rows()[selected_idx][proj.pnp_comment_col]
            ftprint = proj.pnp_grid.rows()[selected_idx][proj.pnp_footprint_col]
            # scan all items and if comment:footprint matches -> apply

            for i, row in enumerate(proj.pnp_grid.rows()):
                if i == selected_idx:
                    continue
                if self.cb_footprint_list[i].get() != "":
                    continue
                if row[proj.pnp_comment_col] == comment and row[proj.pnp_footprint_col] == ftprint:
                    # found: select the same component
                    logging.debug(f"Applying '{selected_component}' to item #{i}")
                    self.cb_footprint_list[i].set(selected_component)
        except Exception as e:
            logging.warning(f"Applying selection to matching items failed: {e}")
        self.btn_save.configure(state=tkinter.NORMAL)

    def combobox_key(self, event):
        logging.debug(f"CB key: {event}")
        self.btn_save.configure(state=tkinter.NORMAL)

    def combobox_enter(self, event):
        logging.debug(f"CB enter: {event}")
        self.btn_save.configure(state=tkinter.NORMAL)

    def combobox_wheel(self, event):
        # logging.debug(f"CB wheel: {event}")
        # block changing value when the list is hidden to avoid accidental modification
        return 'break'
        # pass

    def button_save_event(self):
        logging.debug("Save PnP")
        self.btn_save.configure(state=tkinter.DISABLED)
        # TODO: support for two separate files
        csv_path = os.path.splitext(proj.pnp_path)[0]
        csv_path += "_edited.csv"
        with open(csv_path, "w") as f:
            for i, row in enumerate(proj.pnp_grid.rows()):
                row_str = ";".join([f'"{item}"' for item in row])
                sel_component = self.cb_footprint_list[i].get()
                row_str += f';"{sel_component}"\n'
                f.write(row_str)
        logging.info(f"PnP saved to {csv_path}")

# -----------------------------------------------------------------------------

class ComponentsInfo(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.lblhtml_dbsummary = HTMLLabel(self, wrap='none', height=5)
        self.lblhtml_dbsummary.grid(row=0, column=0, padx=5, pady=5, sticky="wens")

        btn_scanner = customtkinter.CTkButton(self, text="Tou scanner...", command=self.btn_scanner_event)
        btn_scanner.grid(row=0, column=1, pady=5, padx=5, sticky="ne")

        self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)

    def btn_scanner_event(self):
        wnd_scanner = tou_scanner.TouScanner(callback=self.touscanner_callback)

    def touscanner_callback(self, action: str, new_components: ComponentsDB):
        logging.debug(f"TouScanner: {action}")
        if action == "o":
            # save to a CSV file
            db_directory = get_db_directory()

            if not os.path.isdir(db_directory):
                os.mkdir(db_directory)
            global components
            new_components.copy_attributes(components.items)
            new_components.save_new(db_directory)
            components = new_components
            self.update_components_info()

    def update_components_info(self):
        global components
        count = components.count_visible()
        hidden = components.count_hidden()

        self.database_summary_html = ''\
            '<h6>Components database</h6>'\
            '<pre style="font-family: Consolas, monospace; font-size: 80%">'\
            f'Items:   <span style="color: Blue">{count}</span> (+ {hidden} hidden)\n'\
            f'Created: <span style="color: Blue">{components.db_date}</span>\n'\
            '</pre>'

        self.lblhtml_dbsummary.set_html(self.database_summary_html)

# -----------------------------------------------------------------------------

class ComponentsEditor(customtkinter.CTkFrame):
    COMP_PER_PAGE = 500

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.components_pageno = 0

        self.components_info = ComponentsInfo(self)
        self.components_info.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.mk_components_view()

        #
        global components
        if not components or len(components.items) == 0:
            logging.info("DB editor: components DB is empty")
        else:
            self.load_components()

        self.frame_buttons = customtkinter.CTkFrame(self)
        self.frame_buttons.grid(row=2, column=0, pady=5, padx=5, sticky="we")
        self.frame_buttons.grid_columnconfigure(3, weight=1)

        # change components page, view contains up to self.COMP_PER_PAGE items
        self.btn_page_prev = customtkinter.CTkButton(self.frame_buttons, text="<", command=self.button_prev_event)
        self.btn_page_prev.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.lbl_pageno = customtkinter.CTkLabel(self.frame_buttons, text=self.format_pageno())
        self.lbl_pageno.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        self.btn_page_next = customtkinter.CTkButton(self.frame_buttons, text=">", command=self.button_next_event)
        self.btn_page_next.grid(row=0, column=2, pady=5, padx=5, sticky="w")

        #
        sep_v = tkinter.ttk.Separator(self.frame_buttons, orient='vertical')
        sep_v.grid(row=0, column=3, pady=2, padx=5, sticky="wens")

        # save DB modifications to file
        self.btn_save = customtkinter.CTkButton(self.frame_buttons, text="Save DB", command=self.button_save_event)
        self.btn_save.grid(row=0, column=4, pady=5, padx=5, sticky="e")

    def mk_components_view(self):
        self.scrollableframe = customtkinter.CTkScrollableFrame(self)
        self.scrollableframe.grid(row=1, column=0, padx=5, pady=5, columnspan=5, sticky="wens")
        self.scrollableframe.grid_columnconfigure(1, weight=2)
        self.scrollableframe.grid_columnconfigure(2, weight=1)
        # create all widgets only once, keeping them in arrays
        self.lbls_rowno = []
        self.entrys_name = []
        self.chkbttns_hidden = []
        self.vars_hidden = []

        for idx_on_page in range(self.COMP_PER_PAGE):
            lbl_rowno = tkinter.ttk.Label(self.scrollableframe, text="", justify="right")
            lbl_rowno.grid(row=idx_on_page, column=0, padx=5, pady=1, sticky="w")
            self.lbls_rowno.append(lbl_rowno)

            entry_name = tkinter.ttk.Entry(self.scrollableframe, font=customtkinter.CTkFont(family="Consolas"),)
            entry_name.grid(row=idx_on_page, column=1, padx=5, pady=1, sticky="we")
            self.entrys_name.append(entry_name)

            var = tkinter.IntVar(self.scrollableframe, value=False)
            self.vars_hidden.append(var)
            chkbttn_hidden = tkinter.ttk.Checkbutton(self.scrollableframe, text="Hidden", variable=var, command=self.chkbttn_event)
            chkbttn_hidden.grid(row=idx_on_page, column=2, padx=5, pady=1, sticky="we")
            self.chkbttns_hidden.append(chkbttn_hidden)

    def format_pageno(self) -> str:
        global components
        pageno_str = f"{1 + self.components_pageno} / {1 + len(components.items) // self.COMP_PER_PAGE}"
        return pageno_str

    def load_components(self):
        global components
        components_subrange = components.items[self.components_pageno * self.COMP_PER_PAGE:]

        for idx_on_page, component in enumerate(components_subrange):
            if idx_on_page == self.COMP_PER_PAGE:
                break

            idx_absolute = idx_on_page + (self.components_pageno * self.COMP_PER_PAGE)
            self.lbls_rowno[idx_on_page].configure(text=f"{idx_absolute+1:04}.")
            ui_helpers.entry_set_text(self.entrys_name[idx_on_page], component.name)
            self.vars_hidden[idx_on_page].set(component.hidden)

        # clear remaining fields
        for i in range(len(components_subrange), self.COMP_PER_PAGE):
                self.lbls_rowno[i].configure(text="-")
                ui_helpers.entry_set_text(self.entrys_name[i], "")
                self.vars_hidden[i].set(False)

    def chkbttn_event(self):
        self.btn_save.configure(state=tkinter.NORMAL)

    def store_checkbox_selections(self):
        components_subrange = components.items[self.components_pageno * self.COMP_PER_PAGE:]
        for idx_on_page, component in enumerate(components_subrange):
            if idx_on_page == self.COMP_PER_PAGE:
                break
            component.hidden = self.vars_hidden[idx_on_page].get() == 1

    def button_prev_event(self):
        logging.debug("prev page")
        if self.components_pageno > 0:
            self.store_checkbox_selections()
            self.components_pageno -= 1
            self.load_components()
            self.lbl_pageno.configure(text=self.format_pageno())

    def button_next_event(self):
        logging.debug("next page")
        if self.components_pageno < len(components.items) // self.COMP_PER_PAGE:
            self.store_checkbox_selections()
            self.components_pageno += 1
            self.load_components()
            self.lbl_pageno.configure(text=self.format_pageno())

    def button_save_event(self):
        logging.debug("Save DB")
        self.store_checkbox_selections()
        components.save_changes()
        self.btn_save.configure(state=tkinter.DISABLED)
        self.components_info.update_components_info()

# -----------------------------------------------------------------------------

class CtkApp(customtkinter.CTk):
    TAB_HOME = "Start"
    TAB_PREVIEW = "PnP Preview"
    TAB_EDITOR = "PnP Editor"
    TAB_COMPONENTS = "DB Components"

    def __init__(self):
        logging.info('Ctk app is starting')
        super().__init__()

        self.title(f"{APP_NAME}")
        self.geometry("1000x600")
        self.grid_columnconfigure(0, weight=1)

        # tabular panel with Home/Preview/Editor
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.grid_rowconfigure(0, weight=1) # set row 1 height to all remaining space
        tab_home = self.tabview.add(self.TAB_HOME)
        tab_preview = self.tabview.add(self.TAB_PREVIEW)
        tab_pnp_editor = self.tabview.add(self.TAB_EDITOR)
        tab_db_editor = self.tabview.add(self.TAB_COMPONENTS)

        # home panel
        self.home_frame = HomeFrame(tab_home)
        self.home_frame.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        tab_home.grid_columnconfigure(0, weight=1)
        # tab_home.grid_rowconfigure(1, weight=1)

        #
        try:
            global components
            components = ComponentsDB()
            db_directory = get_db_directory()
            if os.path.isdir(db_directory):
                components.load(db_directory)
                logging.info(f"  Date: {components.db_date}")
                logging.info(f"  Items: {len(components.items)}")
            else:
                logging.warning(f"DB folder not found at {db_directory}")
        except Exception as e:
            logging.error(f"Error loading database: {e}")

        # panel with the PnP
        self.pnp_view = PnPView(tab_preview)
        self.pnp_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.pnp_config = PnPConfig(tab_preview, pnp_view=self.pnp_view)
        self.pnp_config.grid(row=1, column=0, padx=5, pady=5, sticky="we")
        self.pnp_config.select_editor = self.tab_select_editor()
        self.home_frame.pnp_config = self.pnp_config
        self.home_frame.pnp_view = self.pnp_view

        # panel with PnP footprints editor
        self.pnp_editor = PnPEditor(tab_pnp_editor)
        self.pnp_editor.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        tab_pnp_editor.grid_columnconfigure(0, weight=1)
        tab_pnp_editor.grid_rowconfigure(0, weight=1)
        self.pnp_view.pnp_editor = self.pnp_editor
        self.pnp_config.pnp_editor = self.pnp_editor

        # panel with DB editor
        self.components_editor = ComponentsEditor(tab_db_editor)
        self.components_editor.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.components_editor.components_info.update_components_info()

        tab_db_editor.grid_columnconfigure(0, weight=1)
        tab_db_editor.grid_rowconfigure(0, weight=1)

        #
        tab_preview.grid_columnconfigure(0, weight=1)
        tab_preview.grid_rowconfigure(0, weight=1)

        # UI ready
        logging.info('Application ready.')

    def tab_select_editor(self):
        # return a closure
        appwnd = self
        return lambda: appwnd.tabview.set(appwnd.TAB_EDITOR)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # logger config with dimmed time
    # https://docs.python.org/3/howto/logging.html
    logging.basicConfig(format='\033[30m%(asctime)s\033[39m %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    # https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output

    ANSI_FG_WHITE=  "\033[1;37m"
    ANSI_FG_YELLOW= "\033[1;33m"
    ANSI_FG_RED=    "\033[1;31m"
    ANSI_FG_DEFAULT="\033[1;0m"

    # logging.addLevelName(logging.INFO,    "\033[1;37m%s\033[1;0m" % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.DEBUG,    "DEBUG")
    logging.addLevelName(logging.INFO,    f"{ANSI_FG_WHITE}INFO {ANSI_FG_DEFAULT}")
    logging.addLevelName(logging.WARNING, f"{ANSI_FG_YELLOW}WARN {ANSI_FG_DEFAULT}")
    logging.addLevelName(logging.ERROR,   f"{ANSI_FG_RED}ERROR{ANSI_FG_DEFAULT}")

    logging.info(f"{APP_NAME}   (c) 2023")

    if (sys.version_info.major < 3) or (sys.version_info.minor < 9):
        logging.error("Required Python version 3.9 or later!")
        exit()
    else:
        logging.info(
            f"Python version: {sys.version_info.major}.{sys.version_info.minor}"
        )

    # https://customtkinter.tomschimansky.com/documentation/appearancemode
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("blue")

    ctkapp = CtkApp()
    ctkapp.mainloop()
