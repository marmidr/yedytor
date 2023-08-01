# https://linuxhint.com/read-excel-file-python/
# https://xlrd.readthedocs.io/en/latest/

import xlrd
import logging

from text_grid import TextGrid

# -----------------------------------------------------------------------------

def read_xls_sheet(path: str) -> TextGrid:
    """
    Reads entire sheet 0
    """
    assert path is not None
    logging.info(f"Reading file '{path}'")
    book = xlrd.open_workbook(filename=path)
    sheet = book.sheet_by_index(0)
    tg = TextGrid()

    # Iterate the loop to read the cell values
    for r in range(sheet.nrows):
        row_cells = []
        for c in range(sheet.ncols):
            cell = sheet.cell_value(r, c)
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
            tg.rows.append(row_cells)

    tg.nrows = len(tg.rows)
    tg.ncols = sheet.ncols
    tg.align_number_of_columns()
    return tg
