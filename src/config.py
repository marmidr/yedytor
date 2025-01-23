import configparser
import os
import logger

# -----------------------------------------------------------------------------

# global config
class Config:
    CONFIG_FILE_NAME = "yedytor.ini"
    __instance = None

    @staticmethod
    def instance():
        """Returns singleton object"""
        if Config.__instance is None:
            Config.__instance = Config()
        return Config.__instance

    def __init__(self):
        # https://docs.python.org/3/library/configparser.html
        self.__config = configparser.ConfigParser()

        if os.path.isfile(self.CONFIG_FILE_NAME):
            try:
                self.__config.read(self.CONFIG_FILE_NAME, encoding="utf-8")
            except Exception as e:
                logger.error(f"Cannot read the program configuration file: {e}")

    def get_section(self, sect_name: str) -> configparser.SectionProxy:
        try:
            self.__config[sect_name]
        except Exception:
            self.__config[sect_name] = {}
        return self.__config[sect_name]

    def save(self):
        try:
            with open(self.CONFIG_FILE_NAME, 'w', encoding="utf-8") as f:
                self.__config.write(f)
        except Exception as e:
            logger.error(f"Cannot write the program configuration file: {e}")

    @property
    def editor_font_idx(self) -> int:
        idx = self.get_section("common").get("editor_font_idx", fallback=0)
        idx = int(idx)
        return idx

    @editor_font_idx.setter
    def editor_font_idx(self, new_idx: int):
        new_idx = str(new_idx)
        self.get_section("common")["editor_font_idx"] = new_idx

    @property
    def recent_pnp_path(self) -> str:
        path = self.get_section("common").get("recent_pnp_path", fallback="")
        return path

    @property
    def recent_pnp2_path(self) -> str:
        path = self.get_section("common").get("recent_pnp2_path", fallback="")
        return path

    @recent_pnp_path.setter
    def recent_pnp_path(self, paths: list[str]):
        path1 = paths[0] if len(paths) > 0 else ""
        path2 = paths[1] if len(paths) > 1 else ""
        self.get_section("common")["recent_pnp_path"] = path1
        self.get_section("common")["recent_pnp2_path"] = path2

    @property
    def recent_board_top_path(self) -> str:
        path1 = self.get_section("common").get("recent_board_top_path", fallback="")
        return path1

    @property
    def recent_board_bot_path(self) -> str:
        path2 = self.get_section("common").get("recent_board_bot_path", fallback="")
        return path2

    @recent_board_top_path.setter
    def recent_board_top_path(self, path: str):
        self.get_section("common")["recent_board_top_path"] = path

    @recent_board_bot_path.setter
    def recent_board_bot_path(self, path: str):
        self.get_section("common")["recent_board_bot_path"] = path

    @property
    def tou_directory_path(self) -> str:
        path = self.get_section("common").get("tou_directory_path", fallback="")
        return path

    @tou_directory_path.setter
    def tou_directory_path(self, path: str):
        self.get_section("common")["tou_directory_path"] = path

    @property
    def devlib_path(self) -> str:
        path = self.get_section("common").get("devlib_path", fallback="")
        return path

    @devlib_path.setter
    def devlib_path(self, path: str):
        self.get_section("common")["devlib_path"] = path

    @property
    def color_logs(self) -> bool:
        enabled = self.get_section("common").get("color_logs", fallback=False)
        return enabled == "True"

    @color_logs.setter
    def color_logs(self, enable: bool):
        new_en = str(enable)
        self.get_section("common")["color_logs"] = new_en

    @property
    def summary_comp_count(self) -> bool:
        enabled = self.get_section("common").get("summary_comp_count", fallback=False)
        return enabled == "True"

    @summary_comp_count.setter
    def summary_comp_count(self, enable: bool):
        new_en = str(enable)
        self.get_section("common")["summary_comp_count"] = new_en

    def write_settings(self, pnp_path: str, pnp_separator: str, pnp_first_row: int, pnp_columns: str, pnp2_path: str = ""):
        """Store a current project settings"""
        if pnp_path:
            pnp_path_key = pnp_path.replace(" ", "_").replace(":", "")
            sett = pnp_separator + "; " + str(pnp_first_row) + "; " + pnp_columns + "; " + pnp2_path
            self.get_section("recent")[pnp_path_key] = sett

    def read_settings(self, pnp_path: str) -> dict:
        """Load a recent project settings"""
        if pnp_path:
            pnp_path_key = pnp_path.replace(" ", "_").replace(":", "")
            recent_sett = self.get_section("recent").get(pnp_path_key, fallback="")
            if recent_sett:
                recent_sett = recent_sett.split(";")
                # safety padding
                while len(recent_sett) < 4:
                    recent_sett.append("")

                ret = {
                    "pnp_separator" : recent_sett[0].strip(),
                    "pnp_first_row" : recent_sett[1].strip(),
                    "pnp_columns"   : recent_sett[2].strip(),
                    "pnp2_path"     : recent_sett[3].strip()
                }
                return ret
            else:
                return None
