import logger
import os

# -----------------------------------------------------------------------------

"""
The DevLibEd.Lib file consists a number of DEVLIB_COMPONENT_SIZE bytes long records,
each starting with the 82 bytes long component name.

The DevLibEd2.Lib consists a number of DEVLIB2_COMPONENT_SIZE bytes long records.
"""

DEVLIB_OFFSET = 160
DEVLIB_HEADER = "Ver500"
DEVLIB_COMPONENT_SIZE = 640
DEVLIB2_COMPONENT_SIZE = 2048
DEVLIB_COMPONENT_NAME_SIZE = 82
DEVLIB_COMPONENT_BASENAME_SIZE = 44

class DevLibFile:
    def __init__(self, path: str):
        self.file_name = os.path.basename(path)
        """.Lib filename"""
        # self.items: dict[str, list[(str, str)]] = {}
        self.items: dict[str, list[str]] = {}
        """dictionary with lower-case component name : list of component names"""
        if not self.__scan(path, True):
            self.items.clear()
            self.__scan(path, False)

    def __scan(self, path: str, lib_v1: bool) -> bool:
        with open(path, "rb") as f:
            header_bytes = f.read(len(DEVLIB_HEADER))
            header_str = header_bytes.decode()
            if header_str != DEVLIB_HEADER:
                logger.error(f"File '{path}' has no expected header")
                return False

            n = 0
            component_size = DEVLIB_COMPONENT_SIZE if lib_v1 else DEVLIB2_COMPONENT_SIZE

            while True:
                f.seek(DEVLIB_OFFSET + (n * component_size), 0) # seek from the beginning
                n += 1
                name_bytes = f.read(DEVLIB_COMPONENT_NAME_SIZE)
                # _base_bytes = f.read(DEVLIB_COMPONENT_BASENAME_SIZE)

                if len(name_bytes) == DEVLIB_COMPONENT_NAME_SIZE:
                    # "2512_R_7,5R/5%/1W(3)\x00\x00\x00\x00\x00\x00\x00" -> "2512_R_7,5R/5%/1W(3)"
                    if name_bytes[0] == 0:
                        # component name can't start with nul (it may if the file is Ed2.Lib)
                        logger.warning(f"Component name starts with NULL - Ed2.Lib?")
                        return False

                    if (nul_idx := name_bytes.find(0)) >= 0:
                        name_bytes = name_bytes[0:nul_idx]

                    # if (nul_idx := base_bytes.find(0)) >= 0:
                    #     base_bytes = base_bytes[0:nul_idx]

                    if name_str := self.__decode_name(n, name_bytes):
                        if name_str.endswith(")"):
                            # "2512_R_7,5R/5%/1W(3)" -> "2512_R_7,5R/5%/1W"
                            if (par_open_idx := name_str.rfind("(")) >= 0:
                                name_str = name_str[0:par_open_idx]

                        name_str = name_str.strip()

                        if len(name_str):
                            key = name_str.lower()
                            if lst := self.items.get(key):
                                # lst.append((name_str, base_str))
                                lst.append(name_str)
                            else:
                                # self.items[key] = [(name_str, base_str)]
                                self.items[key] = [name_str]
                            logger.debug(f"    {n:3}. {name_str}")
                else:
                    break

        return True

    def __decode_name(self, idx: int, input: bytes) -> str:
        try:
            # name_str = name_bytes.decode(encoding="utf-8", errors="replace")
            name_str = input.decode(encoding="utf-8", errors="strict")
            return name_str
        except Exception as e:
            try:
                name_str = input.decode(encoding="ansi", errors="strict")
                name_bytes = name_str.encode(encoding="utf-8")
                name_str = name_bytes.decode(encoding="utf-8", errors="replace")
                return name_str
            except Exception as e:
                logger.warning(f"    Entry '{idx}' contains invalid characters: {e}")
                logger.warning(f"    {input}")
        return None
