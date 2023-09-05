import configparser
import os

# -----------------------------------------------------------------------------

# global config
class Config:
    CONFIG_FILE_NAME = "yedytor.ini"

    def __init__(self):
        # https://docs.python.org/3/library/configparser.html
        self.__config = configparser.ConfigParser()

        if os.path.isfile(self.CONFIG_FILE_NAME):
            self.__config.read(self.CONFIG_FILE_NAME)
        else:
            self.__config['common'] = {
                "initial_dir": "",
                "editor_font_idx": 0 # 12px
            }

    def get_section(self, sect_name: str) -> configparser.SectionProxy:
        try:
            self.__config[sect_name]
        except Exception:
            self.__config[sect_name] = {}
        return self.__config[sect_name]

    def save(self):
        with open(self.CONFIG_FILE_NAME, 'w') as f:
            self.__config.write(f)

    @property
    def editor_font_idx(self) -> int:
        idx = self.get_section('common')["editor_font_idx"]
        idx = int(idx)
        return idx

    @editor_font_idx.setter
    def editor_font_idx(self, new_idx: int):
        new_idx = str(new_idx)
        self.get_section('common')["editor_font_idx"] = new_idx
