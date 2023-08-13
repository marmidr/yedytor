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

class Project:
    CONFIG_FILE_NAME = "yedytor.ini"
    pnp_path: str = "<pnp_fpath>"
    pnp2_path: str = ""
    pnp_separator: str = ""
    __config: configparser.ConfigParser
    pnp_grid: text_grid.TextGrid = None
    pnp_grid_dirty: bool = False
    pnp_footprint_col: int = 0
    pnp_comment_col: int = 0

    def __init__(self):
        self.pnp_separator = "SPACES"
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

# global instance
proj = Project()
components = ComponentsDB()

# -----------------------------------------------------------------------------

class HomeFrame(customtkinter.CTkFrame):
    pnp_config = None
    pnp_view = None

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

class ComponentsFrame(customtkinter.CTkFrame):
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
            if not os.path.isdir("db"):
                os.mkdir("db")
            # TODO: scan present DB and apply 'hidden' attribute to a new DB
            new_components.save("db")
            global components
            components = new_components
            self.update_components_info(components.db_date, len(components.items))

    def update_components_info(self, date: str, count: int):
        self.database_summary_html = ''\
            '<h6>Components database</h6>'\
            '<pre style="font-family: Consolas, monospace; font-size: 80%">'\
            f'Items total: <span style="color: Blue">{count}</span>\n'\
            f'Created: <span style="color: Blue">{date}</span>\n'\
            '</pre>'

        self.lblhtml_dbsummary.set_html(self.database_summary_html)

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

        delim = proj.get_pnp_delimiter()
        path_lower = path.lower()

        if path_lower.endswith("xls"):
            proj.pnp_grid = xls_reader.read_xls_sheet(path)
        elif path_lower.endswith("xlsx"):
            proj.pnp_grid = xlsx_reader.read_xlsx_sheet(path)
        elif path_lower.endswith("ods"):
            proj.pnp_grid = ods_reader.read_ods_sheet(path)
        else: # assume CSV
            proj.pnp_grid = csv_reader.read_csv(path, delim)

        log_f = logging.info if proj.pnp_grid.nrows > 0 else logging.warning
        log_f(f"PnP: {proj.pnp_grid.nrows} rows x {proj.pnp_grid.ncols} cols")

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
                    proj.pnp_grid.ncols, pnp2_grid.ncols
                ))

            proj.pnp_grid.nrows += pnp2_grid.nrows
            proj.pnp_grid.rows.extend(pnp2_grid.rows)

        pnp_txt_grid = proj.pnp_grid.format_grid(0)
        self.textbox.insert("0.0", pnp_txt_grid)
        proj.pnp_grid_dirty = False
        # refresh preview
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
    pnp_view: PnPView = None
    column_selector: ColumnsSelector = None

    def __init__(self, master, **kwargs):
        assert "pnp_view" in kwargs
        self.pnp_view = kwargs.pop("pnp_view")
        assert isinstance(self.pnp_view, PnPView)

        super().__init__(master, **kwargs)

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
        self.btn_load = customtkinter.CTkButton(self, text="Reload PnP",
                                                command=self.button_load_event)
        self.btn_load.grid(row=0, column=2, pady=5, padx=5, sticky="e")

        #
        self.lbl_columns = customtkinter.CTkLabel(self, text="", justify="left")
        self.lbl_columns.grid(row=0, column=4, pady=5, padx=(15,5), sticky="w")
        self.update_lbl_columns()
        #
        self.btn_columns = customtkinter.CTkButton(self, text="Select\ncolumns...",
                                                   command=self.button_columns_event)
        self.btn_columns.grid(row=0, column=5, pady=5, padx=5, sticky="")

    def opt_separator_event(self, new_sep: str):
        logging.info(f"  PnP separator: {new_sep}")
        proj.pnp_separator = new_sep
        self.button_load_event()

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
            columns = list.copy(proj.pnp_grid.rows[0])
        else:
            columns = ["..."]

        if self.column_selector:
            self.column_selector.destroy()
        self.column_selector = ColumnsSelector(self, columns=columns, callback=self.column_selector_callback)

    def column_selector_callback(self, result: ColumnsSelectorResult):
        logging.debug(f"Selected PnP columns: ftprnt={result.footprint_col}, cmnt={result.comment_col}")
        proj.pnp_footprint_col = result.footprint_col
        proj.pnp_comment_col = result.comment_col
        self.update_lbl_columns()

# -----------------------------------------------------------------------------

class PnPEditor(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    #
    def load(self):
        if proj.pnp_grid:
            component_list = list(item.name for item in components.items if not item.hidden)

            for idx, row in enumerate(proj.pnp_grid.rows):
                lbl_rowno = tkinter.ttk.Label(self, text=f"{idx+1}.")
                lbl_rowno.grid(row=idx, column=0, padx=5, pady=1, sticky="w")

                entry_pnp = tkinter.ttk.Entry(self)
                entry_pnp.grid(row=idx, column=1, padx=5, pady=1, sticky="we")
                entry_txt = " • ".join(row)
                ui_helpers.entry_set_text(entry_pnp, entry_txt)
                entry_pnp.configure(state=tkinter.DISABLED)

                # https://docs.python.org/3/library/tkinter.ttk.html?#tkinter.ttk.Combobox
                # https://www.pythontutorial.net/tkinter/tkinter-combobox/
                combo_footprint = tkinter.ttk.Combobox(self, values=component_list)
                combo_footprint.grid(row=idx, column=2, padx=5, pady=1, sticky="we")
                combo_footprint.bind('<<ComboboxSelected>>', self.combobox_event)

            self.grid_columnconfigure(1, weight=3)
            self.grid_columnconfigure(2, weight=1)
        else:
            logging.warning("PnP project not loaded")

    def combobox_event(self, event):
        print(f"CB event: {event}")

# -----------------------------------------------------------------------------

class CtkApp(customtkinter.CTk):
    def __init__(self):
        logging.info('Ctk app is starting')
        super().__init__()

        self.title(f"{APP_NAME}")
        self.geometry("1200x600")
        self.grid_columnconfigure(0, weight=1)

        # tabular panel with Home/Preview/Editor
        tabview = customtkinter.CTkTabview(self)
        tabview.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.grid_rowconfigure(0, weight=1) # set row 1 height to all remaining space
        tab_home = tabview.add("Start")
        tab_preview = tabview.add("PnP Preview")
        tab_editor = tabview.add("PnP Editor")
        tab_db_preview = tabview.add("DB Components")

        # home panel
        self.home_frame = HomeFrame(tab_home)
        self.home_frame.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.components_frame = ComponentsFrame(tab_home)
        self.components_frame.grid(row=1, column=0, padx=5, pady=5, sticky="wens")
        tab_home.grid_columnconfigure(0, weight=1)
        # tab_home.grid_rowconfigure(1, weight=1)

        #
        try:
            global components
            components = ComponentsDB()
            components.load("db")
            logging.info(f"  Date: {components.db_date}")
            logging.info(f"  Items: {len(components.items)}")
            self.components_frame.update_components_info(components.db_date, len(components.items))
        except Exception as e:
            logging.error(f"Error loading database: {e}")

        # panel with the PnP
        self.pnp_view = PnPView(tab_preview)
        self.pnp_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.pnp_config = PnPConfig(tab_preview, pnp_view=self.pnp_view)
        self.pnp_config.grid(row=1, column=0, padx=5, pady=5, sticky="we")
        self.home_frame.pnp_config = self.pnp_config
        self.home_frame.pnp_view = self.pnp_view

        # panel to edit the PnP footprints
        self.pnp_editor = PnPEditor(tab_editor)
        self.pnp_editor.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        tab_editor.grid_columnconfigure(0, weight=1)
        tab_editor.grid_rowconfigure(0, weight=1)

        self.pnp_view.pnp_editor = self.pnp_editor

        #
        tab_preview.grid_columnconfigure(0, weight=1)
        tab_preview.grid_rowconfigure(0, weight=1)

        # UI ready
        logging.info('Application ready.')

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
