import customtkinter
import tkinter
import logging
import typing

# -----------------------------------------------------------------------------

class ColumnsSelectorResult:
    footprint_col: str
    comment_col: str

    def __init__(self):
        self.footprint_col = ""
        self.comment_col = ""

# -----------------------------------------------------------------------------

class ColumnsSelector(customtkinter.CTkToplevel):
    callback: typing.Callable

    def __init__(self, *args, **kwargs):
        assert "columns" in kwargs
        columns = kwargs.pop("columns")

        assert type(columns) is list
        # logging.debug("columns: {}".format(self.columns))
        assert "callback" in kwargs
        self.callback = kwargs.pop("callback")

        super().__init__(*args, **kwargs)
        self.geometry("400x140")

        # prepend column titles with their corresponding index
        columns = [f"{idx}. {item}" for (idx,item) in enumerate(columns)]

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
        self.btn_ok.configure(state="disabled")

        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

    def opt_event(self, _new_choice: str):
        if self.opt_footprint_var.get() != "" and self.opt_comment_var.get() != "":
            self.btn_ok.configure(state="enabled")

    def button_cancel_event(self):
        logging.info("Column selector: cancelled")
        self.destroy()

    def button_ok_event(self):
        result = ColumnsSelectorResult()
        result.footprint_col = self.opt_footprint_var.get()
        result.comment_col = self.opt_comment_var.get()
        # extract column index
        result.footprint_col = int(result.footprint_col.split(sep=". ")[0])
        result.comment_col = int(result.comment_col.split(sep=". ")[0])
        self.callback(result)
        self.destroy()
