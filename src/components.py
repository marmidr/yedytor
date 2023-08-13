import logging
import os
import time
import csv

# -----------------------------------------------------------------------------

class Component:
    def __init__(self, **kwargs) -> None:
        self.names = ""
        """Semicolon-separated variants of component name, eg "R0603_1k;R0603_1K" """
        if "names" in kwargs:
            self.names = kwargs.pop("names")

        self.ignored = False
        """Known, but don't show on the list"""
        if "ignored" in kwargs:
            self.ignored = kwargs.pop("ignored")

    def __lt__(self, other) -> bool:
        # required by sort()
        return self.names < other.names

# -----------------------------------------------------------------------------

class ComponentsDB:
    FILENAME_DATE_FMT = "%Y%m%d_%H%M%S"

    def __init__(self, *args, **kwargs):
        self.db_date = ""
        self.items: list[Component] = []
        if "components_dict" in kwargs:
            components_dict = kwargs.pop("components_dict")
            assert type(components_dict) is dict
            # https://docs.python.org/3/library/stdtypes.html?#dict.items
            self.items = [Component(names=";".join(item[1])) for item in components_dict.items()]
            self.items.sort()

    """Load latest database version"""
    def load(self, db_folder: str):
        logging.info(f"Initialize components database: {db_folder}")
        db_list = []
        for de in os.scandir(db_folder):
            logging.debug("DB path: " + de.path)
            # take only the file name
            db_list.append(de.path)

        if db_list:
            # sort files list to get the latest version
            db_list.sort(reverse=True)
            last_db_path = db_list[0]
            # extract filename from path
            dbname: str = os.path.basename(last_db_path)
            logging.info(f"Loading components from: {dbname}")
            # extract date part from filename
            try:
                self.db_date = dbname.split("__")[1].split(".")[0]
                time_tuple = time.strptime(self.db_date, self.FILENAME_DATE_FMT)
                self.db_date = time.strftime("%Y-%m-%d, %H:%M:%S", time_tuple)
            except Exception as e:
                logging.warning(f"Unable to parse file datetime: {e}")
                self.db_date = "?, ?"

            self.items.clear()
            # read csv file
            with open(last_db_path, "r") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    row_cells = [cell.strip() for cell in row]
                    self.items.append(Component(names=row_cells[0], ignored=row_cells[1] == "x"))
        else:
            logging.warning(f"No DB files found in {db_folder}")

    """Save local DB to a CSV file with date-time"""
    def save(self, db_folder: str):
        now = time.strftime(self.FILENAME_DATE_FMT)
        db_file_path = os.path.join(db_folder, f"components__{now}.csv")
        try:
            with open(db_file_path, "w") as f:
                for item in self.items:
                    ignored="x" if item.ignored else "_"
                    f.write(f"\"{item.names}\"\t{ignored}\n")
        except Exception as e:
            logging.error(f"Error saving to file '{db_file_path}: {e}'")

    """Returns all components"""
    def get_items(self) -> list[Component]:
        return self.items
