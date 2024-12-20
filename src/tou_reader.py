import logger
import os

# -----------------------------------------------------------------------------

TOU_COMPONENT_SIZE = 320
"""The .Tou file consists a number of 320 bytes long records"""

TOU_COMPONENT_NAME_SIZE = 40
"""...each starting with the 40 bytes long component name."""

class TouFile:
    def __init__(self, path: str):
        self.file_name = os.path.basename(path)
        """.Tou filename"""
        self.items: dict[str, list[str]] = {}
        """dictionary with lower-case component name : list of component names"""

        with open(path, "rb") as f:
            n = 0

            while True:
                f.seek(n * TOU_COMPONENT_SIZE, 0) # seek from the beginning
                n += 1
                name_bytes = f.read(TOU_COMPONENT_NAME_SIZE)

                if len(name_bytes) == TOU_COMPONENT_NAME_SIZE:
                    # name_bytes = name_bytes.rstrip(b"\x00 ")
                    if (nul_idx := name_bytes.find(0)) >= 0:
                        name_bytes = name_bytes[0:nul_idx]

                    try:
                        # "SOT23_BSS138\x00\x00\x00\x00\x00\x00\x00" -> "SOT23_BSS138"
                        name_str = name_bytes.decode()
                        if len(name_str):
                            key = name_str.lower()
                            if lst := self.items.get(key):
                                lst.append(name_str)
                            else:
                                self.items[key] = [name_str]
                            # logger.debug(f"    {n:3}. {name_str}")
                    except Exception as e:
                        logger.warning(f"    Entry '{n}' contains invalid characters: {e}")
                        logger.warning(f"    {name_bytes}")
                else:
                    break
