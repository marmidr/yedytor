import tkinter
import customtkinter
# import logging

# -----------------------------------------------------------------------------

def textbox_find_text(textbox: customtkinter.CTkTextbox, needle: str) -> int:
    """Search and highlight the text in the TextBox"""

    textbox.tag_delete("search")
    textbox.tag_config("search", background="yellow")
    start = 1.0
    pos = textbox.search(pattern=needle, index=start, stopindex=tkinter.END, nocase=True)
    found_cnt = 0
    length = len(needle)

    if length > 0:
        while pos:
            found_cnt += 1
            row, col = pos.split('.')
            end = int(col) + length
            end = f'{row}.{str(end)}'
            textbox.tag_add("search", pos, end)
            start = end
            pos = textbox.search(pattern=needle, index=start, stopindex=tkinter.END, nocase=True)

    return found_cnt

def entry_set_text(entry: customtkinter.CTkEntry, text: str):
    # delete/insert are not working on disabled widget
    entry_disabled = entry.cget("state") == tkinter.DISABLED
    if entry_disabled:
        entry.configure(state=tkinter.NORMAL)
    entry.delete(0, tkinter.END)
    entry.insert(0, text)
    if entry_disabled:
        entry.configure(state=tkinter.DISABLED)


# https://stackoverflow.com/questions/4266566/stardand-context-menu-in-python-tkinter-text-widget-when-mouse-right-button-is-p
def _wgt_install_standard_menu(wgt, items: str):
    wgt.menu = tkinter.Menu(wgt, tearoff=0)

    if "c" in items:
        wgt.menu.add_command(label="Copy")
        wgt.menu.entryconfigure("Copy", command=lambda: wgt.focus_force() or wgt.event_generate("<<Copy>>"))
    if "x" in items:
        wgt.menu.add_command(label="Cut")
        wgt.menu.entryconfigure("Cut", command=lambda: wgt.focus_force() or wgt.event_generate("<<Cut>>"))
    if "p" in items:
        wgt.menu.add_command(label="Paste")
        wgt.menu.entryconfigure("Paste", command=lambda: wgt.focus_force() or wgt.event_generate("<<Paste>>"))

    wgt.menu.add_separator()
    wgt.menu.add_command(label="Select all")
    wgt.menu.entryconfigure("Select all", command=wgt.event_select_all)


class EntryWithPPM(tkinter.Entry):
    def __init__(self, *args, **kwargs):
        menuitems = kwargs.pop("menuitems") if "menuitems" in kwargs else "cxp"
        tkinter.Entry.__init__(self, *args, **kwargs)

        _wgt_install_standard_menu(self, menuitems)
        # overwrite default class binding so we don't need to return "break"
        self.bind_class("Entry", "<Control-a>", self.event_select_all)
        self.bind("<Button-3><ButtonRelease-3>", self.show_menu)

    def event_select_all(self, *_args):
        self.focus_force()
        self.selection_range(0, tkinter.END)

    def show_menu(self, ev):
        self.tk.call("tk_popup", self.menu, ev.x_root, ev.y_root)

# seems like bindings (<<Copy>>, ...) are not implemented in Ctk
# class CtkEntryWithPPM(customtkinter.CTkEntry):
#     def __init__(self, *args, **kwargs):
#         menuitems = kwargs.pop("menuitems") if "menuitems" in kwargs else "cxp"
#         customtkinter.CTkEntry.__init__(self, *args, **kwargs)

#         _wgt_install_standard_menu(self, menuitems)
#         # overwrite default class binding so we don't need to return "break"
#         self.bind_class("Entry", "<Control-a>", self.event_select_all)
#         self.bind("<Button-3><ButtonRelease-3>", self.show_menu)

#     def event_select_all(self, *args):
#         self.focus_force()
#         self.selection_range(0, tkinter.END)

#     def show_menu(self, e):
#         self.tk.call("tk_popup", self.menu, e.x_root, e.y_root)


class ComboboxWithPPM(tkinter.ttk.Combobox):
    def __init__(self, *args, **kwargs):
        menuitems = kwargs.pop("menuitems") if "menuitems" in kwargs else "cxp"
        tkinter.ttk.Combobox.__init__(self, *args, **kwargs)

        _wgt_install_standard_menu(self, menuitems)
        # overwrite default class binding so we don't need to return "break"
        self.bind_class("Entry", "<Control-a>", self.event_select_all)
        self.bind("<Button-3><ButtonRelease-3>", self.show_menu)

    def event_select_all(self, *_args):
        self.focus_force()
        self.selection_range(0, tkinter.END)

    def show_menu(self, ev):
        self.tk.call("tk_popup", self.menu, ev.x_root, ev.y_root)

def window_set_centered(app: tkinter.Tk, wnd: tkinter.Toplevel, wnd_w: int, wnd_h: int):
    # set window size
    wnd.geometry(f"{wnd_w}x{wnd_h}")
    # calc position
    wnd_x = app.winfo_rootx()
    wnd_x += app.winfo_width()//2
    wnd_x -= wnd_w//2
    wnd_y = app.winfo_rooty()
    wnd_y += app.winfo_height()//2
    wnd_y -= wnd_h//2
    wnd_y -= 20
    # set screen position
    wnd.geometry(f"+{wnd_x}+{wnd_y}")
