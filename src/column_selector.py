import customtkinter
import tkinter
import logging
import typing

# -----------------------------------------------------------------------------

class ColumnsSelectorResult:
    def __init__(self):
        self.footprint_col = ""
        self.comment_col = ""
        self.has_column_headers = False

# -----------------------------------------------------------------------------

class ColumnsSelector(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        assert "columns" in kwargs
        columns = kwargs.pop("columns")

        assert type(columns) is list
        # logging.debug("columns: {}".format(self.columns))
        assert "callback" in kwargs
        self.callback: typing.Callable = kwargs.pop("callback")

        super().__init__(*args, **kwargs)
        self.geometry("400x170")

        # prepend column titles with their corresponding index
        columns = [f"{idx}. {item}" for (idx,item) in enumerate(columns)]

        #
        lbl_col_headers = customtkinter.CTkLabel(self, text="File has column headers")
        lbl_col_headers.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.chbx_columnheaders_var = customtkinter.BooleanVar(value=False)
        chbx_column_headers = customtkinter.CTkCheckBox(self, text="",
                                                        command=self.chbx_event, variable=self.chbx_columnheaders_var,
                                                        checkbox_width=18, checkbox_height=18)
        chbx_column_headers.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        #
        lbl_footprint = customtkinter.CTkLabel(self, text="Part footprint column:")
        lbl_footprint.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        self.opt_footprint_var = customtkinter.StringVar()
        opt_footprint = customtkinter.CTkOptionMenu(self, values=columns,
                                                     command=self.opt_event,
                                                     variable=self.opt_footprint_var)
        opt_footprint.grid(row=1, column=1, pady=5, padx=5, sticky="we")
        self.grid_columnconfigure(1, weight=1)

        #
        lbl_comment = customtkinter.CTkLabel(self, text="Part comment (value) column:")
        lbl_comment.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.opt_comment_var = customtkinter.StringVar()
        opt_comment = customtkinter.CTkOptionMenu(self, values=columns,
                                                command=self.opt_event,
                                                variable=self.opt_comment_var)
        opt_comment.grid(row=2, column=1, pady=5, padx=5, sticky="we")

        sep_h = tkinter.ttk.Separator(self, orient='horizontal')
        sep_h.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="we")

        self.btn_cancel = customtkinter.CTkButton(self, text="Cancel",
                                                   command=self.button_cancel_event)
        self.btn_cancel.grid(row=4, column=0, pady=5, padx=5, sticky="")

        self.btn_ok = customtkinter.CTkButton(self, text="OK",
                                                command=self.button_ok_event)
        self.btn_ok.grid(row=4, column=1, pady=5, padx=5, sticky="we")
        self.btn_ok.configure(state=tkinter.DISABLED)

        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

    def opt_event(self, _new_choice: str):
        if self.opt_footprint_var.get() != "" and self.opt_comment_var.get() != "":
            self.btn_ok.configure(state=tkinter.NORMAL)

    def chbx_event(self):
        self.btn_ok.configure(state=tkinter.NORMAL)

    def button_cancel_event(self):
        logging.info("Column selector: cancelled")
        self.destroy()

    def button_ok_event(self):
        result = ColumnsSelectorResult()
        result.footprint_col = self.opt_footprint_var.get()
        result.comment_col = self.opt_comment_var.get()
        result.has_column_headers = self.chbx_columnheaders_var.get()
        # extract column index
        result.footprint_col = int(result.footprint_col.split(sep=". ")[0])
        result.comment_col = int(result.comment_col.split(sep=". ")[0])
        self.callback(result)
        self.destroy()
