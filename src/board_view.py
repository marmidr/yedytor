import logger
import os
import customtkinter
import PIL
import tkinter

import ui_helpers

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
        self.image_path = kwargs.pop("image_path")

        # preview image scaling factor
        self.preview_scale = 0.3

        super().__init__(*args, **kwargs)
        ui_helpers.window_set_centered(app, self, 600, 500)

        # self.lbl_board_preview = customtkinter.CTkLabel(self, text="")
        # self.lbl_board_preview.grid(row=0, column=0, pady=5, padx=5, sticky="wn")
        # self.lbl_board_preview.bind("<Button-1><ButtonRelease-1>", self.preview_clicked)

        self.cvs_board_preview = tkinter.Canvas(self)
        self.cvs_board_preview.grid(row=0, column=0, pady=5, padx=5, sticky="wens")
        self.cvs_board_preview.bind("<Button-1><ButtonRelease-1>", self.preview_clicked)

        self.scrollbar_h = customtkinter.CTkScrollbar(self, orientation="horizontal", command=self.cvs_board_preview.xview, height=25)
        self.scrollbar_h.grid(row=1, column=0, padx=5, pady=5, sticky="we")

        self.scrollbar_v = customtkinter.CTkScrollbar(self, orientation="vertical", command=self.cvs_board_preview.yview, width=25)
        self.scrollbar_v.grid(row=0, column=1, padx=5, pady=5, sticky="ns")

        self.cvs_board_preview.configure(yscrollcommand=self.scrollbar_v.set)
        self.cvs_board_preview.configure(xscrollcommand=self.scrollbar_h.set)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # bottom panel
        if True:
            self.frm_bottom = customtkinter.CTkFrame(self)
            self.frm_bottom.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="we")

            self.lbl_size = customtkinter.CTkLabel(self.frm_bottom, text="Size 0x0")
            self.lbl_size.grid(row=0, column=0, pady=15, padx=15, sticky="")

            self.lbl_coord = customtkinter.CTkLabel(self.frm_bottom, text="Pos [0:0]")
            self.lbl_coord.grid(row=0, column=1, pady=15, padx=15, sticky="")

        # load image
        self.load_image(self.image_path)
        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

    def load_image(self, path: str):
        if os.path.isfile(path):
            try:
                # https://pythonguides.com/python-tkinter-image/
                # img = PhotoImage(file=image_path)
                img = PIL.Image.open(path)
                img_scaled = img.resize((int(img.width * self.preview_scale), int(img.height * self.preview_scale)))
                # note: the image to be displayed must not be a local variable!
                self.photo_img = PIL.ImageTk.PhotoImage(img_scaled)
                try:
                    # self.lbl_board_preview.configure(image=photo_img)
                    # self.cvs_board_preview.configure(width=img.width, height=img.height)
                    self.cvs_board_preview.create_image(0, 0, image=self.photo_img, anchor="nw")
                    # make the scrollbars work:
                    self.cvs_board_preview.config(scrollregion=self.cvs_board_preview.bbox("all"))

                    self.lbl_size.configure(text=f"Image size: {img.width} x {img.height}")
                except Exception as e:
                    logger.error(f"{e}")
            except Exception as e:
                logger.error(f"Cannot open image file: {e}")
            finally:
                logger.debug("Board preview loaded")
        else:
            logger.warning("File 'image_path' does not exists")

    def preview_clicked(self, ev):

        # get the X coordinate (0..1) on the Canvas
        canv_w = self.cvs_board_preview.winfo_width()
        x = ev.x
        x /= canv_w

        # get the Y coordinate (0..1) on the Canvas
        canv_h = self.cvs_board_preview.winfo_height()
        y = ev.y
        y /= canv_h

        # get the canvas horizontal view range (0.0 .. 1.0)
        (h_start, h_end) = self.cvs_board_preview.xview()
        # image horizontal display range on the canvas
        x_start = (self.photo_img.width() / self.preview_scale) * h_start
        x_end = (self.photo_img.width() / self.preview_scale) * h_end
        #
        img_x = x * (x_end - x_start)
        img_x += x_start
        img_x = int(img_x)

        # get the canvas vertical view range (0.0 .. 1.0)
        (v_start, v_end) = self.cvs_board_preview.yview()
        y_start = (self.photo_img.height() / self.preview_scale) * v_start
        # image vertical  display range on the canvas
        y_end = (self.photo_img.height() / self.preview_scale) * v_end
        img_y = y * (y_end - y_start)
        img_y += y_start
        img_y = int(img_y)

        # TODO: scale pixels to mm

        self.lbl_coord.configure(text=f"Click pos: [{img_x} : {img_y}]")

    def button_ok_event(self):
        # logger.debug("Ok")
        self.callback("o")
        self.destroy()
