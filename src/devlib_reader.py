import logging
import os

# -----------------------------------------------------------------------------

"""
The DevLibEd.Lib file consists a number of DEVLIB_COMPONENT_SIZE bytes long records,
each starting with the 82 bytes long component name.
"""

DEVLIB_OFFSET = 160
DEVLIB_HEADER = "Ver500"
DEVLIB_COMPONENT_SIZE = 640
DEVLIB_COMPONENT_NAME_SIZE = 82
DEVLIB_COMPONENT_BASENAME_SIZE = 44

class DevLibFile:
    def __init__(self, path: str):
        self.file_name = os.path.basename(path)
        """.Lib filename"""
        # self.items: dict[str, list[(str, str)]] = {}
        self.items: dict[str, list[str]] = {}
        """dictionary with lower-case component name : list of component names"""

        with open(path, "rb") as f:
            header_bytes = f.read(len(DEVLIB_HEADER))
            header_str = header_bytes.decode()
            if header_str != DEVLIB_HEADER:
                logging.error(f"File '{path}' has no expected header")
                return

            n = 0

            while True:
                f.seek(DEVLIB_OFFSET + (n * DEVLIB_COMPONENT_SIZE), 0) # seek from the beginning
                n += 1
                name_bytes = f.read(DEVLIB_COMPONENT_NAME_SIZE)
                _base_bytes = f.read(DEVLIB_COMPONENT_BASENAME_SIZE)

                if len(name_bytes) == DEVLIB_COMPONENT_NAME_SIZE:
                    # "2512_R_7,5R/5%/1W(3)\x00\x00\x00\x00\x00\x00\x00" -> "2512_R_7,5R/5%/1W(3)"
                    if (nul_idx := name_bytes.find(0)) >= 0:
                        name_bytes = name_bytes[0:nul_idx]

                    # if (nul_idx := base_bytes.find(0)) >= 0:
                    #     base_bytes = base_bytes[0:nul_idx]

                    try:
                        name_str = name_bytes.decode()
                        # base_str = base_bytes.decode()

                        if name_str.endswith(")"):
                            # "2512_R_7,5R/5%/1W(3)" -> "2512_R_7,5R/5%/1W"
                            if (par_open_idx := name_str.rfind("(")) >= 0:
                                name_str = name_str[0:par_open_idx]

                        if len(name_str):
                            key = name_str.lower()
                            if lst := self.items.get(key):
                                # lst.append((name_str, base_str))
                                lst.append(name_str)
                            else:
                                # self.items[key] = [(name_str, base_str)]
                                self.items[key] = [name_str]
                            logging.debug(f"    {n:3}. {name_str}")
                    except Exception as e:
                        logging.warning(f"    Entry '{n}' contains invalid characters: {e}")
                        logging.warning(f"    {name_bytes}")
                else:
                    break
