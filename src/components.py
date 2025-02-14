import logger
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
            hid = kwargs.pop("hidden")
            if isinstance(hid, bool):
                self.hidden = hid

        self.aliases = ""
        """Semicolon-separated alternative names"""
        if "aliases" in kwargs:
            al = kwargs.pop("aliases")
            if isinstance(al, str):
                self.aliases = al

    # def get_aliases(self) -> list[str]:
    #     al = self.aliases.split(";")
    #     return al

    # def set_aliases(self, al: list[str]):
    #     self.aliases = al.join(";")

    def __lt__(self, other) -> bool:
        # required by sort()
        return self.name < other.name

# -----------------------------------------------------------------------------

class ComponentMRU:
    """Most Recently Used for a given component filter"""

    def __init__(self, fltr="", mru_components:list[str]=None):
        self.filter = fltr
        self.mru = mru_components if mru_components else []

    def on_select(self, selection: str):
        """put the new selection on the top of the MRU list"""
        try:
            self.mru.remove(selection)
        except Exception:
            pass
        finally:
            self.mru.insert(0, selection)

    def __lt__(self, other) -> bool:
        # required by sort()
        return self.filter < other.filter

# -----------------------------------------------------------------------------

class ComponentsMRU:
    MRU_MAX_LEN = 5
    SPACER_ITEM = "————————=————————=————————=————————"

    def __init__(self):
        self.mru: list[ComponentMRU] = []
        self.__db_folder = ""
        self.dirty = False

    def load(self, db_folder: str):
        self.__db_folder = db_folder
        mru_file_path = os.path.join(self.__db_folder, "mru.csv")
        if os.path.isfile(mru_file_path):
            self.__load_csv(mru_file_path)
        else:
            # check if the old-name file exists
            lru_file_path = os.path.join(self.__db_folder, "lru.csv")
            if os.path.isfile(lru_file_path):
                self.__load_csv(lru_file_path)

    def save_changes(self):
        self.mru.sort()
        mru_file_path = os.path.join(self.__db_folder, "mru.csv")
        self.__save_csv(mru_file_path)
        # remove old file
        lrupath = os.path.join(self.__db_folder, "lru.csv")
        if os.path.isfile(lrupath):
            os.remove(lrupath)
        self.dirty = False

    def arrange(self, filter: str, items_to_arrange: list[str]):
        filter = filter.strip()
        if not filter:
            return

        for component in self.mru:
            if component.filter == filter:
                # if MRU list is not empty
                if component.mru:
                    # make a sets, remove from items_to_arrange items found in MRU
                    mru_set = set(component.mru)
                    to_arrange_set = set(items_to_arrange)
                    to_arrange_set -= mru_set
                    # put remaining items back into the items_to_arrange list
                    items_to_arrange.clear()
                    items_to_arrange.extend(to_arrange_set)
                    items_to_arrange.sort()
                    items_to_arrange.insert(0, self.SPACER_ITEM)
                    # insert MRU at the top of items_to_arrange
                    for item in component.mru[::-1]:
                        items_to_arrange.insert(0, item)
                return
        # not found? create a new entry, with empty MRU
        self.mru.append(ComponentMRU(filter))
        self.dirty = True

    def get_all_mru_components(self) -> set[str]:
        """returns a set of all components used in a MRU lists"""
        all = set()
        for component_mru in self.mru:
            for item in component_mru.mru:
                all.add(item)
        return all

    def remove_invalid_mru_components(self, invalid: set[str]):
        if invalid:
            # not empty? proceed
            logger.debug("MRU cleanup")
            for component_mru in self.mru:
                toremove = []
                for mru_item in component_mru.mru:
                    if mru_item in invalid:
                        toremove.append(mru_item)
                for rem in toremove:
                    logger.debug(f"  remove '{rem}'")
                    component_mru.mru.remove(rem)
                    self.dirty = True

    def on_select(self, filter: str, selection: str):
        if not filter:
            return

        for component in self.mru:
            if component.filter == filter:
                component.on_select(selection)
                self.dirty = True
                break

    def __iterate_reader(self, csv_file):
        reader = csv.reader(csv_file, delimiter="\t")
        self.mru.clear()
        for row in reader:
            row_cells = [cell.strip() for cell in row]
            if len(row_cells) > 0:
                self.mru.append(ComponentMRU(row_cells[0], row_cells[1:]))

    def __load_csv(self, path: str):
        if os.path.exists(path):
            try:
                f = open(path, "r", encoding="utf-8")
                self.__iterate_reader(f)
            except Exception as e:
                logger.error(f"  MRU: not an UTF-8 encoding")
        else:
                logger.warning(f"  MRU file not found")

    def __save_csv(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            for item in self.mru:
                # only items with not-empty MRU list
                if item.mru:
                    f.write(f"\"{item.filter}\"")
                    # store a limited number of recently used
                    for idx, comp in enumerate(item.mru):
                        if idx == self.MRU_MAX_LEN:
                            break
                        if comp: # only not-empty entries
                            f.write(f"\t\"{comp}\"")
                    f.write("\n")


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
        self.dirty = False
        """list updated during operation"""
        self.mru_items = ComponentsMRU()
        """least recently used"""

        if "components_dict" in kwargs:
            components_dict = kwargs.pop("components_dict")
            assert isinstance(components_dict, dict)
            # https://docs.python.org/3/library/stdtypes.html?#dict.items
            for item in components_dict.items():
                # add all component variants into the same flat list
                self.__items.extend([Component(name=subitem) for subitem in item[1]])
            self.__items.sort()

    def load(self, db_folder: str):
        """Load latest database version"""
        logger.info(f"Initialize components database: {db_folder}")
        db_path_list = []
        for de in os.scandir(db_folder):
            db_fname: str = os.path.basename(de.path)
            if db_fname.startswith("components__") and db_fname.endswith(".csv"):
                logger.debug("  DB path: " + de.path)
                db_path_list.append(de.path)

        # if not empty
        if db_path_list:
            # sort files list to get the latest version
            db_path_list.sort(reverse=True)
            last_db_path = db_path_list[0]
            # extract filename from path
            db_fname: str = os.path.basename(last_db_path)
            logger.info(f"Loading components from: {db_fname}")
            # extract date part from filename
            try:
                # throw away the extension
                self.db_date = db_fname.split("__")[1].split(".")[0]
                time_tuple = time.strptime(self.db_date, self.FILENAME_DATE_FMT)
                self.db_date = time.strftime("%Y-%m-%d, %H:%M:%S", time_tuple)
            except Exception as e:
                logger.warning(f"Unable to parse file datetime: {e}")
                self.db_date = "?, ?"

            # read csv file
            self.__load_csv(last_db_path)
            self.db_file_path = last_db_path

            # read the MRU
            self.mru_items.load(db_folder)
            all_visible = set(self.names_visible())
            # get components in mru, that are not in the all_visible
            invalid_mru = self.mru_items.get_all_mru_components()
            invalid_mru -= all_visible
            self.mru_items.remove_invalid_mru_components(invalid_mru)
        else:
            logger.warning(f"No DB files found in {db_folder}")

    def __iterate_reader(self, csv_file):
        reader = csv.reader(csv_file, delimiter="\t")
        self.__items.clear()
        for row in reader:
            row_cells = [cell.strip() for cell in row]
            hidd = row_cells[1] == "x"
            al = row_cells[2] if len(row_cells) >= 3 else ""
            self.__items.append(Component(name=row_cells[0],
                                          hidden=hidd,
                                          aliases=al))

    def __load_csv(self, path: str):
        try:
            f = open(path, "r", encoding="utf-8")
            self.__iterate_reader(f)
        except Exception as e:
            logger.warning(f"  Not an UTF-8 encoding - opening in legacy ANSI mode")
            # for backward-compatibility, to open older DB file not saved as UTF-8
            f = open(path, "r", encoding="ansi")
            self.__iterate_reader(f)

    def add_new(self, new_items: list[Component]) -> int:
        """Iterate over new_items to add components not existing in current db"""
        items_set = set(item.name for item in self.__items)
        added = 0

        for new_item in new_items:
            if not new_item.name in items_set:
                self.__items.append(new_item)
                logger.debug(f"  + {new_item.name}")
                added += 1

        return added

    def __save_csv(self, db_file_path: str):
        with open(db_file_path, "w", encoding="utf-8") as f:
            for item in self.__items:
                hidden="x" if item.hidden else "_"
                f.write(f"\"{item.name}\"\t{hidden}\t\"{item.aliases}\"\n")

    def save_new(self, db_folder: str):
        """Save local DB to a CSV file with date-time"""
        self.__items.sort()
        now = time.strftime(self.FILENAME_DATE_FMT)
        db_file_path = os.path.join(db_folder, f"components__{now}.csv")
        try:
            self.__save_csv(db_file_path)
            self.db_file_path = db_file_path
        except Exception as e:
            logger.error(f"Error saving to file '{db_file_path}: {e}'")

    def save_changes(self):
        """Save local DB to the same file"""
        self.__items.sort()
        try:
            self.__save_csv(self.db_file_path)
            self.dirty = False
        except Exception as e:
            logger.error(f"Error saving changes to file '{self.db_file_path}: {e}'")

    def count_visible(self) -> int:
        """Returns the number of valid components"""
        n = 0
        for item in self.__items:
            if not item.hidden:
                n += 1
        return n

    def count_hidden(self) -> int:
        """Returns the number of hidden components"""
        n = 0
        for item in self.__items:
            if item.hidden:
                n += 1
        return n

    def items_all(self) -> list[Component]:
        """Returns all components"""
        return self.__items

    def items_filtered(self, needle: str, show_hidden: bool=False) -> list[Component]:
        """
        Returns components containing the needle
        :needle: space-separated keywords: "603", "603 2k2", ...
        :show_hidden: show components with the Hidden atrribute set
        :return List
        """
        needle = '*' + '*'.join(needle.split(' ')) + '*'
        result = []
        for item in self.__items:
            if show_hidden or not item.hidden:
                if fnmatch.fnmatch(f"{item.name};{item.aliases}", needle):
                    result.append(item)
        return result

    def names_visible(self) -> list[str]:
        names_list = list(item.name for item in self.items_all() if not item.hidden)
        return names_list

    def add_if_not_exists(self, component_name: str) -> bool:
        component_name = component_name.strip()
        if len(component_name) < 3:
            logger.warning(f"Cannot add component '{component_name}' - the name must be 3 characters long at least")
            return False

        component_name_lower = component_name.lower()
        for item in self.__items:
            if item.name.lower() == component_name_lower:
                return False
        self.__items.append(Component(name=component_name))
        self.dirty = True
        return True
