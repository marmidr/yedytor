# https://linuxhint.com/read-excel-file-python/
# https://openpyxl.readthedocs.io/en/stable/tutorial.html

import openpyxl
import logging

from text_grid import TextGrid

# -----------------------------------------------------------------------------

def read_xlsx_sheet(path: str) -> TextGrid:
    """
    Reads entire sheet 0
    """
    assert path is not None
    logging.info(f"Reading file '{path}'")
    # Define variable to load the wookbook
    wookbook = openpyxl.load_workbook(path)
    sheet = wookbook.active
    tg = TextGrid()

    # Iterate the loop to read the cell values
    for row in sheet.iter_rows(min_row=1, max_col=sheet.max_column, max_row=sheet.max_row, values_only=True):
        row_cells = []
        for cell in row:
            if cell is None:
                cell = ""
            elif type(cell) is float or type(cell) is int:
                if type(cell) is float and int(cell) == float(cell):
                    # prevent the conversion of '100' to '100.0'
                    cell = int(cell)
                cell = repr(cell)
            # change multiline cells into single-line
            cell = cell.replace("\n", " ⏎ ")
            row_cells.append(cell.strip())

        # ignore rows with empty cell 'A'
        if row_cells and row_cells[0] != "":
            tg.rows_raw().append(row_cells)

    tg.nrows = len(tg.rows_raw())
    tg.ncols = sheet.max_column
    tg.align_number_of_columns()
    return tg
