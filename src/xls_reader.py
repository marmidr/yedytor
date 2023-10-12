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
            cellobj = sheet.cell(r, c)
            cell_val = cellobj.value or ""

            # https://xlrd.readthedocs.io/en/latest/api.html#xlrd.sheet.Cell
            if cellobj.ctype == xlrd.XL_CELL_NUMBER:
                if type(cell_val) is float and int(cell_val) == cell_val:
                    # prevent the conversion of '100' to '100.0'
                    cell_val = int(cell_val)
                cell_val = repr(cell_val)
            # change multiline cells into single-line
            cell_val = cell_val.replace("\n", " ⏎ ")
            row_cells.append(cell_val.strip())

        # ignore rows with empty cell 'A'
        if row_cells and row_cells[0] != "":
            tg.rows_raw().append(row_cells)

    tg.nrows = len(tg.rows_raw())
    tg.ncols = sheet.ncols
    tg.align_number_of_columns()
    return tg
