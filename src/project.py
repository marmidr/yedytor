import logger
import os

import csv_reader
import ods_reader
import xls_reader
import xlsx_reader
import text_grid

from column_selector import ColumnsSelectorResult

# -----------------------------------------------------------------------------

class Project:
    def __init__(self):
        self.pnp_path = "<pnp_fpath>"
        self.pnp2_path = ""
        self.pnp_separator = "SPACES"
        self.pnp_grid: text_grid.TextGrid = None
        self.pnp_grid_dirty = False
        self.pnp_first_row = 0
        self.pnp_columns = ColumnsSelectorResult()
        # self.wip_path = None
        # self.board_top_path = None
        # self.board_bot_path = None
        self.loading = False

    def to_serializable(self) -> dict:
        """Returns class as a dict, containing only basic types, dictionaries and arrays"""
        grid = self.pnp_grid.to_serializable()
        ret = {
            'pnp_path': self.pnp_path,
            'pnp2_path': self.pnp2_path,
            'pnp_separator': self.pnp_separator,
            'pnp_first_row': self.pnp_first_row,
            'pnp_columns': self.pnp_columns.serialize(),
            'pnp_grid': grid,
        }
        return ret

    def from_serializable(self, inp: dict):
        """Loads class from an object returned by `to_serializable()`"""
        try:
            self.pnp_path = inp['pnp_path']
            self.pnp2_path = inp['pnp2_path']
            self.pnp_separator = inp['pnp_separator']
            self.pnp_first_row = inp['pnp_first_row']
            self.pnp_columns.deserialize(inp['pnp_columns'])
            self.pnp_grid = text_grid.TextGrid()
            self.pnp_grid.from_serializable(inp['pnp_grid'])
        except Exception as e:
            logger.error(f"Load from serialized data: {e}")

    def get_name(self) -> str:
        return os.path.basename(self.pnp_path)

    @staticmethod
    def get_separator_names() -> list[str]:
        return ["COMMA", "SEMICOLON", "TAB", "SPACES", "FIXED-WIDTH", "REGEX"].copy()

    @staticmethod
    def translate_separator(sep: str) -> str:
        if sep == "COMMA":
            return ","
        if sep == "SEMICOLON":
            return ";"
        if sep == "TAB":
            return "\t"
        if sep == "SPACES":
            return "*sp"
        if sep == "FIXED-WIDTH":
            return "*fw"
        if sep == "REGEX":
            return "*re"
        raise RuntimeError("Unknown CSV separator")

    def get_pnp_delimiter(self) -> str:
        return self.translate_separator(self.pnp_separator)

    def load_from_file(self, path: str, path2: str):
        path_lower = path.lower()
        delim = self.get_pnp_delimiter()

        if path_lower.endswith("xls"):
            self.pnp_grid = xls_reader.read_xls_sheet(path)
        elif path_lower.endswith("xlsx"):
            self.pnp_grid = xlsx_reader.read_xlsx_sheet(path)
        elif path_lower.endswith("ods"):
            self.pnp_grid = ods_reader.read_ods_sheet(path)
        else: # assume CSV
            self.pnp_grid = csv_reader.read_csv(path, delim)

        log_f = logger.info if self.pnp_grid.nrows > 0 else logger.warning
        log_f(f"  PnP: {self.pnp_grid.nrows} rows x {self.pnp_grid.ncols} cols")

        # load the optional second PnP file
        if path2 != "":
            path2_lower = path2.lower()

            if path2_lower.endswith("xls"):
                pnp2_grid = xls_reader.read_xls_sheet(path2)
            elif path2_lower.endswith("xlsx"):
                pnp2_grid = xlsx_reader.read_xlsx_sheet(path)
            elif path2_lower.endswith("ods"):
                pnp2_grid = ods_reader.read_ods_sheet(path2)
            else: # assume CSV
                pnp2_grid = csv_reader.read_csv(path2, delim)

            log_f = logger.info if pnp2_grid.nrows > 0 else logger.warning
            log_f(f"PnP2: {pnp2_grid.nrows} rows x {pnp2_grid.ncols} cols")

            # merge
            if pnp2_grid.ncols != self.pnp_grid.ncols:
                raise ValueError(f"PnP has {self.pnp_grid.ncols} columns, but PnP2 has {pnp2_grid.ncols} columns")

            self.pnp_grid.nrows += pnp2_grid.nrows
            self.pnp_grid.rows_raw().extend(pnp2_grid.rows())
