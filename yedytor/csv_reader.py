import csv
import logging

from text_grid import TextGrid

# -----------------------------------------------------------------------------

def __read_sp(rows: list[str], tg: TextGrid):
    max_cols = 0
    for row in rows:
        # split row by any number of following whitespaces
        row_cells = row.split()
        max_cols = max(max_cols, len(row_cells))
        # ignore rows with empty cell 'A' or cell with a long horizontal line
        if len(row_cells) > 0 and row_cells[0] != "" and not row_cells[0].startswith("___"):
            row_cells_processed = []

            # merge quoted cells into single one,
            # like this: "5k1 5% 0603"
            quoted_cell = ""
            for cell in row_cells:
                if cell.startswith('"'):
                    quoted_cell = cell
                elif len(quoted_cell) > 0:
                    quoted_cell += ' '
                    quoted_cell += cell
                    if cell.endswith('"'):
                        # drop the quotes
                        quoted_cell = quoted_cell[1:-1]
                        row_cells_processed.append(quoted_cell)
                        quoted_cell = ""
                else:
                    row_cells_processed.append(cell.strip())
            tg.rows_raw().append(row_cells_processed)
    return max_cols

def read_csv(path: str, delim: str) -> TextGrid:
    """
    Reads entire CSV/text file.

    Delim may be: ' '  ','  ';'  '\t'  '*fw'  '*re'
    """

    assert path is not None
    assert type(delim) is str
    logging.info(f"Reading file '{path}', delim='{delim}'")
    tg = TextGrid()
    max_cols = 0

    with open(path, 'r', encoding="utf-8") as f:
        if delim == "*sp":
            rows = f.read().splitlines()
            max_cols = __read_sp(rows, tg)
        elif delim == "*fw":
            # TODO: add reader for fixed-width
            raise ValueError("delimiter *fw not yet implemented")
        elif delim == "*re":
            # TODO: add reader for reg-ex
            raise ValueError("delimiter *re not yet implemented")
        else:
            reader = csv.reader(f, delimiter=delim)
            for row in reader:
                # ignore rows with empty cell 'A' or cell with a long horizontal line
                if len(row) > 0 and row[0] != "" and not row[0].startswith("___"):
                    row_cells = [cell.strip() for cell in row]
                    max_cols = max(max_cols, len(row_cells))
                    tg.rows_raw().append(row_cells)

    tg.nrows = len(tg.rows_raw())
    tg.ncols = max_cols
    tg.align_number_of_columns()
    return tg
