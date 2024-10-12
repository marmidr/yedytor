import logger

from odf import opendocument, table

# local copy of odf:
# import os
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), "odfpy"))
# from odfpy.odf import opendocument, table

from text_grid import TextGrid

# -----------------------------------------------------------------------------

def read_ods_sheet(path: str) -> TextGrid:
    """
    Reads ODS/spreadsheet document, returning the first sheet
    """
    assert path is not None
    logger.info(f"Reading file '{path}'")
    doc = opendocument.load(path)
    tg = TextGrid()

    # with open(path + "-dump.xml", "w") as f:
    #     f.write(str(doc.xml()))

    if "opendocument.spreadsheet" in doc.getMediaType():
        for tab in doc.getElementsByType(table.Table):
            name = tab.getAttrNS(table.TABLENS, "name")
            logger.info(f"Reading sheet: {name}")
            max_cols = 0
            REPEATS_ATTR = "number-columns-repeated".replace('-','')

            for tablerow in tab.getElementsByType(table.TableRow):
                tablecells = tablerow.getElementsByType(table.TableCell)
                row_cells = []
                # when iterating through the row cells, take the "repeat" attribute into account
                for cell in tablecells:
                    repeated = cell.getAttribute(REPEATS_ATTR) or 1
                    repeated = int(repeated)
                    for _ in range(repeated):
                        row_cells.append(str(cell))

                max_cols = max(max_cols, len(row_cells))

                # ignore rows with empty cell 'A'
                if row_cells and row_cells[0] != "":
                    tg.rows_raw().append(row_cells)

            tg.nrows = len(tg.rows_raw())
            tg.ncols = max_cols

            # dont read any other sheets
            break
    else:
        logger.error("File does not contain a spreadsheet document")

    tg.align_number_of_columns()
    return tg
