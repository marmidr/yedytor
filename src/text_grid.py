import logger

class TextGrid:
    """
    Represents data read from the XLS/XLSX/ODS/CSV
    """

    def __init__(self):
        self.nrows = 0
        self.ncols = 0
        self.firstrow = 0
        self.lastrow = 0
        self.__rows: list[list[str]] = []

    def to_serializable(self) -> dict:
        ret = {
            'nrows': self.nrows,
            'ncols': self.ncols,
            'firstrow': self.firstrow,
            'lastrow': self.lastrow,
            'rows': self.__rows
        }
        return ret

    def from_serializable(self, inp: dict):
        try:
            self.nrows = inp['nrows']
            self.ncols = inp['ncols']
            self.firstrow = inp['firstrow']
            self.lastrow = inp['lastrow']
            self.__rows = inp['rows']
        except Exception as e:
            logger.error(f"Load from serialized data: {e}")

    @staticmethod
    def format_cell(cell) -> str:
        """
        Returns a string representation of a given cell, depending on its type
        """
        # https://stackoverflow.com/questions/2184955/test-if-a-variable-is-a-list-or-tuple
        if cell is None:
            cell = ""
        elif not isinstance(cell, str):
            cell = repr(cell)
        return cell

    def get_columns_width(self, first_row: int) -> list[int]:
        """
        Returns a list of each column width, in chars
        """
        col_max_w = [0 for _ in range(self.ncols)]
        for r_idx, row in enumerate(self.__rows):
            if r_idx >= first_row:
                for c_idx, cell in enumerate(row):
                    cell = self.format_cell(cell)
                    cell_w = len(cell)
                    col_max_w[c_idx] = max(col_max_w[c_idx], cell_w)
        return col_max_w

    def format_grid(self, first_row: int, last_row: int = 0) -> str:
        """
        Create spreadsheet-like grid from the content
        """
        columns_width = self.get_columns_width(first_row)
        grid_formatted = ""
        last_row = len(self.__rows) if last_row <= 0 else last_row
        for r_idx, row in enumerate(self.__rows):
            if r_idx >= first_row and r_idx <= last_row:
                row_formatted = "{:0>3} | ".format(r_idx+1)
                for c_idx, cell in enumerate(row):
                    cell = self.format_cell(cell)
                    to_fill = max(columns_width[c_idx] - len(cell), 0)
                    fill = " " * to_fill
                    cell += f"{fill} | "
                    row_formatted += cell
                grid_formatted += row_formatted + "\n"
        return grid_formatted

    def align_number_of_columns(self):
        """
        Ensure every row has the same number of columns
        """
        for row in self.__rows:
            cols_to_add = self.ncols - len(row)
            row.extend(("" for _ in range(cols_to_add)))

    def rows(self) -> list[list[str]]:
        """Returns the rows subset, skipping X first rows"""
        if self.lastrow > 0 and self.lastrow < len(self.__rows):
            return self.__rows[self.firstrow:self.lastrow]
        return self.__rows[self.firstrow:]

    def rows_raw(self) -> list[list[str]]:
        """Returns full rows: for editing, appending"""
        return self.__rows

class ConfiguredTextGrid:
    """
    Determines data range to be imported
    """
    text_grid: TextGrid
    has_column_headers: bool
    designator_col: str
    comment_col: str
    first_row: int
    last_row: int
