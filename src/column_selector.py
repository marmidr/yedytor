import customtkinter
import tkinter
import logging
import typing

import ui_helpers

# -----------------------------------------------------------------------------

class ColumnsSelectorResult:
    def __init__(self):
        self.valid = False
        self.has_column_headers = False
        self.id_col = ""
        self.comment_col = ""
        self.footprint_col = ""
        self.xcoord_col = ""
        self.ycoord_col = ""
        self.rot_col = ""
        self.layer_col = "" # may be None

    def tostr(self) -> str:
        return f"id={self.id_col}, cmnt={self.comment_col}, ftprnt={self.footprint_col}, x={self.xcoord_col}, y={self.ycoord_col}, rot={self.rot_col}, lr={self.layer_col}"

    def serialize(self) -> str:
        """Ensures all fields are an integer indexes, creates a string of space-separated numbers"""
        entities = (
            int(self.has_column_headers),
            self.id_col, self.comment_col, self.footprint_col,
            self.xcoord_col, self.ycoord_col, self.rot_col, self.layer_col
        )
        for ent in entities:
            if not type(ent) is int:
                raise ValueError(f"{ent} is not of type int")
        result = ""
        for ent in entities: result += f"{ent} "
        return result

    def deserialize(self, serialized: str):
        """Load fields from the string created by serialize()"""
        items = serialized.split()
        setters = [
            lambda v: self.__setattr__("has_column_headers", v != 0),
            lambda v: self.__setattr__("id_col", v),
            lambda v: self.__setattr__("comment_col", v),
            lambda v: self.__setattr__("footprint_col", v),
            lambda v: self.__setattr__("xcoord_col", v),
            lambda v: self.__setattr__("ycoord_col", v),
            lambda v: self.__setattr__("rot_col", v),
            lambda v: self.__setattr__("layer_col", v)
        ]
        if len(items) > len(setters):
            logging.error(f"Input has {len(items)} fields, while the struct has {len(setters)}.")
            return
        for i, col_idx in enumerate(items):
            col_idx = int(col_idx)
            setters[i](col_idx)
        self.valid = True

# -----------------------------------------------------------------------------

class ColumnsSelector(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        assert "app" in kwargs
        app = kwargs.pop("app")

        assert "columns" in kwargs
        columns = kwargs.pop("columns")

        assert type(columns) is list
        # logging.debug("columns: {}".format(self.columns))

        assert "callback" in kwargs
        self.callback: typing.Callable = kwargs.pop("callback")

        assert "last_result" in kwargs
        last_result: ColumnsSelectorResult = kwargs.pop("last_result")

        super().__init__(*args, **kwargs)
        ui_helpers.window_set_centered(app, self, 400, 360)

        # prepend column titles with their corresponding index
        columns = [f"{idx+1}. {item}" for (idx,item) in enumerate(columns)]

        #
        lbl_col_headers = customtkinter.CTkLabel(self, text="File has column headers")
        lbl_col_headers.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.chbx_columnheaders_var = customtkinter.BooleanVar(value=True if last_result.valid and last_result.has_column_headers else False)
        chbx_column_headers = customtkinter.CTkCheckBox(self, text="",
                                                        command=self.chbx_event, variable=self.chbx_columnheaders_var,
                                                        checkbox_width=18, checkbox_height=18)
        chbx_column_headers.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        #
        lbl_id = customtkinter.CTkLabel(self, text="ID column:")
        lbl_id.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        initial_value = lambda idx: columns[idx] if last_result.valid else ""

        self.opt_id_var = customtkinter.StringVar(value=initial_value(last_result.id_col))
        opt_id = customtkinter.CTkOptionMenu(self, values=columns,
                                            command=self.opt_event,
                                            variable=self.opt_id_var)
        opt_id.grid(row=1, column=1, pady=5, padx=5, sticky="we")

        #
        lbl_comment = customtkinter.CTkLabel(self, text="Comment / Value column:")
        lbl_comment.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.opt_comment_var = customtkinter.StringVar(value=initial_value(last_result.comment_col))
        opt_comment = customtkinter.CTkOptionMenu(self, values=columns,
                                                command=self.opt_event,
                                                variable=self.opt_comment_var)
        opt_comment.grid(row=2, column=1, pady=5, padx=5, sticky="we")

        #
        lbl_footprint = customtkinter.CTkLabel(self, text="Footprint column:")
        lbl_footprint.grid(row=3, column=0, pady=5, padx=5, sticky="w")

        self.opt_footprint_var = customtkinter.StringVar(value=initial_value(last_result.footprint_col))
        opt_footprint = customtkinter.CTkOptionMenu(self, values=columns,
                                                    command=self.opt_event,
                                                    variable=self.opt_footprint_var)
        opt_footprint.grid(row=3, column=1, pady=5, padx=5, sticky="we")

        # x
        lbl_xcoord = customtkinter.CTkLabel(self, text="X-center column:")
        lbl_xcoord.grid(row=4, column=0, pady=5, padx=5, sticky="w")

        self.opt_xcoord_var = customtkinter.StringVar(value=initial_value(last_result.xcoord_col))
        opt_xcoord = customtkinter.CTkOptionMenu(self, values=columns,
                                                command=self.opt_event,
                                                variable=self.opt_xcoord_var)
        opt_xcoord.grid(row=4, column=1, pady=5, padx=5, sticky="we")

        # y
        lbl_ycoord = customtkinter.CTkLabel(self, text="Y-center column:")
        lbl_ycoord.grid(row=5, column=0, pady=5, padx=5, sticky="w")

        self.opt_ycoord_var = customtkinter.StringVar(value=initial_value(last_result.ycoord_col))
        opt_ycoord = customtkinter.CTkOptionMenu(self, values=columns,
                                                command=self.opt_event,
                                                variable=self.opt_ycoord_var)
        opt_ycoord.grid(row=5, column=1, pady=5, padx=5, sticky="we")

        # rot
        lbl_rot = customtkinter.CTkLabel(self, text="Rotation column:")
        lbl_rot.grid(row=6, column=0, pady=5, padx=5, sticky="w")

        self.opt_rot_var = customtkinter.StringVar(value=initial_value(last_result.rot_col))
        opt_rot = customtkinter.CTkOptionMenu(self, values=columns,
                                            command=self.opt_event,
                                            variable=self.opt_rot_var)
        opt_rot.grid(row=6, column=1, pady=5, padx=5, sticky="we")

        # layer
        lbl_layer = customtkinter.CTkLabel(self, text="Layer column:")
        lbl_layer.grid(row=7, column=0, pady=5, padx=5, sticky="w")

        self.opt_layer_var = customtkinter.StringVar(value=initial_value(last_result.layer_col))
        opt_layer = customtkinter.CTkOptionMenu(self, values=columns,
                                                command=self.opt_event,
                                                variable=self.opt_layer_var)
        opt_layer.grid(row=7, column=1, pady=5, padx=5, sticky="we")

        #
        self.grid_columnconfigure(1, weight=1)


        #
        sep_h = tkinter.ttk.Separator(self, orient='horizontal')
        sep_h.grid(row=8, column=0, columnspan=2, pady=5, padx=5, sticky="we")

        self.btn_cancel = customtkinter.CTkButton(self, text="Cancel",
                                                   command=self.button_cancel_event)
        self.btn_cancel.grid(row=9, column=0, pady=5, padx=5, sticky="")

        self.btn_ok = customtkinter.CTkButton(self, text="OK",
                                                command=self.button_ok_event)
        self.btn_ok.grid(row=9, column=1, pady=5, padx=5, sticky="we")

        if last_result.valid:
            self.btn_ok.configure(state=tkinter.NORMAL)
        else:
            self.btn_ok.configure(state=tkinter.DISABLED)

        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

    def opt_event(self, _new_choice: str):
        if self.opt_id_var.get() != "" and \
            self.opt_comment_var.get() != "" and \
            self.opt_footprint_var.get() != "" and \
            self.opt_xcoord_var.get() != "" and \
            self.opt_ycoord_var.get() != "" and \
            self.opt_rot_var.get() != "":
            self.btn_ok.configure(state=tkinter.NORMAL)

    def chbx_event(self):
        self.btn_ok.configure(state=tkinter.NORMAL)

    def button_cancel_event(self):
        logging.info("Column selector: cancelled")
        self.destroy()

    def button_ok_event(self):
        result = ColumnsSelectorResult()
        result.has_column_headers = self.chbx_columnheaders_var.get()
        result.id_col = self.opt_id_var.get()
        result.comment_col = self.opt_comment_var.get()
        result.footprint_col = self.opt_footprint_var.get()
        result.xcoord_col = self.opt_xcoord_var.get()
        result.ycoord_col = self.opt_ycoord_var.get()
        result.rot_col = self.opt_rot_var.get()
        result.layer_col = self.opt_layer_var.get()
        # extract column index
        def extract_idx(input: str) -> int:
            parsed = int(input.split(sep=". ")[0])
            return parsed-1
        #
        result.id_col = extract_idx(result.id_col)
        result.comment_col = extract_idx(result.comment_col)
        result.footprint_col = extract_idx(result.footprint_col)
        result.xcoord_col = extract_idx(result.xcoord_col)
        result.ycoord_col = extract_idx(result.ycoord_col)
        result.rot_col = extract_idx(result.rot_col)
        result.layer_col = extract_idx(result.layer_col) if result.layer_col != "" else None
        result.valid = True
        #
        self.callback(result)
        self.destroy()
