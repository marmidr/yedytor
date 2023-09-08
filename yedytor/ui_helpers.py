import customtkinter
import tkinter
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
    if entry_disabled: entry.configure(state=tkinter.NORMAL)
    entry.delete(0, tkinter.END)
    entry.insert(0, text)
    if entry_disabled: entry.configure(state=tkinter.DISABLED)
