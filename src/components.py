import logging
import os
import time
import csv

# -----------------------------------------------------------------------------

class Component:
    def __init__(self, **kwargs) -> None:
        self.name = ""
        """Original component name, eg "R0603_1k" """
        if "name" in kwargs:
            self.name = kwargs.pop("name")

        self.hidden = False
        """Known, but don't show on the list"""
        if "hidden" in kwargs:
            self.hidden = kwargs.pop("hidden")

    def __lt__(self, other) -> bool:
        # required by sort()
        return self.name < other.name

# -----------------------------------------------------------------------------

class ComponentsDB:
    FILENAME_DATE_FMT = "%Y%m%d_%H%M%S"

    def __init__(self, **kwargs):
        self.db_date = ""
        self.items: list[Component] = []
        if "components_dict" in kwargs:
            components_dict = kwargs.pop("components_dict")
            assert type(components_dict) is dict
            # https://docs.python.org/3/library/stdtypes.html?#dict.items
            for item in components_dict.items():
                # add all component variants into the same flat list
                self.items.extend([Component(name=subitem) for subitem in item[1]])
            self.items.sort()

    """Load latest database version"""
    def load(self, db_folder: str):
        logging.info(f"Initialize components database: {db_folder}")
        db_path_list = []
        for de in os.scandir(db_folder):
            db_fname: str = os.path.basename(de.path)
            if db_fname.startswith("components__") and db_fname.endswith(".csv"):
                logging.debug("  DB path: " + de.path)
                db_path_list.append(de.path)

        # if not empty
        if db_path_list:
            # sort files list to get the latest version
            db_path_list.sort(reverse=True)
            last_db_path = db_path_list[0]
            # extract filename from path
            db_fname: str = os.path.basename(last_db_path)
            logging.info(f"Loading components from: {db_fname}")
            # extract date part from filename
            try:
                # throw away the extension
                self.db_date = db_fname.split("__")[1].split(".")[0]
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
                    self.items.append(Component(name=row_cells[0], hidden=row_cells[1] == "x"))
        else:
            logging.warning(f"No DB files found in {db_folder}")

    """Iterate over components and apply 'hidden' attribute from an old components"""
    def copy_attributes(self, old_items: list[Component]):
        old_items_dict = dict([(v.name, v) for v in old_items])
        for item in self.items:
            if old_item := old_items_dict.get(item.name):
                item.hidden = old_item.hidden

    """Save local DB to a CSV file with date-time"""
    def save(self, db_folder: str):
        now = time.strftime(self.FILENAME_DATE_FMT)
        db_file_path = os.path.join(db_folder, f"components__{now}.csv")
        try:
            with open(db_file_path, "w") as f:
                for item in self.items:
                    hidden="x" if item.hidden else "_"
                    f.write(f"\"{item.name}\"\t{hidden}\n")
        except Exception as e:
            logging.error(f"Error saving to file '{db_file_path}: {e}'")

    """Returns all components"""
    def get_items(self) -> list[Component]:
        return self.items
