# Yedytor
#
# PnP files editor, using a footprint components defined in the Yamaha .Tou files.
#
# (c) 2023-2025 Mariusz Midor
# https://github.com/marmidr/yedytor

import logger
import os
import sys
import time
import tkinter
from typing import Callable

import customtkinter

import db_scanner
import ui_helpers
import pnp_editor_helpers
import output
import board_view

from pnp_editor_helpers import Marker
from column_selector import ColumnsSelector, ColumnsSelectorResult
from msg_box import MessageBox
from tkhtmlview import HTMLLabel
from components import Component, ComponentsDB, ComponentsMRU
from config import Config
from project import Project

# -----------------------------------------------------------------------------

APP_NAME = "Yedytor v1.4.1"
APP_DATE = "(c) 2023-2025"

# -----------------------------------------------------------------------------

def get_db_directory() -> str:
    db_path = os.path.dirname(__file__)
    db_path = os.path.join(db_path, "..")
    db_path = os.path.abspath(db_path)
    db_path = os.path.join(db_path, "db")
    return db_path

def get_logs_directory() -> str:
    logs_path = os.path.dirname(__file__)
    logs_path = os.path.join(logs_path, "..")
    logs_path = os.path.abspath(logs_path)
    logs_path = os.path.join(logs_path, "logs")
    return logs_path

# -----------------------------------------------------------------------------

# global instance
glob_proj = Project()
glob_components = ComponentsDB()

# -----------------------------------------------------------------------------

class HomeFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "app" in kwargs
        self.app = kwargs.pop("app")

        super().__init__(master, **kwargs)

        self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        lbl_pnp_path = customtkinter.CTkLabel(self, text="PnP path:")
        lbl_pnp_path.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.var_pnp = customtkinter.StringVar(value="")
        self.entry_pnp_path = customtkinter.CTkEntry(self, textvariable=self.var_pnp)
        self.entry_pnp_path.grid(row=0, column=1, pady=5, padx=5, columnspan=3, sticky="we")
        self.entry_pnp_path.configure(state=tkinter.DISABLED)

        btn_browse_pnp = customtkinter.CTkButton(self, text="Browse...", width=20, command=self.button_browse_pnp_event)
        btn_browse_pnp.grid(row=0, column=4, pady=5, padx=5, sticky="e")

        #
        lbl_pnp2_path = customtkinter.CTkLabel(self, text="PnP2 (optional):")
        lbl_pnp2_path.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.var_pnp2 = customtkinter.StringVar(value="")
        self.entry_pnp2_path = customtkinter.CTkEntry(self, textvariable=self.var_pnp2)
        self.entry_pnp2_path.grid(row=2, column=1, pady=5, padx=5, columnspan=3, sticky="we")
        self.entry_pnp2_path.configure(state=tkinter.DISABLED)

        # Board view TOP
        if True:
            lbl_board_top_path = customtkinter.CTkLabel(self, text="Board view TOP (optional):")
            lbl_board_top_path.grid(row=3, column=0, pady=5, padx=5, sticky="w")

            self.var_board_top_path = customtkinter.StringVar(value="")
            self.entry_board_top_path = customtkinter.CTkEntry(self, textvariable=self.var_board_top_path)
            self.entry_board_top_path.grid(row=3, column=1, pady=5, padx=5, columnspan=2, sticky="we")
            self.entry_board_top_path.configure(state=tkinter.DISABLED)

            btn_browse_board_top = customtkinter.CTkButton(self, text="Browse...", width=20, command=self.button_browse_board_top_event)
            btn_browse_board_top.grid(row=3, column=3, pady=5, padx=5, sticky="e")
            btn_browse_board_top.configure(state=tkinter.DISABLED)

            btn_show_board_top = customtkinter.CTkButton(self, text="Show", width=20, command=self.button_show_board_top_event)
            btn_show_board_top.grid(row=3, column=4, pady=5, padx=5,  sticky="")
            btn_show_board_top.configure(state=tkinter.DISABLED)

        # Board view BOT
        if True:
            lbl_board_bottom_path = customtkinter.CTkLabel(self, text="Board view BOT (optional):")
            lbl_board_bottom_path.grid(row=4, column=0, pady=5, padx=5, sticky="w")

            self.var_board_bot_path = customtkinter.StringVar(value="")
            self.entry_board_bot_path = customtkinter.CTkEntry(self, textvariable=self.var_board_bot_path)
            self.entry_board_bot_path.grid(row=4, column=1, pady=5, padx=5, columnspan=2, sticky="we")
            self.entry_board_bot_path.configure(state=tkinter.DISABLED)

            btn_browse_board_bot = customtkinter.CTkButton(self, text="Browse...", width=20, command=self.button_browse_board_bot_event)
            btn_browse_board_bot.grid(row=4, column=3, pady=5, padx=5, sticky="e")
            btn_browse_board_bot.configure(state=tkinter.DISABLED)

            btn_show_board_bot = customtkinter.CTkButton(self, text="Show", width=20, command=self.button_show_board_bot_event)
            btn_show_board_bot.grid(row=4, column=4, pady=5, padx=5, sticky="")
            btn_show_board_bot.configure(state=tkinter.DISABLED)

        #
        sep_h = tkinter.ttk.Separator(self, orient='horizontal')
        sep_h.grid(row=5, column=0, pady=5, padx=5, columnspan=5, sticky="we")

        #
        self.wip = customtkinter.CTkFrame(self)
        self.wip.grid(row=6, column=0, pady=5, padx=5, columnspan=5, sticky="we")

        self.wip.lbl_msg = customtkinter.CTkLabel(self.wip, text="Restore previous Work In Progress")
        self.wip.lbl_msg.grid(row=0, column=0, pady=5, padx=5, columnspan=2, sticky="w")

        self.wip.btn_load = customtkinter.CTkButton(self.wip, text="Browse ...",
                                                    command=self.button_browse_wip_event)
        self.wip.btn_load.grid(row=0, column=2, pady=5, padx=5, sticky="e")

        #
        sep_h = tkinter.ttk.Separator(self, orient='horizontal')
        sep_h.grid(row=7, column=0, pady=5, padx=5, columnspan=5, sticky="we")

        #
        self.config_pnpedit = customtkinter.CTkFrame(self)
        self.config_pnpedit.grid(row=8, column=0, pady=5, padx=5, columnspan=1, sticky="we")
        self.config_pnpedit.lbl_font = customtkinter.CTkLabel(self.config_pnpedit, text="PnP Editor Font:")
        self.config_pnpedit.lbl_font.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.config_pnpedit.radio_var = tkinter.IntVar(value=Config.instance().editor_font_idx)
        self.config_pnpedit.rb_font0 = customtkinter.CTkRadioButton(self.config_pnpedit, text="12px",
                                                                variable=self.config_pnpedit.radio_var,
                                                                value=0, command=self.radiobutton_event)
        self.config_pnpedit.rb_font0.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.config_pnpedit.rb_font1 = customtkinter.CTkRadioButton(self.config_pnpedit, text="16px",
                                                                variable=self.config_pnpedit.radio_var,
                                                                value=1, command=self.radiobutton_event)
        self.config_pnpedit.rb_font1.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        #
        self.config_pnpedit.lbl_summary_cnt = customtkinter.CTkLabel(self.config_pnpedit, text="Summary report:")
        self.config_pnpedit.lbl_summary_cnt.grid(row=3, column=0, pady=5, padx=5, sticky="w")

        self.config_pnpedit.summary_com_count_var = customtkinter.BooleanVar(value=Config.instance().summary_comp_count)
        self.config_pnpedit.chx_summary_com_count = customtkinter.CTkCheckBox(self.config_pnpedit,
                                                        text="Number of components",
                                                        command=self.checkbox_summary_com_count_event,
                                                        variable=self.config_pnpedit.summary_com_count_var,
                                                        checkbox_width=18, checkbox_height=18)
        self.config_pnpedit.chx_summary_com_count.grid(row=4, column=0, pady=5, padx=5, sticky="w")

        #
        self.config_logs = customtkinter.CTkFrame(self)
        self.config_logs.grid(row=8, column=1, pady=5, padx=5, columnspan=1, sticky="wns")

        self.config_logs.lbl_font = customtkinter.CTkLabel(self.config_logs, text="Console:")
        self.config_logs.lbl_font.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.config_logs.colorlogs_var = customtkinter.BooleanVar(value=Config.instance().color_logs)
        self.config_logs.chx_color_logs = customtkinter.CTkCheckBox(self.config_logs,
                                                        text="Colorful logs",
                                                        command=self.checkbox_color_logs_event,
                                                        variable=self.config_logs.colorlogs_var,
                                                        checkbox_width=18, checkbox_height=18)
        self.config_logs.chx_color_logs.grid(row=1, column=0, pady=5, padx=5, sticky="w")

    def radiobutton_event(self):
        Config.instance().editor_font_idx = self.config_pnpedit.radio_var.get()
        # logger.debug(f"RB event: {self.config_font.editor_font_idx}")
        Config.instance().save()

    def checkbox_color_logs_event(self):
        Config.instance().color_logs = self.config_logs.colorlogs_var.get()
        Config.instance().save()

    def checkbox_summary_com_count_event(self):
        Config.instance().summary_comp_count = self.config_pnpedit.summary_com_count_var.get()
        Config.instance().save()

    def clear_pnp_previews(self):
        loading_bkp = glob_proj.loading
        try:
            glob_proj.loading = True
            self.var_pnp.set("")
            self.var_pnp2.set("")
            self.pnp_view.clear_preview()
            self.pnp_config.entry_first_row_var.set("1")
            self.pnp_config.btn_columns.configure(state=tkinter.DISABLED)
        finally:
            glob_proj.loading = loading_bkp

    def button_browse_pnp_event(self):
        logger.debug("Browse for PnP")
        self.load_pnp()

    def button_browse_board_top_event(self):
        logger.debug("Browse for TOP jpeg")
        image_path = self._filedialog_image("TOP")
        if os.path.isfile(image_path):
            logger.info(f"Selected image: {image_path}")
            self.var_board_top_path.set(image_path)
            glob_proj.board_top_path = image_path
            Config.instance().recent_board_top_path = image_path
            Config.instance().save()

    def button_browse_board_bot_event(self):
        logger.debug("Browse for BOT jpeg")
        image_path = self._filedialog_image("BOTTOM")
        if os.path.isfile(image_path):
            logger.info(f"Selected image: {image_path}")
            self.var_board_bot_path.set(image_path)
            glob_proj.board_bot_path = image_path
            Config.instance().recent_board_bot_path = image_path
            Config.instance().save()

    def _filedialog_image(self, layer : str) -> str:
        # https://docs.python.org/3/library/dialog.html
        image_path = tkinter.filedialog.askopenfilename(
            title=f"Select boart {layer} view",
            initialdir=None,
            filetypes = [
                ("Image files", "*.jpg;*.jpeg;*.png;*.bmp")
            ],
        )
        return image_path

    def button_show_board_top_event(self):
        logger.debug("Show TOP jpeg")
        board_view.BoardView(app=self.app, image_path=glob_proj.board_top_path)

    def button_show_board_bot_event(self):
        logger.debug("Show BOTTOM jpeg")
        board_view.BoardView(app=self.app, image_path=glob_proj.board_bot_path)

    def load_pnp(self):
        self.clear_pnp_previews()

        # https://docs.python.org/3/library/dialog.html
        pnp_paths = tkinter.filedialog.askopenfilenames(
            title="Select PnP file(s)",
            initialdir=None,
            filetypes = [
                ("All text files", ".*")
            ],
        )
        logger.info(f"Selected PnP(s): {pnp_paths}")

        if len(pnp_paths) > 2:
            MessageBox(app=self.app, dialog_type="o",
                    message="You can only select one or two PnP files of the same type",
                    callback=lambda btn: btn)
            return

        if len(pnp_paths) == 2:
            # https://docs.python.org/3/library/os.path.html#os.path.splitext
            ext1 = os.path.splitext(pnp_paths[0])[1].lower()
            ext2 = os.path.splitext(pnp_paths[1])[1].lower()
            if ext1 != ext2:
                MessageBox(app=self.app, dialog_type="o",
                        message="You must select two PnP files of the same type",
                        callback=lambda btn: btn)
                return

        self.process_input_files(pnp_paths)

    def button_browse_wip_event(self):
        # https://docs.python.org/3/library/dialog.html
        wip_path = tkinter.filedialog.askopenfile(
            mode="r",
            title="Open the PnP editor wip.json file",
            initialdir=None,
            filetypes = [
                ("JSON", "*_wip.json"),
                ("All files", ".*")
            ],
        )

        if wip_path:
            self.clear_pnp_previews()
            logger.info(f"Selected WiP: {wip_path.name}")

            wip = pnp_editor_helpers.wip_load(wip_path.name, )
            if not wip[0]:
                MessageBox(app=self.app, dialog_type="o",
                            message=wip[1],
                            callback=lambda btn: btn)
                return

            logger.info("Restore project...")

            # reset entire project
            global glob_proj
            glob_proj = Project()

            try:
                glob_proj.loading = True
                glob_proj.from_serializable(wip[2]['project'])
                glob_proj.wip_path = wip_path.name

                self.app.title(f"{APP_NAME} - {glob_proj.pnp_path} (WiP)")

                logger.info("  Restore PnP editor content...")
                self.app.pnp_editor.load(wip[2]['components'])
                logger.info("Open the PnP editor page")
                self.app.get_tab_select_editor_fn()()
            finally:
                glob_proj.loading = False

    def process_input_files(self, pnp_paths: list[str]):
        try:
            glob_proj.loading = True
            self._process_input_files(pnp_paths)
        finally:
            glob_proj.loading = False

    def _process_input_files(self, pnp_paths: list[str]):
        if len(pnp_paths) > 0 and os.path.isfile(pnp_paths[0]):
            try:
                # reset entire project
                global glob_proj
                sep_backup = glob_proj.pnp_separator
                # first_row_backup = glob_proj.pnp_first_row
                loading_backup = glob_proj.loading

                glob_proj = Project()
                glob_proj.pnp_separator = sep_backup
                # glob_proj.pnp_first_row = first_row_backup
                glob_proj.loading = loading_backup
                glob_proj.pnp_path = pnp_paths[0]
                glob_proj.pnp2_path = pnp_paths[1] if len(pnp_paths) > 1 else ""
                self.var_pnp.set(glob_proj.pnp_path)
                self.var_pnp2.set(glob_proj.pnp2_path)
                self.setup_pnp_config_pane()
                # reset the CSV filename postfix
                self.pnp_editor.entry_csv_postfix.set_text("")
                self.pnp_editor.entry_csv_postfix.put_placeholder()
                self.app.title(f"{APP_NAME} - {glob_proj.pnp_path}")

            except Exception as e:
                logger.error(f"Cannot open file: {e}")

            Config.instance().recent_pnp_path = pnp_paths
            Config.instance().save()
        else:
            if len(pnp_paths):
                logger.error(f"Cannot access the file '{pnp_paths[0]}'")

    def restore_board_preview_paths(self, top_path: str, bot_path: str):
        glob_proj.board_top_path = top_path
        glob_proj.board_bot_path = bot_path
        self.var_board_top_path.set(top_path)
        self.var_board_bot_path.set(bot_path)

    def setup_pnp_config_pane(self):
        self.activate_csv_separator()
        last_colsel_result = ColumnsSelectorResult()

        if recent_sett := Config.instance().read_settings(glob_proj.pnp_path):
            self.pnp_config.entry_first_row_var.set(str(int(recent_sett["pnp_first_row"]) + 1))
            self.pnp_config.opt_separator_var.set(recent_sett["pnp_separator"])
            self.pnp_config.btn_goto_editor.configure(state=tkinter.NORMAL)
            # load the columns selection from the history
            last_colsel_result.deserialize(recent_sett["pnp_columns"])
            glob_proj.pnp_first_row = int(recent_sett["pnp_first_row"])
            glob_proj.pnp_separator = recent_sett["pnp_separator"]
            glob_proj.pnp2_path = recent_sett["pnp2_path"]
        else:
            glob_proj.pnp_first_row = 0
            self.pnp_config.entry_first_row_var.set("1")
            # check the old settings ([columns] section is deprecated)
            history_key = glob_proj.get_name().replace(" ", "_").replace(":", "_")
            cols_serialized = Config.instance().get_section("columns").get(history_key, fallback="")
            if cols_serialized != "":
                last_colsel_result.deserialize(cols_serialized)

        glob_proj.pnp_columns = last_colsel_result

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

        self.entry_search = ui_helpers.EntryWithPPM(self)
        self.entry_search.grid(row=1, column=0, padx=5, pady=5, sticky="we")

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

    def clear_preview(self):
        self.textbox.delete("0.0", tkinter.END)

    def button_find_event(self):
        txt = self.entry_search.get()
        logger.info(f"Find '{txt}'")
        cnt = ui_helpers.textbox_find_text(self.textbox, txt)
        self.lbl_occurences.configure(text=f"Found: {cnt}")

# -----------------------------------------------------------------------------

class PnPConfig(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "app" in kwargs
        self.app = kwargs.pop("app")

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
        self.entry_first_row_var.trace_add("write", lambda n, i, m,
                                           sv=self.entry_first_row_var: self.var_first_row_event(sv))
        self.entry_first_row = customtkinter.CTkEntry(self, width=60,
                                                      placeholder_text="first row",
                                                      textvariable=self.entry_first_row_var)
        self.entry_first_row.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        #
        self.btn_load_pnp_preview = customtkinter.CTkButton(self, text="Reload PnP",
                                                command=self.button_load_pnp_preview_event)
        self.btn_load_pnp_preview.grid(row=0, column=3, pady=5, padx=5, sticky="e")

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
        self.btn_goto_editor = customtkinter.CTkButton(self, text="Go to\nEditor →", state=tkinter.DISABLED,
                                                command=self.button_goto_editor_event)
        self.btn_goto_editor.grid(row=0, column=8, pady=5, padx=5, sticky="")

    def opt_separator_event(self, new_sep: str):
        if glob_proj.loading:
            return

        logger.info(f"  PnP separator: {new_sep}")
        glob_proj.pnp_separator = new_sep
        self.button_load_pnp_preview_event()

    def var_first_row_event(self, sv: customtkinter.StringVar):
        if glob_proj.loading:
            return

        if (new_first_row := sv.get().strip()) != "":
            try:
                glob_proj.pnp_first_row = int(new_first_row) - 1
                logger.info(f"  PnP 1st row: {glob_proj.pnp_first_row+1}")
                self.button_load_pnp_preview_event()
            except Exception as e:
                logger.error(f"  Invalid row number: {e}")

    def button_load_pnp_preview_event(self):
        logger.debug("Load PnP...")
        try:
            self.pnp_view.load_pnp(glob_proj.pnp_path, glob_proj.pnp2_path)
            # refresh editor (if columns were selected)
            # if glob_proj.pnp_columns.valid:
            #     self.pnp_editor.load()
            self.btn_columns.configure(state=tkinter.NORMAL)
        except Exception as e:
            logger.error(f"Cannot load PnP: {e}")

    def update_lbl_columns(self):
        # self.lbl_columns.configure(
            # text=f"COLUMNS:\n• Footprint: {glob_proj.pnp_columns.footprint_col}\n• Comment: {glob_proj.pnp_columns.comment_col}")
        pass

    def button_columns_event(self):
        logger.debug("Select PnP columns...")
        if glob_proj.pnp_grid:
            columns = list.copy(glob_proj.pnp_grid.rows_raw()[glob_proj.pnp_first_row])
        else:
            columns = ["..."]

        if self.column_selector:
            self.column_selector.destroy()

        # show the column selector
        self.column_selector = ColumnsSelector(self, app=self.app, columns=columns,
                                               callback=self.column_selector_callback,
                                               last_result=glob_proj.pnp_columns)

    def column_selector_callback(self, result: ColumnsSelectorResult):
        logger.debug(f"Selected PnP columns: {result.tostr()}")
        glob_proj.pnp_columns = result
        self.update_lbl_columns()
        if result.valid:
            self.btn_goto_editor.configure(state=tkinter.NORMAL)

    def button_goto_editor_event(self):
        try:
            Config.instance().write_settings(
                glob_proj.pnp_path, glob_proj.pnp_separator,
                glob_proj.pnp_first_row,
                glob_proj.pnp_columns.serialize(), glob_proj.pnp2_path
            )
            Config.instance().save()
        except Exception as e:
            logger.error(f"Cannot save a recent project settings: {e}")

        if glob_proj.pnp_grid:
            logger.info("Load PnP editor content...")
            self.pnp_editor.load()
            logger.info("Open the PnP editor page")
            self.select_editor()
        else:
            logger.warning("PnP file not loaded")

# -----------------------------------------------------------------------------

class PnPEditor(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert 'app' in kwargs
        self.app = kwargs.pop('app')
        super().__init__(master, **kwargs)

        self.editor_data = pnp_editor_helpers.PnPEditorData()

        # top toolbar
        if True:
            self.frame_toolbar = customtkinter.CTkFrame(self)
            self.frame_toolbar.grid(row=0, column=0, pady=5, padx=5, columnspan=7, sticky="we")

            # change components page, view contains up to self.COMP_PER_PAGE items
            self.btn_page_prev = customtkinter.CTkButton(self.frame_toolbar, text="<", command=self.button_prev_event)
            self.btn_page_prev.grid(row=0, column=1, pady=5, padx=5, sticky="w")

            self.lbl_pageno = customtkinter.CTkLabel(self.frame_toolbar, text=self.format_pageno())
            self.lbl_pageno.grid(row=0, column=2, pady=5, padx=5, sticky="w")

            self.btn_page_next = customtkinter.CTkButton(self.frame_toolbar, text=">", command=self.button_next_event)
            self.btn_page_next.grid(row=0, column=3, pady=5, padx=5, sticky="w")

            sep_v = tkinter.ttk.Separator(self.frame_toolbar, orient='vertical')
            sep_v.grid(row=0, column=4, pady=2, padx=5, sticky="ns")

            #
            self.radio_filter_var = tkinter.IntVar(value=0)
            self.rb_show_all = customtkinter.CTkRadioButton(self.frame_toolbar, text="All components",
                                                                    variable=self.radio_filter_var,
                                                                    value=0, command=self.radiobutton_event)
            self.rb_show_all.grid(row=0, column=5, pady=5, padx=5, sticky="")
            #
            self.rb_show_notconfigured = customtkinter.CTkRadioButton(self.frame_toolbar, text="Not configured",
                                                                    variable=self.radio_filter_var,
                                                                    value=1, command=self.radiobutton_event)
            self.rb_show_notconfigured.grid(row=0, column=6, pady=5, padx=5, sticky="")
            #
            self.rb_show_notconfigured = customtkinter.CTkRadioButton(self.frame_toolbar, text="Configured",
                                                                    variable=self.radio_filter_var,
                                                                    value=2, command=self.radiobutton_event)
            self.rb_show_notconfigured.grid(row=0, column=7, pady=5, padx=5, sticky="")
            #
            self.rb_show_notconfigured = customtkinter.CTkRadioButton(self.frame_toolbar, text="Removed",
                                                                    variable=self.radio_filter_var,
                                                                    value=3, command=self.radiobutton_event)
            self.rb_show_notconfigured.grid(row=0, column=8, pady=5, padx=5, sticky="")

            #
            sep_v = tkinter.ttk.Separator(self.frame_toolbar, orient='vertical')
            sep_v.grid(row=0, column=9, pady=2, padx=5, sticky="ns")


        # bottom toolbar
        if True:
            self.pgbar_selected = customtkinter.CTkProgressBar(self)
            self.pgbar_selected.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
            self.pgbar_selected.set(0)

            self.lbl_selected = tkinter.Label(self, text="0 / 0")
            self.lbl_selected.grid(row=3, column=1, padx=5, pady=5, sticky="w")

            sep_v = tkinter.ttk.Separator(self, orient='vertical')
            sep_v.grid(row=3, column=2, pady=2, padx=5, sticky="ns")

            self.btn_save_wip = customtkinter.CTkButton(self, text="Save for later", command=self.button_save_wip_event)
            self.btn_save_wip.grid(row=3, column=3, pady=5, padx=5, sticky="e")

            sep_v = tkinter.ttk.Separator(self, orient='vertical')
            sep_v.grid(row=3, column=4, pady=2, padx=5, sticky="ns")

            self.entry_csv_postfix = ui_helpers.EntryWithPPM(self, placeholder_text="< filename postfix >")
            self.entry_csv_postfix.grid(row=3, column=5, padx=5, pady=2, sticky="we")

            self.btn_save = customtkinter.CTkButton(self, text="Save PnP as new CSV", command=self.button_save_event)
            self.btn_save.grid(row=3, column=6, pady=5, padx=5, sticky="e")
            self.btn_save.configure(state=tkinter.DISABLED)

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

        # apply font to ALL application combobox list
        self.app.option_add('*TCombobox*Listbox.font', self.fonts[Config.instance().editor_font_idx][0])
        self.app.option_add('*TCombobox*Listbox.background', 'LightBlue')
        # static editor
        self.create_editor()
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def format_pageno(self) -> str:
        pages_cnt = 1 + len(self.editor_data.items_filtered()) // self.editor_data.ITEMS_PER_PAGE
        pageno_str = f"{1 + self.editor_data.page_no} / {pages_cnt}"
        return pageno_str

    def button_prev_event(self):
        if (self.editor_data.page_no > 0):
            self.editor_data.page_no -= 1
            self.editor_load_data()
            self.lbl_pageno.configure(text=self.format_pageno())

    def button_next_event(self):
        last_page = len(self.editor_data.items_filtered()) // self.editor_data.ITEMS_PER_PAGE
        if self.editor_data.page_no < last_page:
            self.editor_data.page_no += 1
            self.editor_load_data()
            self.lbl_pageno.configure(text=self.format_pageno())

    def radiobutton_event(self):
        filter_idx = self.radio_filter_var.get()
        logger.info(f"Selected component filter: {filter_idx}")
        self.editor_data.set_items_filter(filter_idx)
        self.editor_load_data()
        logger.info(f"  Editor reloaded")
        self.lbl_pageno.configure(text=self.format_pageno())

    def create_editor(self):
        self.focused_idx = None

        self.entry_summary_list: list[tkinter.Entry] = []
        self.entry_descr_list: list[tkinter.Entry] = []
        self.lbl_marker_list = []
        self.cbx_component_list = []
        self.lbl_namelength_list = []
        self.cbx_rotation_list = []

        self.scrollableframe = customtkinter.CTkScrollableFrame(self)
        self.scrollableframe.grid(row=1, column=0, padx=5, pady=1, columnspan=7, sticky="wens")

        # Header row
        if True:
            lbl = tkinter.Label(self.scrollableframe, text="Component ID + Footprint + Value")
            lbl.grid(row=0, column=0, padx=5, pady=1, sticky="we")

            lbl = tkinter.Label(self.scrollableframe, text="Description")
            lbl.grid(row=0, column=1, padx=5, pady=1, sticky="we")

            lbl = tkinter.Label(self.scrollableframe, text="✔")
            lbl.grid(row=0, column=2, padx=5, pady=1, sticky="")

            lbl = tkinter.Label(self.scrollableframe, text="Yamaha DB component")
            lbl.grid(row=0, column=3, padx=5, pady=1, sticky="we")

            lbl = tkinter.Label(self.scrollableframe, text="Rotation")
            lbl.grid(row=0, column=5, padx=6, pady=1, sticky="we")

        # Components table:
        for idx in range(1, pnp_editor_helpers.PnPEditorData.ITEMS_PER_PAGE+1):
            # --- summary
            # menuitems="" -> means no menu at all (number of menus to be created is limited)
            entry_summary = ui_helpers.EntryWithPPM(
                self.scrollableframe, menuitems="c",
                font=self.fonts[Config.instance().editor_font_idx][0])
            entry_summary.grid(row=idx, column=0, padx=5, pady=1, sticky="we")
            entry_summary.bind("<FocusIn>", self.focus_in)
            self.entry_summary_list.append(entry_summary)

            # --- descr
            entry_descr = ui_helpers.EntryWithPPM(
                self.scrollableframe,
                font=self.fonts[Config.instance().editor_font_idx][0])
            entry_descr.grid(row=idx, column=1, padx=5, pady=1, sticky="we")
            entry_descr.bind("<FocusIn>", self.focus_in)
            self.entry_descr_list.append(entry_descr)

            # --- selection marker
            lbl_marker = tkinter.Label(self.scrollableframe, text=" ")
            lbl_marker.grid(row=idx, column=2, padx=5, pady=1, sticky="")
            self.lbl_marker_list.append(lbl_marker)

            cbx_component = ui_helpers.ComboboxWithPPM(
                self.scrollableframe, menuitems="cp@",
                font=self.fonts[Config.instance().editor_font_idx][0])
            self.cbx_components_add_context_menu(cbx_component)
            cbx_component.grid(row=idx, column=3, padx=5, pady=1, sticky="we")
            cbx_component.bind('<<ComboboxSelected>>', self.cbx_components_selected)
            # cbx_component.bind('<Key>', self.combobox_key)
            cbx_component.bind("<Return>", self.cbx_components_return)
            cbx_component.bind("<MouseWheel>", self.cbx_wheel)
            cbx_component.bind("<FocusIn>", self.focus_in)
            self.cbx_component_list.append(cbx_component)

            # --- component name length
            lbl_length = tkinter.Label(
                self.scrollableframe,
                font=self.fonts[Config.instance().editor_font_idx][0])
            lbl_length.grid(row=idx, column=4, padx=1, pady=1, sticky="e")
            lbl_length.config(foreground="maroon")
            self.lbl_namelength_list.append(lbl_length)

            # --- component rotation
            cbx_rotation = tkinter.ttk.Combobox(
                self.scrollableframe, width=5,
                values=("0", "90", "180", "270"),
                font=self.fonts[Config.instance().editor_font_idx][0])
            cbx_rotation.grid(row=idx, column=5, padx=5, pady=1, sticky="we")
            cbx_rotation.bind('<<ComboboxSelected>>', self.cbx_rotation_selected)
            cbx_rotation.bind("<Return>", self.cbx_rotation_return)
            cbx_rotation.bind("<MouseWheel>", self.cbx_wheel)
            cbx_rotation.bind("<FocusIn>", self.focus_in)
            self.cbx_rotation_list.append(cbx_rotation)

            self.scrollableframe.grid_columnconfigure(0, weight=3)
            self.scrollableframe.grid_columnconfigure(3, weight=1)

            # to display long descriptions:
            self.entry_descr_long = ui_helpers.EntryWithPPM(
                self, menuitems="c", # state=tkinter.DISABLED,
                placeholder_text="< long description preview >",
                font=self.fonts[Config.instance().editor_font_idx][0])
            self.entry_descr_long.grid(row=2, column=0, columnspan=7, padx=15, pady=1, sticky="we")
            self.update_component_description_long("") # to activate placeholder text

    def load(self, wip_items: list[dict] = None):
        self.btn_save.configure(state=tkinter.DISABLED)
        self.wip_items = wip_items
        self.radio_filter_var.set(0)

        if (not glob_proj.pnp_grid) or (glob_proj.pnp_grid.nrows == 0):
            logger.warning("PnP file not loaded")
            return

        # if we are here, user already selected the PnP file first row
        glob_proj.pnp_grid.firstrow = max(0, glob_proj.pnp_first_row)
        glob_proj.pnp_grid.firstrow += 1 if glob_proj.pnp_columns.has_column_headers else 0

        if not self.check_selected_columns():
            logger.warning("Select proper Footprint and Comment columns before editing")
            return

        self.component_names = glob_components.names_visible()

        # find the max comment width
        footprint_max_w = 0
        id_max_w = 0
        for row in glob_proj.pnp_grid.rows():
            footprint_max_w = max(footprint_max_w, len(row[glob_proj.pnp_columns.footprint_col]))
            id_max_w = max(id_max_w, len(row[0]))

        if True:
            logger.info(f"Preparing editor data...")
            started_at = time.monotonic()
            try:
                self.editor_data = pnp_editor_helpers.prepare_editor_data(glob_components, glob_proj, self.wip_items)
            except Exception as e:
                logger.error(f"Failed to prepare data: {e}")
                return
            delta = time.monotonic() - started_at
            delta = f"{delta:.1f}s"
            logger.info(f"  {len(self.editor_data.items_filtered())} items prepared in {delta}")

        self.lbl_pageno.configure(text=self.format_pageno())
        self.editor_load_data()

    def editor_load_data(self):
        # Components table:
        pnpitem_start_idx = self.editor_data.items_visible_offset()
        pnpitem_end_idx = min(len(self.editor_data.items_filtered()), pnpitem_start_idx + self.editor_data.ITEMS_PER_PAGE)
        wgt_idx = 0 # must be declared outside the loop, as the range may be empty

        for pnpitem_idx in range(pnpitem_start_idx, pnpitem_end_idx):
            pnp_item = self.editor_data.items_filtered()[pnpitem_idx]
            # summary:
            ui_helpers.entry_set_text(self.entry_summary_list[wgt_idx], pnp_item.summary)
            # descr
            ui_helpers.entry_set_text(self.entry_descr_list[wgt_idx], pnp_item.descr)
            # marker:
            self.lbl_marker_list[wgt_idx].config(background=pnp_item.marker.color)
            # component list:
            self.cbx_component_list[wgt_idx].set(pnp_item.editor_selection)
            self.cbx_component_list[wgt_idx].configure(values=pnp_item.editor_cbx_items)
            # comp. name length:
            self.update_componentname_length_lbl(self.lbl_namelength_list[wgt_idx], pnp_item.editor_selection)
            # rotation:
            self.cbx_rotation_list[wgt_idx].set(pnp_item.rotation)
            #
            wgt_idx += 1

        # clear unused rows
        for idx in range(wgt_idx, pnp_editor_helpers.PnPEditorData.ITEMS_PER_PAGE):
            ui_helpers.entry_set_text(self.entry_summary_list[idx], 0)
            # entry_pnp.configure(state=tkinter.DISABLED)
            ui_helpers.entry_set_text(self.entry_descr_list[idx], "")
            self.lbl_marker_list[idx].config(background="white")
            self.cbx_component_list[idx].set("")
            self.cbx_component_list[idx].configure(values=[])
            self.lbl_namelength_list[idx].configure(text="")
            self.cbx_rotation_list[idx].set("")

        # scroll the list to the top
        ui_helpers.scrollable_moveto_top(self.scrollableframe)

        # to activate placeholder text
        self.update_component_description_long("")
        # update progressbar
        self.update_selected_status()

    def update_componentname_length_lbl(self, lbl: tkinter.Label, comp_name: str):
        COMPONENT_MAX_LEN = 38
        name_len = len(comp_name)

        if name_len < COMPONENT_MAX_LEN:
            lbl.configure(text="")
        else:
            lbl.configure(text=f"+{name_len-COMPONENT_MAX_LEN}")

    def update_component_description_long(self, descr: str):
        ui_helpers.entry_set_text(self.entry_descr_long, descr)

    def check_selected_columns(self) -> bool:
        if not glob_proj.pnp_columns.valid:
            return False
        return glob_proj.pnp_columns.footprint_col < glob_proj.pnp_grid.ncols \
           and glob_proj.pnp_columns.comment_col < glob_proj.pnp_grid.ncols

    def cbx_components_selected(self, event):
        wgt_idx = self.cbx_component_list.index(event.widget)
        selected_component: str = event.widget.get().strip()

        if pnp_item := self.editor_data.item_filtered_paginated(wgt_idx):
            logger.debug(f"Apply '{selected_component}' to item {pnp_item.id} (filter: '{pnp_item.editor_filter}')")

            if selected_component == ComponentsMRU.SPACER_ITEM:
                logger.debug("  spacer - selection ignored")
                # restore filter value
                event.widget.set(pnp_item.editor_filter)
                return

            self.apply_component_to_matching(wgt_idx, selected_component)
            # update the MRU
            glob_components.mru_items.on_select(pnp_item.editor_filter, selected_component)

            # update drop-down list so it contains the new MRU items
            filtered_comp_names = list(component.name for component in glob_components.components_filtered(pnp_item.editor_filter))
            glob_components.mru_items.arrange(pnp_item.editor_filter, filtered_comp_names)

            pnp_item.editor_selection = selected_component
            pnp_item.editor_cbx_items = filtered_comp_names
            pnp_item.marker.value = Marker.MAN_SEL
            event.widget.configure(values=pnp_item.editor_cbx_items)
            self.btn_save.configure(state=tkinter.NORMAL)

    def apply_component_to_matching(self, wgt_idx: int, selected_component: str, force: bool = False):
        try:
            # get the selection details:
            absolute_idx = self.editor_data.item_absolute_index_from_widget_filtered_paginated_index(wgt_idx)
            if absolute_idx is None:
                logger.error(f"Internal error: pnp item at {wgt_idx} not found")
                return

            comment_ref = glob_proj.pnp_grid.rows()[absolute_idx][glob_proj.pnp_columns.comment_col]
            ftprint_ref = glob_proj.pnp_grid.rows()[absolute_idx][glob_proj.pnp_columns.footprint_col]
            invalidated_pnp_items = []

            # traverse all items and if comment:footprint matches -> apply
            for pnp_idx, pnp_item in enumerate(self.editor_data.items_all()):
                if pnp_idx == absolute_idx:
                    # add marker that this is a final value
                    pnp_item.marker.value = Marker.MAN_SEL
                    invalidated_pnp_items.append(pnp_item)
                    # widget from event source, so we can skip this one
                    continue

                # if already selected, skip this item
                if not force and (pnp_item.marker.value in (Marker.MAN_SEL, Marker.REMOVED)):
                    continue

                if pnp_item.comment == comment_ref and pnp_item.footprint == ftprint_ref:
                    # found: select the same component
                    logger.debug(f"  Apply '{selected_component}' to item {pnp_item.id} ({pnp_item.comment})")
                    pnp_item.editor_selection = selected_component
                    invalidated_pnp_items.append(pnp_item)

                    if len(selected_component) >= 3:
                        # add marker that this is a final value
                        pnp_item.marker.value = Marker.MAN_SEL
                    else:
                        # too short -> filter or empty
                        pnp_item.marker.value = Marker.NOMATCH

            pnp_idx = None
            pnp_item = None

            # update visible editor items
            for pnp_item in invalidated_pnp_items:
                if not (wgt_idx := self.editor_data.item_filtered_paginated_index(pnp_item)) is None:
                    self.lbl_marker_list[wgt_idx].config(background=pnp_item.marker.color)
                    self.cbx_component_list[wgt_idx].set(selected_component)
                    self.update_componentname_length_lbl(self.lbl_namelength_list[wgt_idx], selected_component)

        except Exception as e:
            logger.warning(f"Applying selection to the matching items failed: {e}")
        finally:
            self.update_selected_status()

    def add_component_if_missing(self, new_component_name: str):
        new_component_name = new_component_name.strip()
        if glob_components.add_if_not_exists(new_component_name):
            logger.info(f"⭐New component '{new_component_name}' added to the database")
            self.component_names.append(new_component_name)

    # def combobox_key(self, event):
    #     logger.debug(f"CB key: {event}")

    def cbx_components_add_context_menu(self, cbx_component):
        if cbx_component.menu is None:
            return

        # as we are using the same menu for all ComboBoxes, add extra menus only once
        if hasattr(cbx_component.menu, "cbx_extra_menu"):
            return

        menu = cbx_component.menu
        menu.cbx_extra_menu = True

        menu.add_separator()
        #
        menu.add_command(label="Update drop-down items (apply filter)",
                        command=lambda: self.cbx_components_apply_filter(menu.wgt))
        menu.add_separator()
        #
        menu.add_command(label="Set default: <Footprint>_<Comment>",
                        command=lambda: self.cbx_components_set_default(menu.wgt))
        #
        menu.add_command(label="Apply selection to all matching components",
                        command=lambda: self.cbx_components_apply_selected_to_all(menu.wgt, False))
        #
        menu.add_command(label="Apply+override selection to all matching components",
                        command=lambda: self.cbx_components_apply_selected_to_all(menu.wgt, True))
        menu.add_separator()
        #
        menu.add_command(label="Remove component",
                        command=lambda: self.cbx_components_remove_component(menu.wgt))

    def cbx_components_return(self, event):
        self.cbx_components_apply_filter(event.widget)

    def cbx_components_apply_selected_to_all(self, cbx, force: bool):
        cbx.focus_force()
        wgt_idx = self.cbx_component_list.index(cbx)
        selected_component: str = cbx.get().strip()
        logger.debug(f"Applying '{selected_component}':")
        self.apply_component_to_matching(wgt_idx, selected_component, force)
        self.add_component_if_missing(selected_component)
        self.btn_save.configure(state=tkinter.NORMAL)

    def cbx_components_remove_component(self, cbx):
        cbx.focus_force()
        wgt_idx = self.cbx_component_list.index(cbx)
        selected_component: str = self.entry_summary_list[wgt_idx].get()
        # remove double spaces
        selected_component = " ".join(selected_component.split())

        if pnp_item := self.editor_data.item_filtered_paginated(wgt_idx):
            logger.debug(f"Removing: '{selected_component}'")
            # add marker that this is a deleted entry
            pnp_item.marker.value = Marker.REMOVED
            pnp_item.editor_selection = ""
            pnp_item.editor_cbx_items = []

            self.lbl_marker_list[wgt_idx].config(background=pnp_item.marker.color)
            # clear selection
            self.cbx_component_list[wgt_idx].set(pnp_item.editor_selection)
            self.cbx_component_list[wgt_idx].configure(values=pnp_item.editor_cbx_items)
            self.update_selected_status()
            self.btn_save.configure(state=tkinter.NORMAL)

    def cbx_components_set_default(self, cbx):
        wgt_idx = self.cbx_component_list.index(cbx)

        if pnp_item := self.editor_data.item_filtered_paginated(wgt_idx):
            component_name = pnp_item.footprint + "_" + pnp_item.comment
            logger.debug(f"Set default <footprint>_<comment>: '{component_name}'")
            pnp_item.editor_selection = component_name
            pnp_item.marker.value = Marker.FILTER

            cbx.set(component_name)
            self.lbl_marker_list[wgt_idx].config(background=pnp_item.marker.color)
            self.btn_save.configure(state=tkinter.NORMAL)

    def cbx_components_apply_filter(self, cbx):
        filter: str = cbx.get().strip()
        wgt_idx = self.cbx_component_list.index(cbx)

        if len(filter) >= 2:
            filtered_comp_names = list(item.name for item in glob_components.components_filtered(filter))
            logger.info(f"Apply filter '{filter}' -> {len(filtered_comp_names)} matching")
            #
            glob_components.mru_items.arrange(filter, filtered_comp_names)

            if pnp_item := self.editor_data.item_filtered_paginated(wgt_idx):
                pnp_item.editor_filter = filter
                pnp_item.editor_cbx_items = filtered_comp_names
                # set a new combobox items
                cbx.configure(values=pnp_item.editor_cbx_items)

                try:
                    self.component_names.index(filter)
                    # filter found on component list: add marker that this is a final value
                    pnp_item.marker.value = Marker.MAN_SEL
                    self.lbl_marker_list[wgt_idx].config(background=pnp_item.marker.color)
                except Exception:
                    if len(filtered_comp_names) > 0:
                        # mark this is a filter, not value
                        pnp_item.marker.value = Marker.FILTER
                        self.lbl_marker_list[wgt_idx].config(background=pnp_item.marker.color)
                    else:
                        # mark no matching component in database
                        pnp_item.marker.value = Marker.NOMATCH
                        self.lbl_marker_list[wgt_idx].config(background=pnp_item.marker.color)

                    self.update_componentname_length_lbl(self.lbl_namelength_list[wgt_idx], filter)
        else:
            logger.info("Filter too short: use full list")

            if pnp_item := self.editor_data.item_filtered_paginated(wgt_idx):
                pnp_item.editor_cbx_items = self.component_names
                cbx.configure(values=pnp_item.editor_cbx_items)

                try:
                    pnp_item.marker.value = Marker.NOMATCH
                    self.lbl_marker_list[wgt_idx].config(background=pnp_item.marker.color)
                except Exception as e:
                    logger.warning(f"{e}")

        self.btn_save.configure(state=tkinter.NORMAL)

    def cbx_wheel(self, _event):
        # logger.debug(f"CB wheel: {event}")
        # block changing value when the list is hidden to avoid accidental modification
        return 'break'

    def focus_in(self, event):
        # logger.debug(f"focus_in: {event}")
        try:
            # restore normal font on previous item
            if not self.focused_idx is None and self.focused_idx < len(self.entry_summary_list):
                new_font = self.fonts[Config.instance().editor_font_idx][0]
                self.entry_summary_list[self.focused_idx].config(font=new_font)
                self.entry_descr_list[self.focused_idx].config(font=new_font)
                self.cbx_component_list[self.focused_idx].config(font=new_font)
                self.cbx_rotation_list[self.focused_idx].config(font=new_font)

            # set bold font in new item
            #   depending which widget was clicked:
            if event.widget in self.cbx_component_list:
                self.focused_idx = self.cbx_component_list.index(event.widget)
            elif event.widget in self.cbx_rotation_list:
                self.focused_idx = self.cbx_rotation_list.index(event.widget)
            elif event.widget in self.entry_summary_list:
                self.focused_idx = self.entry_summary_list.index(event.widget)
            elif event.widget in self.entry_descr_list:
                self.focused_idx = self.entry_descr_list.index(event.widget)

            new_font = self.fonts[Config.instance().editor_font_idx][1]
            self.entry_summary_list[self.focused_idx].config(font=new_font)
            self.entry_descr_list[self.focused_idx].config(font=new_font)
            self.cbx_component_list[self.focused_idx].config(font=new_font)
            self.cbx_rotation_list[self.focused_idx].config(font=new_font)

            # set the item long description text
            self.update_component_description_long(self.entry_descr_list[self.focused_idx].get())
        except Exception as e:
            logger.debug(f"focus_in: {e}")

    def cbx_rotation_selected(self, event):
        rot: str = event.widget.get().strip()
        logger.debug(f"Rotation selected: {rot}")
        wgt_idx = self.cbx_rotation_list.index(event.widget)

        if pnp_item := self.editor_data.item_filtered_paginated(wgt_idx):
            pnp_item.rotation = rot
            self.btn_save.configure(state=tkinter.NORMAL)

    def cbx_rotation_return(self, event):
        rot: str = event.widget.get().strip()
        logger.debug(f"Rotation entered: {rot}")
        wgt_idx = self.cbx_rotation_list.index(event.widget)

        if pnp_item := self.editor_data.item_filtered_paginated(wgt_idx):
            pnp_item.rotation = rot
            self.btn_save.configure(state=tkinter.NORMAL)

    def entry_focus_in(self, event):
        logger.debug(f"entry_focus_in: {event}")
        try:
            # set the item long description text
            # self.update_component_description_long(self.entry_descr_list[self.focused_idx].get())
            pass
        except Exception as e:
            logger.debug(f"entry_focus_in: {e}")

    def button_save_wip_event(self):
        logger.debug("Saving Work-In-Progress")
        wip_path = os.path.splitext(glob_proj.pnp_path)[0]
        wip_path += "_wip.json"
        self.save_wip(wip_path)

        MessageBox(app=self.app, dialog_type="o",
                    message="Work in progress saved to:\n\n" +
                            f"{os.path.dirname(wip_path)}/\n" +
                            f"{os.path.basename(wip_path)}",
                    callback=lambda btn: btn)

    def save_wip(self, wip_path: str):
        pnp_editor_helpers.wip_save(wip_path, glob_proj.to_serializable(), self.editor_data)

    def button_save_event(self):
        logger.debug("Save PnP")
        n_selected = self.count_selected()
        if n_selected[0] == n_selected[1]:
            self.save_pnp_to_new_csv_file()
            self.btn_save.configure(state=tkinter.DISABLED)
        else:
            MessageBox(app=self.app, dialog_type="yn",
                       message=f"Only {n_selected[0]} / {n_selected[1]} "\
                                "items have selected PnP component.\n\nSave it now?",
                       callback=self.msgbox_save_callback)

    def msgbox_save_callback(self, btn: str):
        if btn == "y":
            self.save_pnp_to_new_csv_file()
            self.btn_save.configure(state=tkinter.DISABLED)

    def save_pnp_to_new_csv_file(self):
        csv_path = glob_proj.pnp_path
        if not os.path.exists(csv_path):
            logger.warning(f"Oryginal file: '{csv_path}' not found")
            if glob_proj.wip_path and os.path.exists(glob_proj.wip_path):
                csv_path : str = glob_proj.wip_path
                csv_path = csv_path.removesuffix("_wip.json")
            else:
                logger.error(f"WiP file: '{csv_path}' also not found")
                return

        output.write_yamaha_csv(self.app, csv_path, self.entry_csv_postfix.get(), glob_proj, self.editor_data)

    def update_selected_status(self):
        n_selected = self.count_selected()
        self.lbl_selected.configure(text=f"{n_selected[0]} / {n_selected[1]}")
        if n_selected[1] > 0:
            self.pgbar_selected.set(n_selected[0] / n_selected[1])
        else:
            self.pgbar_selected.set(0)

    def count_selected(self) -> tuple[int, int]:
        n = 0
        for pnp_item in self.editor_data.items_filtered():
            if pnp_item.marker.value in (Marker.MAN_SEL, Marker.AUTO_SEL, Marker.REMOVED):
                n += 1
        return (n, len(self.editor_data.items_filtered()))

# -----------------------------------------------------------------------------

class ComponentsInfo(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "app" in kwargs
        self.app = kwargs.pop("app")
        assert "callback" in kwargs
        self.on_new_components_callback: Callable = kwargs.pop("callback")

        super().__init__(master, **kwargs)

        self.lblhtml_dbsummary = HTMLLabel(self, wrap='none', height=5)
        self.lblhtml_dbsummary.grid(row=0, column=0, padx=5, pady=5, sticky="wens")

        frame_buttons = customtkinter.CTkFrame(self)
        frame_buttons.grid(row=0, column=1, sticky="")

        btn_tou_scanner = customtkinter.CTkButton(frame_buttons, text="Tou scanner...",
                                                  command=self.btn_tou_scanner_event)
        btn_tou_scanner.grid(row=0, column=0, pady=5, padx=5, sticky="")

        btn_lib_scanner = customtkinter.CTkButton(frame_buttons, text="DevLib scanner...",
                                                  command=self.btn_devlib_scanner_event)
        btn_lib_scanner.grid(row=1, column=0, pady=5, padx=5, sticky="")

        self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)

    def btn_tou_scanner_event(self):
        db_scanner.DbScanner(app=self.app, callback=self.scanner_callback, input_type="tou")

    def btn_devlib_scanner_event(self):
        db_scanner.DbScanner(app=self.app, callback=self.scanner_callback, input_type="devlib")

    def scanner_callback(self, action: str, input_type: str, new_components: ComponentsDB):
        logger.debug(f"Scanner {input_type}: {action}")
        if action == "o":
            # save to a CSV file
            db_directory = get_db_directory()

            if not os.path.isdir(db_directory):
                os.mkdir(db_directory)
            # since the user can add it's own components to the working database,
            # we only add a new components do the working db instead of replacing it with the new one
            global glob_components
            added = glob_components.add_new(new_components.components_all())
            logger.info(f"Added {added} new components to the database")
            glob_components.save_new(db_directory)
            self.update_components_info()
            # update components view
            self.on_new_components_callback()

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
        assert "app" in kwargs
        self.app = kwargs.pop("app")

        super().__init__(master, **kwargs)
        self.components_pageno = 0
        self.component_filter = ""
        self.changed = False

        self.components_info = ComponentsInfo(self, app=self.app, callback=self.reload_components)
        self.components_info.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_components_view()

        self.frame_buttons = customtkinter.CTkFrame(self)
        self.frame_buttons.grid(row=2, column=0, pady=5, padx=5, sticky="we")
        self.frame_buttons.grid_columnconfigure(3, weight=1)

        self.entry_filter_var = customtkinter.StringVar(value="")
        self.entry_filter_var.trace_add("write", lambda n, i, m, sv=self.entry_filter_var: self.var_filter_event(sv))
        self.entry_filter = ui_helpers.EntryWithPPM(self.frame_buttons, width=40, placeholder_text="Filter; use * ?")
        self.entry_filter.grid(row=0, column=0, padx=5, pady=5, sticky="we")
        # textvariable added later to avoid trace event while setting a placeholder text
        self.entry_filter.configure(textvariable=self.entry_filter_var)
        self.entry_filter.put_placeholder()

        # change components page, view contains up to self.COMP_PER_PAGE items
        self.btn_page_prev = customtkinter.CTkButton(self.frame_buttons, text="<", command=self.button_prev_event)
        self.btn_page_prev.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        self.lbl_pageno = customtkinter.CTkLabel(self.frame_buttons, text=self.format_pageno())
        self.lbl_pageno.grid(row=0, column=2, pady=5, padx=5, sticky="w")

        self.btn_page_next = customtkinter.CTkButton(self.frame_buttons, text=">", command=self.button_next_event)
        self.btn_page_next.grid(row=0, column=3, pady=5, padx=5, sticky="w")

        #
        sep_v = tkinter.ttk.Separator(self.frame_buttons, orient='vertical')
        sep_v.grid(row=0, column=4, pady=2, padx=5, sticky="ns")

        # save DB modifications to file
        self.btn_save = customtkinter.CTkButton(self.frame_buttons, text="Save edited components to the DB", command=self.button_save_event)
        self.btn_save.grid(row=0, column=5, pady=5, padx=5, sticky="e")
        self.btn_save.configure(state=tkinter.DISABLED)

        #
        global glob_components
        if not glob_components or len(glob_components.components_all()) == 0:
            logger.info("DB editor: components DB is empty")
        else:
            self.load_components()

    def reload_components(self):
        # reload view
        self.components_pageno = 0
        self.load_components()
        self.lbl_pageno.configure(text=self.format_pageno())

    def var_filter_event(self, sv: customtkinter.StringVar):
        filter = sv.get().strip()
        if filter == self.entry_filter.placeholder_text:
            return
        self.component_filter = filter
        # correct the page index
        n_pages = 1 + len(self.get_components()) // self.COMP_PER_PAGE
        if self.components_pageno >= n_pages:
            self.components_pageno = max(0, n_pages-1)
        # reload view
        self.load_components()
        self.lbl_pageno.configure(text=self.format_pageno())

    def create_components_view(self):
        self.scrollableframe = customtkinter.CTkScrollableFrame(self)
        self.scrollableframe.grid(row=1, column=0, padx=5, pady=5, columnspan=6, sticky="wens")
        self.scrollableframe.grid_columnconfigure(1, weight=2)
        self.scrollableframe.grid_columnconfigure(2, weight=1)
        self.scrollableframe.grid_columnconfigure(3, weight=1)
        # create all widgets only once, keeping them in arrays
        self.lbls_rowno = []
        self.entrys_name = []
        self.entrys_alias = []
        self.chkbttns_hidden = []
        self.vars_hidden = []
        font_size = 12 if Config.instance().editor_font_idx == 0 else 16
        self.editor_font = customtkinter.CTkFont(family="Consolas", size=font_size)

        for idx_on_page in range(self.COMP_PER_PAGE):
            lbl_rowno = tkinter.Label(self.scrollableframe, text="", justify="right")
            lbl_rowno.grid(row=idx_on_page, column=0, padx=5, pady=1, sticky="w")
            self.lbls_rowno.append(lbl_rowno)

            entry_name = ui_helpers.EntryWithPPM(self.scrollableframe, font=self.editor_font, menuitems="c")
            entry_name.grid(row=idx_on_page, column=1, padx=5, pady=1, sticky="we")
            self.entrys_name.append(entry_name)

            entry_alias = ui_helpers.EntryWithPPM(self.scrollableframe, font=self.editor_font, placeholder_text="alias1;")
            entry_alias.grid(row=idx_on_page, column=2, padx=5, pady=1, sticky="we")
            entry_alias.bind("<Return>", self.entry_alias_return)
            self.entrys_alias.append(entry_alias)

            chkbtn_var = tkinter.IntVar(self.scrollableframe, value=False)
            self.vars_hidden.append(chkbtn_var)
            chkbttn_hidden = tkinter.Checkbutton(self.scrollableframe, text="Hidden",
                                                 variable=chkbtn_var, command=self.chkbttn_hidden_event)
            chkbttn_hidden.grid(row=idx_on_page, column=3, padx=5, pady=1, sticky="w")
            self.chkbttns_hidden.append(chkbttn_hidden)

    def get_components(self) -> list[Component]:
        global glob_components
        # depending on entered filter, returns filtered or entire list of components
        if len(self.component_filter) > 0:
            return glob_components.components_filtered(self.component_filter)
        return glob_components.components_all()

    def format_pageno(self) -> str:
        pageno_str = f"{1 + self.components_pageno} / {1 + len(self.get_components()) // self.COMP_PER_PAGE}"
        return pageno_str

    def load_components(self):
        self.changed = False
        components = self.get_components()
        # logger.debug(f"DB Editor: {len(components)} components")
        components_subrange = components[self.components_pageno * self.COMP_PER_PAGE : ]

        for wgt_idx, component in enumerate(components_subrange):
            if wgt_idx == self.COMP_PER_PAGE:
                break
            idx_absolute = wgt_idx + (self.components_pageno * self.COMP_PER_PAGE)
            self.lbls_rowno[wgt_idx].configure(text=f"{idx_absolute+1:04}.")
            ui_helpers.entry_set_text(self.entrys_name[wgt_idx], component.name)
            ui_helpers.entry_set_text(self.entrys_alias[wgt_idx], component.aliases)
            self.vars_hidden[wgt_idx].set(component.hidden)

        # clear remaining fields
        for i in range(len(components_subrange), self.COMP_PER_PAGE):
            self.lbls_rowno[i].configure(text="-")
            ui_helpers.entry_set_text(self.entrys_name[i], "")
            ui_helpers.entry_set_text(self.entrys_alias[i], "")
            self.vars_hidden[i].set(False)

        # scroll the list to the top
        ui_helpers.scrollable_moveto_top(self.scrollableframe)

    def chkbttn_hidden_event(self):
        self.btn_save.configure(state=tkinter.NORMAL)
        logger.debug("Hidden attribute changed")
        self.changed = True

    def entry_alias_return(self, event):
        aliases = event.widget.get().strip()
        logger.debug(f"New aliases: {aliases}")
        self.btn_save.configure(state=tkinter.NORMAL)
        self.changed = True

    def store_component_modifications(self):
        components_subrange = self.get_components()[self.components_pageno * self.COMP_PER_PAGE : ]
        for wgt_idx, component in enumerate(components_subrange):
            if wgt_idx == self.COMP_PER_PAGE:
                break
            component.hidden = self.vars_hidden[wgt_idx].get() == 1
            component.aliases = self.entrys_alias[wgt_idx].get().strip()

    def on_component_attr_changed(self, btn: str, go_next: bool):
        if btn == "y":
            self.button_save_event()
        else:
            self.changed = False

        if not go_next is None:
            if go_next:
                self.button_next_event()
            else:
                self.button_prev_event()

    def check_component_attributes_changed(self, go_next: bool = None):
        if self.changed:
            MessageBox(app=self.app, dialog_type="yn",
                    message="Components attribute(s) has hanged - save?",
                    callback=lambda btn: self.on_component_attr_changed(btn, go_next))
            return True
        return False

    def button_prev_event(self):
        logger.debug("prev page")
        if self.check_component_attributes_changed(False):
            return

        if self.components_pageno > 0:
            self.store_component_modifications()
            self.components_pageno -= 1
            self.load_components()
            self.lbl_pageno.configure(text=self.format_pageno())
            self.changed = False

    def button_next_event(self):
        logger.debug("next page")
        if self.check_component_attributes_changed(True):
            return

        if self.components_pageno < len(self.get_components()) // self.COMP_PER_PAGE:
            self.store_component_modifications()
            self.components_pageno += 1
            self.load_components()
            self.lbl_pageno.configure(text=self.format_pageno())
            self.changed = False

    def button_save_event(self):
        self.store_component_modifications()
        glob_components.save_changes()
        logger.info(f"DB saved to '{glob_components.db_file_path}'")
        self.btn_save.configure(state=tkinter.DISABLED)
        self.components_info.update_components_info()
        self.changed = False

# -----------------------------------------------------------------------------

class CtkApp(customtkinter.CTk):
    TAB_HOME = "Start"
    TAB_PREVIEW = "PnP Preview"
    TAB_EDITOR = "PnP Editor"
    TAB_COMPONENTS = "DB Components"

    def __init__(self):
        logger.info('Ctk app is starting')
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
        self.home_frame = HomeFrame(tab_home, app=self)
        self.home_frame.app = self
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
                logger.info(f"  Date: {glob_components.db_date}")
                logger.info(f"  Items: {len(glob_components.components_all())}")
            else:
                logger.warning(f"DB folder not found at {db_directory}")
        except Exception as e:
            logger.error(f"Error loading database: {e}")

        # panel with the PnP
        self.pnp_view = PnPView(tab_preview)
        self.pnp_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.pnp_config = PnPConfig(tab_preview, app=self, pnp_view=self.pnp_view)
        self.pnp_config.grid(row=1, column=0, padx=5, pady=5, sticky="we")
        self.pnp_config.select_editor = self.get_tab_select_editor_fn()
        self.home_frame.pnp_config = self.pnp_config
        self.home_frame.pnp_view = self.pnp_view

        # panel with PnP footprints editor
        self.pnp_editor = PnPEditor(tab_pnp_editor, app=self)
        self.pnp_editor.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        tab_pnp_editor.grid_columnconfigure(0, weight=1)
        tab_pnp_editor.grid_rowconfigure(0, weight=1)
        self.pnp_view.pnp_editor = self.pnp_editor
        self.pnp_config.pnp_editor = self.pnp_editor
        self.home_frame.pnp_editor = self.pnp_editor

        # panel with DB editor
        self.components_editor = ComponentsEditor(tab_db_editor, app=self)
        self.components_editor.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.components_editor.components_info.update_components_info()

        tab_db_editor.grid_columnconfigure(0, weight=1)
        tab_db_editor.grid_rowconfigure(0, weight=1)

        #
        tab_preview.grid_columnconfigure(0, weight=1)
        tab_preview.grid_rowconfigure(0, weight=1)

        # load the last project
        self.home_frame.process_input_files([Config.instance().recent_pnp_path, Config.instance().recent_pnp2_path])
        self.home_frame.restore_board_preview_paths(Config.instance().recent_board_top_path, Config.instance().recent_board_bot_path)

        # UI ready
        logger.info('Application ready.')

    def get_tab_select_editor_fn(self) -> Callable:
        # return a closure
        appwnd = self
        return lambda: appwnd.tabview.set(appwnd.TAB_EDITOR)

    def get_tab_select_preview_fn(self) -> Callable:
        # return a closure
        appwnd = self
        return lambda: appwnd.tabview.set(appwnd.TAB_PREVIEW)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    logger.config(Config.instance().color_logs)
    logger.info(f"{APP_NAME}   {APP_DATE}")

    if (sys.version_info.major < 3) or (sys.version_info.major == 3 and sys.version_info.minor < 9):
        logger.error("Required Python version 3.9 or later!")
        sys.exit()
    else:
        logger.info(f"Python version: {sys.version_info.major}.{sys.version_info.minor}")

    # https://customtkinter.tomschimansky.com/documentation/appearancemode
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("blue")

    ctkapp = CtkApp()
    ctkapp.mainloop()

    # app exitting
    if glob_components.dirty:
        logger.info('Saving the components database...')
        glob_components.save_changes()

    if glob_components.mru_items.dirty:
        logger.info('Saving the most recent used components (MRU list)...')
        glob_components.mru_items.save_changes()

    logger.info('Program ended.')
