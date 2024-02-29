import typing
# import logging

import customtkinter

import ui_helpers

# -----------------------------------------------------------------------------

class MessageBox(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        """
        Opens a new MessageBox popup:
        app=main wnd, so we know how to center the popup
        dialog_type=str - 'yn', 'ync', 'o', 'oc'
        message=str - text of the message
        callback=typing.Callable[[str], None] - function receiving "y", "n", "o", "c"
        """
        assert "app" in kwargs
        app = kwargs.pop("app")

        assert "dialog_type" in kwargs
        self.dialog_type = kwargs.pop("dialog_type")

        assert "message" in kwargs
        self.message = kwargs.pop("message")

        assert "callback" in kwargs
        self.callback: typing.Callable[[str], None] = kwargs.pop("callback")

        super().__init__(*args, **kwargs)
        ui_helpers.window_set_centered(app, self, 400, 150)

        lbl_message = customtkinter.CTkLabel(self, text=self.message)
        lbl_message.grid(row=0, column=0, pady=15, padx=15, sticky="wens", columnspan=3)

        if self.dialog_type == "yn":
            self.btn_yes = customtkinter.CTkButton(self, text="Yes", command=self.button_yes_event)
            self.btn_yes.grid(row=2, column=0, pady=5, padx=5, sticky="we")
            self.btn_no = customtkinter.CTkButton(self, text="No", command=self.button_no_event)
            self.btn_no.grid(row=2, column=1, pady=5, padx=5, sticky="we")
        elif self.dialog_type == "ync":
            self.btn_yes = customtkinter.CTkButton(self, text="Yes", command=self.button_yes_event)
            self.btn_yes.grid(row=2, column=0, pady=5, padx=5, sticky="")
            self.btn_no = customtkinter.CTkButton(self, text="No", command=self.button_no_event)
            self.btn_no.grid(row=2, column=1, pady=5, padx=5, sticky="")
            self.btn_cancel = customtkinter.CTkButton(self, text="Cancel", command=self.button_cancel_event)
            self.btn_cancel.grid(row=2, column=2, pady=5, padx=5, sticky="")
        elif self.dialog_type == "o":
            self.btn_ok = customtkinter.CTkButton(self, text="Ok", command=self.button_ok_event)
            self.btn_ok.grid(row=2, column=1, pady=5, padx=5, sticky="")
        elif self.dialog_type == "oc":
            self.btn_ok = customtkinter.CTkButton(self, text="Ok", command=self.button_ok_event)
            self.btn_ok.grid(row=2, column=0, pady=5, padx=5, sticky="")
            self.btn_cancel = customtkinter.CTkButton(self, text="Cancel", command=self.button_cancel_event)
            self.btn_cancel.grid(row=2, column=2, pady=5, padx=5, sticky="")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

    def button_yes_event(self):
        # logging.debug("Yes")
        self.callback("y")
        self.destroy()

    def button_no_event(self):
        # logging.debug("No")
        self.callback("n")
        self.destroy()

    def button_cancel_event(self):
        # logging.debug("Cancel")
        self.callback("c")
        self.destroy()

    def button_ok_event(self):
        # logging.debug("Ok")
        self.callback("o")
        self.destroy()
