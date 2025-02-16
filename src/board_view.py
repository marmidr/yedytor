import PIL.Image
import logger
import os

import customtkinter

import ui_helpers
# from tkinter import PhotoImage
import PIL

# -----------------------------------------------------------------------------

class BoardView(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        """
        Opens a new Window with PCB overlay preview:
        app=main wnd, so we know how to center the popup
        image_path=path to the JPEG to display
        """
        assert "app" in kwargs
        app = kwargs.pop("app")

        assert "image_path" in kwargs
        image_path = kwargs.pop("image_path")

        super().__init__(*args, **kwargs)
        ui_helpers.window_set_centered(app, self, 600, 500)

        self.scrollable_h = customtkinter.CTkScrollableFrame(self, orientation="horizontal")
        self.scrollable_h.grid(row=0, column=0, padx=5, pady=5, sticky="wens")

        self.scrollable_h.grid_columnconfigure(0, weight=1)
        self.scrollable_h.grid_rowconfigure(0, weight=1)

        self.scrollable_v = customtkinter.CTkScrollableFrame(self.scrollable_h)
        self.scrollable_v.grid(row=0, column=0, padx=5, pady=5, sticky="wens")

        self.scrollable_v.grid_columnconfigure(0, weight=1)
        self.scrollable_v.grid_rowconfigure(0, weight=1)

        self.board_preview = customtkinter.CTkLabel(self.scrollable_h, text="")
        self.board_preview.grid(row=0, column=0, pady=5, padx=5, sticky="wens")
        self.board_preview.bind("<Button-1><ButtonRelease-1>", self.image_clicked)

        # bottom panel
        self.frm_bottom = customtkinter.CTkFrame(self)
        self.frm_bottom.grid(row=1, column=0, pady=5, padx=5, sticky="we")

        self.lbl_size = customtkinter.CTkLabel(self.frm_bottom, text="Size 0x0")
        self.lbl_size.grid(row=0, column=0, pady=15, padx=15, sticky="")

        self.lbl_coord = customtkinter.CTkLabel(self.frm_bottom, text="Pos [0:0]")
        self.lbl_coord.grid(row=0, column=1, pady=15, padx=15, sticky="")

        # load image
        if os.path.isfile(image_path):
            try:
                # https://pythonguides.com/python-tkinter-image/
                # img = PhotoImage(file=image_path)
                img = PIL.Image.open(image_path)
                show_img = PIL.ImageTk.PhotoImage(img)
                try:
                    self.board_preview.configure(image=show_img)
                    self.lbl_size.configure(text=f"Size {img.width} x {img.height}")
                except Exception as e:
                    logger.error(f"{e}")
            except Exception as e:
                logger.error(f"Cannot open image file: {e}")
            finally:
                logger.debug("Board preview loaded")
        else:
            logger.warning("File 'image_path' does not exists")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

    def image_clicked(self, ev):
        self.lbl_coord.configure(text=f"Pos [{ev.x_root}:{ev.y_root}]")

    def button_ok_event(self):
        # logger.debug("Ok")
        self.callback("o")
        self.destroy()
