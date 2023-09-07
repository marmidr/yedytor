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
from components import ComponentsDB
from config import Config

# -----------------------------------------------------------------------------

APP_NAME = "Yedytor v0.4.2"

# -----------------------------------------------------------------------------

def get_db_directory() -> str:
    db_path = os.path.dirname(__file__)
    db_path = os.path.join(db_path, "..")
    db_path = os.path.abspath(db_path)
    db_path = os.path.join(db_path, "db")
    return db_path

# -----------------------------------------------------------------------------

class Project:
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

    def get_name(self) -> str:
        return os.path.basename(self.pnp_path)

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
            if pnp2_grid.ncols != glob_proj.pnp_grid.ncols:
                raise ValueError("PnP has {} columns, but PnP2 has {} columns".format(
                    self.pnp_grid.ncols, pnp2_grid.ncols
                ))

            self.pnp_grid.nrows += pnp2_grid.nrows
            self.pnp_grid.rows_raw().extend(pnp2_grid.rows)

# -----------------------------------------------------------------------------

# global instance
glob_proj = Project()
glob_components = ComponentsDB()
glob_config = Config()

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

        #
        sep_h = tkinter.ttk.Separator(self, orient='horizontal')
        sep_h.grid(row=3, column=0, pady=5, padx=5, columnspan=4, sticky="we")

        #
        self.config = customtkinter.CTkFrame(self)
        self.config.grid(row=4, column=0, pady=5, padx=5, columnspan=4, sticky="we")
        self.config.lbl_font = customtkinter.CTkLabel(self.config, text="PnP Editor font size:")
        self.config.lbl_font.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.config.radio_var = tkinter.IntVar(value=glob_config.editor_font_idx)
        self.config.rb_font0 = customtkinter.CTkRadioButton(self.config, text="12px",
                                                            variable=self.config.radio_var, value=0, command=self.radiobutton_event)
        self.config.rb_font0.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.config.rb_font1 = customtkinter.CTkRadioButton(self.config, text="16px",
                                                            variable=self.config.radio_var, value=1, command=self.radiobutton_event)
        self.config.rb_font1.grid(row=2, column=0, pady=5, padx=5, sticky="w")

    def radiobutton_event(self):
        glob_config.editor_font_idx = self.config.radio_var.get()
        # logging.debug(f"RB event: {config.editor_font_idx}")
        glob_config.save()

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
            MessageBox(dialog_type="o", message="You can only select one or two PnP files of the same type",
                        callback=lambda btn: btn)
            return
        elif len(pnp_paths) == 2:
            # https://docs.python.org/3/library/os.path.html#os.path.splitext
            ext1 = os.path.splitext(pnp_paths[0])[1].lower()
            ext2 = os.path.splitext(pnp_paths[1])[1].lower()
            if ext1 != ext2:
                MessageBox(dialog_type="o", message="You must select two PnP files of the same type",
                            callback=lambda btn: btn)
                return

        if len(pnp_paths) and os.path.isfile(pnp_paths[0]):
            try:
                # reset entire project
                global glob_proj
                sep_backup = glob_proj.pnp_separator
                glob_proj = Project()

                glob_proj.pnp_separator = sep_backup
                glob_proj.pnp_path = pnp_paths[0]
                glob_proj.pnp2_path = pnp_paths[1] if len(pnp_paths) > 1 else ""
                self.var_pnp.set(glob_proj.pnp_path)
                self.var_pnp2.set(glob_proj.pnp2_path)

                self.activate_csv_separator()
            except Exception as e:
                logging.error(f"Cannot open file: {e}")
        else:
            if len(pnp_paths):
                logging.error(f"Cannot access the file '{pnp_paths[0]}'")

    def activate_csv_separator(self):
        pnp_fname = glob_proj.pnp_path.lower()
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

        glob_proj.load_from_file(path, path2)
        pnp_txt_grid = glob_proj.pnp_grid.format_grid(glob_proj.pnp_first_row)
        self.textbox.insert("0.0", pnp_txt_grid)
        glob_proj.pnp_grid_dirty = False
        # refresh editor (if columns were selected)
        if glob_proj.pnp_footprint_col > 0 or glob_proj.pnp_comment_col > 0:
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

        self.opt_separator_var = customtkinter.StringVar(value=glob_proj.pnp_separator)
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
        self.btn_columns = customtkinter.CTkButton(self, text="Select\ncolumns...", state=tkinter.DISABLED,
                                                   command=self.button_columns_event)
        self.btn_columns.grid(row=0, column=7, pady=5, padx=5, sticky="")
        #
        self.btn_edit = customtkinter.CTkButton(self, text="Go to\nEditor →", state=tkinter.DISABLED,
                                                command=self.button_edit_event)
        self.btn_edit.grid(row=0, column=8, pady=5, padx=5, sticky="")

    def opt_separator_event(self, new_sep: str):
        logging.info(f"  PnP separator: {new_sep}")
        glob_proj.pnp_separator = new_sep
        self.button_load_event()

    def var_first_row_event(self, sv: customtkinter.StringVar):
        new_first_row = sv.get().strip()
        try:
            glob_proj.pnp_first_row = int(new_first_row) - 1
            logging.info(f"  PnP 1st row: {glob_proj.pnp_first_row+1}")
            self.button_load_event()
        except Exception as e:
            logging.error(f"  Invalid row number: {e}")

    def button_load_event(self):
        logging.debug("Load PnP...")
        try:
            self.pnp_view.load_pnp(glob_proj.pnp_path, glob_proj.pnp2_path)
            self.btn_columns.configure(state=tkinter.NORMAL)
        except Exception as e:
            logging.error(f"Cannot load PnP: {e}")

    def update_lbl_columns(self):
        self.lbl_columns.configure(text=f"COLUMNS:\n• Footprint: {glob_proj.pnp_footprint_col}\n• Comment: {glob_proj.pnp_comment_col}")

    def button_columns_event(self):
        logging.debug("Select PnP columns...")
        if glob_proj.pnp_grid:
            columns = list.copy(glob_proj.pnp_grid.rows_raw()[glob_proj.pnp_first_row])
        else:
            columns = ["..."]

        if self.column_selector:
            self.column_selector.destroy()
        self.column_selector = ColumnsSelector(self, columns=columns, callback=self.column_selector_callback)

    def column_selector_callback(self, result: ColumnsSelectorResult):
        logging.debug(f"Selected PnP columns: ftprnt={result.footprint_col}, cmnt={result.comment_col}")
        glob_proj.pnp_footprint_col = result.footprint_col
        glob_proj.pnp_comment_col = result.comment_col
        glob_proj.pnp_has_column_headers = result.has_column_headers
        self.update_lbl_columns()
        self.btn_edit.configure(state=tkinter.NORMAL)

    def button_edit_event(self):
        logging.debug(f"Go to Edit page")
        # refresh editor
        self.pnp_editor.load()
        self.select_editor()

# -----------------------------------------------------------------------------

class PnPEditor(customtkinter.CTkFrame):
    CL_NOMATCH = "orange"
    CL_FILTER = "yellow"
    CL_AUTO_SEL = "lime"
    CL_MAN_SEL = "green"

    def __init__(self, master, **kwargs):
        app = None
        if 'app' in kwargs:
            app = kwargs.pop('app')

        super().__init__(master, **kwargs)

        self.pgbar_selected = customtkinter.CTkProgressBar(self)
        self.pgbar_selected.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.pgbar_selected.set(0)

        self.lbl_selected = tkinter.Label(self, text="0 / 500")
        self.lbl_selected.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        sep_v = tkinter.ttk.Separator(self, orient='vertical')
        sep_v.grid(row=2, column=2, pady=2, padx=5, sticky="ns")

        self.btn_save = customtkinter.CTkButton(self, text="Save PnP as new CSV", command=self.button_save_event)
        self.btn_save.grid(row=2, column=3, pady=5, padx=5, sticky="e")
        self.btn_save.configure(state=tkinter.DISABLED)

        #
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # define fonts for editor
        self.fonts = (
            (
                customtkinter.CTkFont(family="Consolas", size=12, weight='normal'),
                customtkinter.CTkFont(family="Consolas", size=12, weight='bold')
            ),
            (
                customtkinter.CTkFont(family="Consolas", size=16, weight='normal'),
                customtkinter.CTkFont(family="Consolas", size=16, weight='bold')
            )
        )

        if not app is None:
            # apply font to ALL application combobox list
            app.option_add('*TCombobox*Listbox.font', self.fonts[glob_config.editor_font_idx][0])
            app.option_add('*TCombobox*Listbox.background', 'LightBlue')

    def load(self):
        self.btn_save.configure(state=tkinter.DISABLED)
        self.scrollableframe = customtkinter.CTkScrollableFrame(self)
        self.scrollableframe.grid(row=0, column=0, padx=5, pady=1, columnspan=4, sticky="wens")
        self.entry_list = []
        self.cbx_component_list = []
        self.lbl_marker_list = []
        self.focused_idx = None

        # if we are here, user already selected the PnP file first row
        glob_proj.pnp_grid.firstrow = max(0, glob_proj.pnp_first_row)
        glob_proj.pnp_grid.firstrow += 1 if glob_proj.pnp_has_column_headers else 0

        if (not glob_proj.pnp_grid) or (glob_proj.pnp_grid.nrows == 0):
            logging.warning("PnP file not loaded")
        else:
            if not self.check_selected_columns():
                logging.warning("Select proper Footprint and Comment columns before editing")
            else:
                self.components_all = glob_components.items_visible()
                # find the max comment width
                footprint_max_w = 0

                for row in glob_proj.pnp_grid.rows():
                    footprint_max_w = max(footprint_max_w, len(row[glob_proj.pnp_footprint_col]))

                for idx, row in enumerate(glob_proj.pnp_grid.rows()):
                    entry_pnp = tkinter.Entry(self.scrollableframe, font=self.fonts[glob_config.editor_font_idx][0])
                    entry_pnp.grid(row=idx, column=0, padx=5, pady=1, sticky="we")
                    entry_txt = "{idx:03} | {ftprint:{fprint_w}} | {cmnt} ".format(
                        idx=idx+1,
                        ftprint=row[glob_proj.pnp_footprint_col], fprint_w=footprint_max_w,
                        cmnt=row[glob_proj.pnp_comment_col])
                    ui_helpers.entry_set_text(entry_pnp, entry_txt)
                    self.entry_list.append(entry_pnp)
                    # entry_pnp.configure(state=tkinter.DISABLED)

                    lbl_marker = tkinter.Label(self.scrollableframe, text=" ")
                    lbl_marker.grid(row=idx, column=1, padx=5, pady=1, sticky="")
                    self.lbl_marker_list.append(lbl_marker)

                    # https://docs.python.org/3/library/tkinter.ttk.html?#tkinter.ttk.Combobox
                    # https://www.pythontutorial.net/tkinter/tkinter-combobox/
                    cbx_component = tkinter.ttk.Combobox(self.scrollableframe, values=self.components_all, font=self.fonts[glob_config.editor_font_idx][0])
                    cbx_component.grid(row=idx, column=2, padx=5, pady=1, sticky="we")
                    cbx_component.bind('<<ComboboxSelected>>', self.combobox_selected)
                    # combo_footprint.bind('<Key>', self.combobox_key)
                    cbx_component.bind("<Return>", self.combobox_return)
                    cbx_component.bind("<MouseWheel>", self.combobox_wheel)
                    cbx_component.bind("<FocusIn>", self.combobox_focus_in)
                    self.cbx_component_list.append(cbx_component)
                    self.try_select_component(cbx_component, lbl_marker, row[glob_proj.pnp_footprint_col], row[glob_proj.pnp_comment_col])

                self.scrollableframe.grid_columnconfigure(0, weight=2)
                self.scrollableframe.grid_columnconfigure(2, weight=1)

            # update progressbar
            self.update_selected_status()

    def try_select_component(self, cbx: tkinter.ttk.Combobox, lbl: tkinter.Label, ftprint: str, cmnt: str):
        filter = ftprint + "_" + cmnt
        try:
            self.components_all.index(filter) # may raise exception if not found
            cbx.set(filter)
            # mark autoselection
            lbl.config(background=self.CL_AUTO_SEL)
            logging.info(f"Matching component found: {filter}")
        except:
            # not found; try to create a good filter expression
            # "1206_R_1,2k" -> "1206"
            ftprint_prefix = ftprint.split("_")
            if len(ftprint_prefix):
                ftprint_prefix = ftprint_prefix[0]
                filter = ftprint_prefix + " " + cmnt
                # assign a filtered list of components
                filtered_components = glob_components.items_filtered(filter)
                cbx.configure(values=filtered_components)
                # set value to the filter
                cbx.set(filter.lower())
                if len(filtered_components):
                    # mark filter
                    lbl.config(background=self.CL_FILTER)
                else:
                    # remove filter and assign all components
                    cbx.set("")
                    cbx.configure(values=self.components_all)
                    # mark no matching component in database
                    lbl.config(background=self.CL_NOMATCH)

    def check_selected_columns(self, ) -> bool:
        return glob_proj.pnp_footprint_col < glob_proj.pnp_grid.ncols \
            and glob_proj.pnp_comment_col < glob_proj.pnp_grid.ncols

    def combobox_selected(self, event):
        selected_component = event.widget.get()
        logging.debug(f"CB selected: {selected_component}")
        try:
            # get the selection details:
            selected_idx = self.cbx_component_list.index(event.widget)
            comment = glob_proj.pnp_grid.rows()[selected_idx][glob_proj.pnp_comment_col]
            ftprint = glob_proj.pnp_grid.rows()[selected_idx][glob_proj.pnp_footprint_col]

            # scan all items and if comment:footprint matches -> apply
            for i, row in enumerate(glob_proj.pnp_grid.rows()):
                if i == selected_idx:
                    # add marker that this is a final value
                    self.lbl_marker_list[i].config(background=self.CL_MAN_SEL)
                    continue
                marker_bg = self.lbl_marker_list[i].cget("background")
                # if already selected, skip this item
                if marker_bg == self.CL_MAN_SEL:
                    continue
                if row[glob_proj.pnp_comment_col] == comment and row[glob_proj.pnp_footprint_col] == ftprint:
                    # found: select the same component
                    logging.debug(f"Applying '{selected_component}' to item #{i}")
                    self.cbx_component_list[i].set(selected_component)
                    # add marker that this is a final value
                    self.lbl_marker_list[i].config(background=self.CL_MAN_SEL)
            self.update_selected_status()
        except Exception as e:
            logging.warning(f"Applying selection to the matching items failed: {e}")
        self.btn_save.configure(state=tkinter.NORMAL)

    # def combobox_key(self, event):
        # logging.debug(f"CB key: {event}")
        # self.btn_save.configure(state=tkinter.NORMAL)

    def combobox_return(self, event):
        filter: str = event.widget.get().strip()
        if len(filter) > 2:
            components_filtered = glob_components.items_filtered(filter)
            logging.debug(f"Apply filter '{filter}' -> {len(components_filtered)} matching")
            event.widget.configure(values=components_filtered)

            selected_idx = self.cbx_component_list.index(event.widget)
            try:
                self.components_all.index(filter)
                # filter found on component list: add marker that this is a final value
                self.lbl_marker_list[selected_idx].config(background=self.CL_MAN_SEL)
            except:
                if len(components_filtered):
                    # mark this is a filter, not value
                    self.lbl_marker_list[selected_idx].config(background=self.CL_FILTER)
                else:
                    # mark no matching component in database
                    self.lbl_marker_list[selected_idx].config(background=self.CL_NOMATCH)

        else:
            logging.debug(f"Filter too short: use full list")
            event.widget.configure(values=self.components_all)

        self.btn_save.configure(state=tkinter.NORMAL)

    def combobox_wheel(self, event):
        # logging.debug(f"CB wheel: {event}")
        # block changing value when the list is hidden to avoid accidental modification
        return 'break'
        # pass

    def combobox_focus_in(self, event):
        # logging.debug(f"CB focus_in: {event}")
        try:
            # restore normal font on previous item
            if not self.focused_idx is None and self.focused_idx < len(self.entry_list):
                self.entry_list[self.focused_idx].config(font=self.fonts[glob_config.editor_font_idx][0])
                self.cbx_component_list[self.focused_idx].config(font=self.fonts[glob_config.editor_font_idx][0])

            # set bold font in new item
            self.focused_idx = self.cbx_component_list.index(event.widget)
            self.entry_list[self.focused_idx].config(font=self.fonts[glob_config.editor_font_idx][1])
            self.cbx_component_list[self.focused_idx].config(font=self.fonts[glob_config.editor_font_idx][1])
        except Exception as e:
            logging.debug(f"focus_in: {e}")

    def button_save_event(self):
        logging.debug("Save PnP")
        n_selected = self.count_selected()
        if n_selected[0] == n_selected[1]:
            self.btn_save.configure(state=tkinter.DISABLED)
            self.save_pnp_to_new_csv_file()
        else:
            MessageBox(dialog_type="yn",
                       message=f"Only {n_selected[0]} / {n_selected[1]} items have selected PnP component.\n\nSave it now?",
                       callback=self.msgbox_save_callback)

    def msgbox_save_callback(self, btn: str):
        if btn == "y":
            self.save_pnp_to_new_csv_file()

    def save_pnp_to_new_csv_file(self):
        csv_path = os.path.splitext(glob_proj.pnp_path)[0]
        csv_path += "_edited.csv"
        write_errors = 0

        with open(csv_path, "w", encoding="UTF-8") as f:
            for i, row in enumerate(glob_proj.pnp_grid.rows()):
                row_str = ";".join([f'"{item}"' for item in row])
                sel_component = self.cbx_component_list[i].get()
                row_str += f';"{sel_component}"\n'
                try:
                    f.write(row_str)
                except UnicodeEncodeError as e:
                    logging.error(f"Encoding error in: {i}. {row_str} -> {e}")
                    write_errors += 1
        if write_errors == 0:
            logging.info(f"PnP saved to {csv_path}")
        else:
            logging.warning(f"PnP saved to {csv_path} with {write_errors} errors")
            mb = MessageBox(dialog_type="o",
                            message=f"Encoding errors occured!\n\n{write_errors} items not saved",
                            callback=lambda btn: btn)

    def update_selected_status(self):
        n_selected = self.count_selected()
        self.lbl_selected.configure(text=f"{n_selected[0]} / {n_selected[1]}")
        if n_selected[1] > 0:
            self.pgbar_selected.set(n_selected[0] / n_selected[1])
        else:
            self.pgbar_selected.set(0)

    def count_selected(self) -> (int, int):
        n = 0
        for lbl in self.lbl_marker_list:
            bg = lbl.cget("background")
            if bg in (self.CL_MAN_SEL, self.CL_AUTO_SEL):
                n += 1
        return (n, len(self.lbl_marker_list))

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
            global glob_components
            new_components.copy_attributes(glob_components.items_all())
            new_components.save_new(db_directory)
            glob_components = new_components
            self.update_components_info()

    def update_components_info(self):
        global glob_components
        count = glob_components.count_visible()
        hidden = glob_components.count_hidden()

        self.database_summary_html = ''\
            '<h6>Components database</h6>'\
            '<pre style="font-family: Consolas, monospace; font-size: 80%">'\
            f'Items:   <span style="color: Blue">{count}</span> (+ {hidden} hidden)\n'\
            f'Created: <span style="color: Blue">{glob_components.db_date}</span>\n'\
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
        global glob_components
        if not glob_components or len(glob_components.items_all()) == 0:
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
        sep_v.grid(row=0, column=3, pady=2, padx=5, sticky="ns")

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
        self.editor_font = customtkinter.CTkFont(family="Consolas")

        for idx_on_page in range(self.COMP_PER_PAGE):
            lbl_rowno = tkinter.Label(self.scrollableframe, text="", justify="right")
            lbl_rowno.grid(row=idx_on_page, column=0, padx=5, pady=1, sticky="w")
            self.lbls_rowno.append(lbl_rowno)

            entry_name = tkinter.Entry(self.scrollableframe, font=self.editor_font)
            entry_name.grid(row=idx_on_page, column=1, padx=5, pady=1, sticky="we")
            self.entrys_name.append(entry_name)

            var = tkinter.IntVar(self.scrollableframe, value=False)
            self.vars_hidden.append(var)
            chkbttn_hidden = tkinter.Checkbutton(self.scrollableframe, text="Hidden", variable=var, command=self.chkbttn_event)
            chkbttn_hidden.grid(row=idx_on_page, column=2, padx=5, pady=1, sticky="w")
            self.chkbttns_hidden.append(chkbttn_hidden)

    def format_pageno(self) -> str:
        global glob_components
        pageno_str = f"{1 + self.components_pageno} / {1 + len(glob_components.items_all()) // self.COMP_PER_PAGE}"
        return pageno_str

    def load_components(self):
        global glob_components
        components_subrange = glob_components.items_all()[self.components_pageno * self.COMP_PER_PAGE:]

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
        components_subrange = glob_components.items_all()[self.components_pageno * self.COMP_PER_PAGE:]
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
        if self.components_pageno < len(glob_components.items_all()) // self.COMP_PER_PAGE:
            self.store_checkbox_selections()
            self.components_pageno += 1
            self.load_components()
            self.lbl_pageno.configure(text=self.format_pageno())

    def button_save_event(self):
        logging.debug("Save DB")
        self.store_checkbox_selections()
        glob_components.save_changes()
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
            global glob_components
            glob_components = ComponentsDB()
            db_directory = get_db_directory()
            if os.path.isdir(db_directory):
                glob_components.load(db_directory)
                logging.info(f"  Date: {glob_components.db_date}")
                logging.info(f"  Items: {len(glob_components.items_all())}")
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
        self.pnp_editor = PnPEditor(tab_pnp_editor, app=self)
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
