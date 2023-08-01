import logging
import os

# -----------------------------------------------------------------------------

class Component:
    """Current component name, eg R0603_1k"""
    name: str = ""
    """File the component was found"""
    tou_file_name: str = ""
    """Known, but don't show on the list"""
    ignored: bool = False

# -----------------------------------------------------------------------------

class ComponentDB:
    items_all: list[Component]
    items_filtered: list[Component]
    db_folder: str = ""

    def __init__(self, db_folder: str, *args, **kwargs):
        self.db_folder = db_folder
        self._load(db_folder)
        pass

    """Load database"""
    def _load(self, db_folder: str):
        db_file_path = os.path.join(db_folder, "components.csv")
        logging.info("Initialize components database: {db_file_path}")

    def save(self):
        # 1. make a copy with date-time
        # 2. save as a new file
        pass

    """Returns filtered components"""
    def get_items(self) -> list[Component]:
        return self.items_filtered

    """Returns all known components"""
    def get_items_all(self) -> list[Component]:
        return self.items_all
