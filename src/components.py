import logging
import os
import time
import csv
import fnmatch

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
        """date str"""
        self.db_file_path = ""
        """full filepath"""
        self.__items: list[Component] = []
        """list of components"""

        if "components_dict" in kwargs:
            components_dict = kwargs.pop("components_dict")
            assert type(components_dict) is dict
            # https://docs.python.org/3/library/stdtypes.html?#dict.items
            for item in components_dict.items():
                # add all component variants into the same flat list
                self.__items.extend([Component(name=subitem) for subitem in item[1]])
            self.__items.sort()

    def load(self, db_folder: str):
        """Load latest database version"""
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

            self.__items.clear()
            # read csv file
            with open(last_db_path, "r") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    row_cells = [cell.strip() for cell in row]
                    self.__items.append(Component(name=row_cells[0], hidden=row_cells[1] == "x"))
                self.db_file_path = last_db_path
        else:
            logging.warning(f"No DB files found in {db_folder}")

    def copy_attributes(self, old_items: list[Component]):
        """Iterate over components and apply 'hidden' attribute from an old components"""
        old_items_dict = dict([(v.name, v) for v in old_items])
        for item in self.__items:
            if old_item := old_items_dict.get(item.name):
                item.hidden = old_item.hidden

    def save_new(self, db_folder: str):
        """Save local DB to a CSV file with date-time"""
        now = time.strftime(self.FILENAME_DATE_FMT)
        db_file_path = os.path.join(db_folder, f"components__{now}.csv")
        try:
            with open(db_file_path, "w") as f:
                for item in self.__items:
                    hidden="x" if item.hidden else "_"
                    f.write(f"\"{item.name}\"\t{hidden}\n")
            self.db_file_path = db_file_path
        except Exception as e:
            logging.error(f"Error saving to file '{db_file_path}: {e}'")

    def save_changes(self):
        """Save local DB to the same file"""
        try:
            with open(self.db_file_path, "w") as f:
                for item in self.__items:
                    hidden="x" if item.hidden else "_"
                    f.write(f"\"{item.name}\"\t{hidden}\n")
        except Exception as e:
            logging.error(f"Error saving changes to file '{self.db_file_path}: {e}'")

    def count_visible(self) -> int:
        """Returns the number of valid components"""
        n = 0
        for item in self.__items:
            if not item.hidden: n += 1
        return n

    def count_hidden(self) -> int:
        """Returns the number of hidden components"""
        n = 0
        for item in self.__items:
            if item.hidden: n += 1
        return n

    def items_all(self) -> list[Component]:
        """Returns all components"""
        return self.__items

    def items_filtered(self, needle: str, visible: bool=True) -> list[Component]:
        """Returns components containing the needle"""
        """Needle: space-separated keywords: "603", "603 2k2", ..."""
        needle = '*' + '*'.join(needle.split(' ')) + '*'
        result = []
        for item in self.__items:
            if fnmatch.fnmatch(item.name, needle):
                if (not visible) or (visible and not item.hidden):
                    result.append(item.name)
        return result

    def items_visible(self) -> list[str]:
        component_list = list(item.name for item in self.items_all() if not item.hidden)
        return component_list
