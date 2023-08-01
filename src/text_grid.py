
class TextGrid:
    """
    Represents data read from the XLS/XLSX/ODS/CSV
    """

    nrows: int
    ncols: int
    rows: list[list[str]]

    def __init__(self):
        self.nrows = 0
        self.ncols = 0
        self.rows = []

    @staticmethod
    def format_cell(cell) -> str:
        """
        Returns a string representation of a given cell, depending on its type
        """
        # https://stackoverflow.com/questions/2184955/test-if-a-variable-is-a-list-or-tuple
        if cell is None:
            cell = ""
        elif type(cell) is not str:
            cell = repr(cell)
        return cell

    def get_columns_width(self, first_row: int) -> list[int]:
        """
        Returns a list of each column width, in chars
        """
        col_max_w = [0 for _ in range(self.ncols)]
        for r, row in enumerate(self.rows):
            if r >= first_row:
                for c, cell in enumerate(row):
                    cell = self.format_cell(cell)
                    cell_w = len(cell)
                    col_max_w[c] = max(col_max_w[c], cell_w)
        return col_max_w

    def format_grid(self, first_row: int, last_row: int = -1) -> str:
        """
        Create spreadsheet-like grid from the content
        """
        columns_width = self.get_columns_width(first_row)
        grid_formatted = ""
        last_row = len(self.rows) if last_row == -1 else last_row
        for r, row in enumerate(self.rows):
            if r >= first_row and r <= last_row:
                row_formatted = "{:0>3} | ".format(r+1)
                for c, cell in enumerate(row):
                    cell = self.format_cell(cell)
                    to_fill = max(columns_width[c] - len(cell), 0)
                    fill = " " * to_fill
                    cell += f"{fill} | "
                    row_formatted += cell
                grid_formatted += row_formatted + "\n"
        return grid_formatted

    def align_number_of_columns(self):
        """
        Ensure every row has the same number of columns
        """
        for row in self.rows:
            cols_to_add = self.ncols - len(row)
            row.extend(("" for _ in range(cols_to_add)))

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
