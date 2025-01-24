import functools
import logger
import multiprocessing

from components import ComponentsDB
from project import Project

# -----------------------------------------------------------------------------

class Markers:
    CL_NOMATCH = "orange"
    CL_FILTER = "yellow"
    CL_AUTO_SEL = "lime"
    CL_MAN_SEL = "green"
    CL_REMOVED = "black"

    MARKERS_MAP_INV = {
        "NOMATCH": CL_NOMATCH,
        "FILTER": CL_FILTER,
        "AUTO_SEL": CL_AUTO_SEL,
        "MAN_SEL": CL_MAN_SEL,
        "REMOVED": CL_REMOVED
    }

    MARKERS_MAP = {
        CL_NOMATCH: "NOMATCH",
        CL_FILTER: "FILTER",
        CL_AUTO_SEL: "AUTO_SEL",
        CL_MAN_SEL: "MAN_SEL",
        CL_REMOVED: "REMOVED"
    }

# -----------------------------------------------------------------------------

# used for reading/parsing files
class PnpItem:
    def __init__(self):
        self.item = ""
        self.marker = None
        self.selection = None
        self.footprint = ""
        self.comment = ""
        self.cbx_items = list()
        self.rotation = ""
        self.descr = ""

    def __repr__(self) -> str:
        if not (self.footprint is None or self.comment is None):
            return self.footprint + "|" + self.comment
        raise RuntimeError("PnpItem without footprint/comment attributes")

# -----------------------------------------------------------------------------

class ItemsIterator:
    """
    Iterates over project rows from CSV or items read from the `*_wip.JSON` file
    """

    def __init__(self, project: Project, wip_items: list[dict] = None):
        self.__proj = project
        self.__proj_rows = None
        self.__wip_items = wip_items
        self.__idx = 0
        self.__id_max_w = None
        self.__fprint_max_w = None

    def __find_max_id_footprint_width(self):
        if self.__proj:
            id_max_w = 0
            fprint_max_w = 0
            fprint_col = self.__proj.pnp_columns.footprint_col
            rows = self.__proj.pnp_grid.rows()
            for row in rows:
                fprint_max_w = max(fprint_max_w, len(row[fprint_col]))
                id_max_w = max(id_max_w, len(row[0]))
            self.__id_max_w = id_max_w
            self.__fprint_max_w = fprint_max_w

    def length(self) -> int:
        if self.__wip_items:
            return len(self.__wip_items)
        if self.__proj:
            return len(self.__proj.pnp_grid.rows())
        return 0

    def __iter__(self):
        return self

    def __next__(self) -> PnpItem:
        # if provided, prefer WiP records over the current project
        if self.__wip_items:
            if self.__idx < len(self.__wip_items):
                wip_cmp = self.__wip_items[self.__idx]
                self.__idx += 1

                pnpitem = PnpItem()
                pnpitem.item = wip_cmp['item']
                pnpitem.marker = wip_cmp['marker']
                pnpitem.selection = wip_cmp['selection']
                pnpitem.footprint = None
                pnpitem.comment = None
                pnpitem.rotation = wip_cmp['rotation']
                pnpitem.descr = wip_cmp.get('descr', '')

                item_splitted: list[str] = pnpitem.item.split("|")

                if len(item_splitted) == 3:
                    # old
                    # "C42  | SMC_B              | 100u/10V "
                    pnpitem.footprint = item_splitted[1].strip()
                    pnpitem.comment = item_splitted[2].strip()
                elif len(item_splitted) == 4:
                    # new
                    # "002 | C11  | WCAP-CSGP_1210_H0.95 | 1nF "
                    pnpitem.footprint = item_splitted[2].strip()
                    pnpitem.comment = item_splitted[3].strip()
                else:
                    raise RuntimeError(f"Invalid item: '{pnpitem.item}'")

                return pnpitem

            # print(f"STOP1")
            raise StopIteration

        if self.__proj:
            if self.__proj_rows is None:
                # cache the list, because each call to rows() creates a new list
                self.__proj_rows = self.__proj.pnp_grid.rows()

            if self.__idx < len(self.__proj_rows):
                if not self.__id_max_w:
                    self.__find_max_id_footprint_width()

                row = self.__proj_rows[self.__idx]
                self.__idx += 1

                item = "{idx:0>3} | {id:{id_w}} | {ftprint:{fprint_w}} | {cmnt} ".format(
                    idx=self.__idx,
                    id=row[0],
                    id_w=self.__id_max_w,
                    ftprint=row[self.__proj.pnp_columns.footprint_col],
                    fprint_w=self.__fprint_max_w,
                    cmnt=row[self.__proj.pnp_columns.comment_col]
                )

                pnpitem = PnpItem()
                pnpitem.item = item
                pnpitem.marker = None
                pnpitem.selection = None
                pnpitem.footprint = row[self.__proj.pnp_columns.footprint_col]
                pnpitem.comment = row[self.__proj.pnp_columns.comment_col]
                pnpitem.rotation = row[self.__proj.pnp_columns.rot_col]
                pnpitem.descr = row[self.__proj.pnp_columns.descr_col] if self.__proj.pnp_columns.descr_col >= 0 else ""
                return pnpitem

            # print(f"STOP2")
            raise StopIteration

        # print(f"STOP3")
        raise StopIteration

# -----------------------------------------------------------------------------

def prepare_editor_items(components: ComponentsDB, project: Project, wip_items: list[dict] = None) -> list[PnpItem]:
    # works well with `wip_items`, hangs the app for `project`:
    USE_MULTIPROCESS = False

    items_iterator = ItemsIterator(project, wip_items)
    names_visible = components.names_visible()
    out = []

    if USE_MULTIPROCESS:
        # processes=1 -> 26s
        # processes=4 -> 10s
        # processes=8 -> 9s
        # https://stackoverflow.com/questions/40283772/python-3-why-does-only-functions-and-partials-work-in-multiprocessing-apply-asy
        cache = dict()
        process_fn = functools.partial(__process_pnpitem, components=components, names_visible=names_visible, cache=cache)

        # https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.pool
        with multiprocessing.Pool(processes=4) as pool:
            # out = pool.map(process_fn, items_iterator)
            #
            # best results for chunksize=8:
            it = pool.imap(process_fn, items_iterator, chunksize=8)
            out = [item for item in it]
    else:
        # single thread: 24s
        cache = dict()
        for pnpitem in items_iterator:
            __process_pnpitem(pnpitem, components, names_visible, cache)
            out.append(pnpitem)

    return out

def __process_pnpitem(pnpitem: PnpItem, components: ComponentsDB, names_visible: list[str], cache: dict) -> PnpItem:
    # cache the component matching results:
    USE_CACHE = True

    if USE_CACHE:
        # for 270 items: 21s -> 8s
        # for 506 items: 41s -> 7s
        if cached := cache.get(repr(pnpitem)):
            pnpitem.selection = cached['selection']
            pnpitem.cbx_items = cached['cbx_items']
            pnpitem.marker    = cached['marker']
            return pnpitem

    if pnpitem.marker:
        # iterating over WiP items
        if pnpitem.marker == Markers.MARKERS_MAP[Markers.CL_FILTER]:
            __try_find_matching(components, names_visible, pnpitem)
    else:
        # iterating over Project items
        __try_find_exact(components, names_visible, pnpitem)

    if USE_CACHE:
        cached = {
            'selection' : pnpitem.selection,
            'cbx_items' : pnpitem.cbx_items,
            'marker'    : pnpitem.marker,
        }
        cache[repr(pnpitem)] = cached

    return pnpitem


def __try_find_exact(components: ComponentsDB, names_visible: list[str], pnpitem: PnpItem):
    """
    Try to find exact component using footprint and comment
    """
    ftprint = pnpitem.footprint
    cmnt = pnpitem.comment

    try:
        expected_component = ftprint + "_" + cmnt
        # raise exception if not found:
        names_visible.index(expected_component)
        # if we are here - matching comonent was found
        pnpitem.selection = expected_component
        # record['cbx_items'] -> not needed
        pnpitem.marker = Markers.MARKERS_MAP[Markers.CL_AUTO_SEL]
        logger.info(f"  Matching component found: {expected_component}")
    except Exception:
        __try_find_matching(components, names_visible, pnpitem)


def __try_find_matching(components: ComponentsDB, names_visible: list[str], pnpitem: PnpItem):
    """
    Try to match component from the DB using item footprint nad comment
    """
    ftprint = pnpitem.footprint
    cmnt = pnpitem.comment
    # "1206_R_1,2k" -> "1206"
    ftprint_prefix = ftprint.split("_")

    if len(ftprint_prefix) > 0:
        ftprint_prefix = ftprint_prefix[0]

        # "CAPC0805(2012)100_L" -> "0805"
        for ftprint_sz in ("0402", "0603", "0805", "1206", "1210", "2512"):
            if ftprint_sz in ftprint_prefix:
                ftprint_prefix = ftprint_sz
                break

        # create a proposition list based on a footprint and the comment
        fltr = ftprint_prefix + " " + cmnt
        filtered_comp_names = list(item.name for item in components.items_filtered(fltr))
        if len(filtered_comp_names) > 0:
            pnpitem.selection = fltr.lower()
            pnpitem.cbx_items = filtered_comp_names
            pnpitem.marker = Markers.MARKERS_MAP[Markers.CL_FILTER]
            # insert MRU items at the top of the `cbx_items` list
            components.mru_items.arrange(pnpitem.selection, pnpitem.cbx_items)
            return

    # create component list proposition based only on the comment
    fltr = cmnt
    filtered_comp_names = list(item.name for item in components.items_filtered(fltr))

    if len(filtered_comp_names) > 0:
        pnpitem.selection = fltr.lower()
        pnpitem.cbx_items = filtered_comp_names
        pnpitem.marker = Markers.MARKERS_MAP[Markers.CL_FILTER]
        components.mru_items.arrange(pnpitem.selection, pnpitem.cbx_items)
        return

    # remove filter and assign all components
    pnpitem.selection = ""
    pnpitem.cbx_items = names_visible
    pnpitem.marker = Markers.MARKERS_MAP[Markers.CL_NOMATCH]

# -----------------------------------------------------------------------------

class Marker:
    """State of selection of the given somponent"""

    NOMATCH = "NOMATCH"
    FILTER = "FILTER"
    AUTO_SEL = "AUTO_SEL"
    MAN_SEL = "MAN_SEL"
    REMOVED = "REMOVED"
    __enums = [NOMATCH, FILTER, AUTO_SEL, MAN_SEL, REMOVED]

    CL_NOMATCH = "orange"
    CL_FILTER = "yellow"
    CL_AUTO_SEL = "lime"
    CL_MAN_SEL = "green"
    CL_REMOVED = "black"
    __colors = [CL_NOMATCH, CL_FILTER, CL_AUTO_SEL, CL_MAN_SEL, CL_REMOVED]

    ENUM_TO_COLOR = {
        NOMATCH:    CL_NOMATCH,
        FILTER:     CL_FILTER,
        AUTO_SEL:   CL_AUTO_SEL,
        MAN_SEL:    CL_MAN_SEL,
        REMOVED:    CL_REMOVED
    }

    COLOR_TO_ENUM = {
        CL_NOMATCH: NOMATCH,
        CL_FILTER:  FILTER,
        CL_AUTO_SEL:AUTO_SEL,
        CL_MAN_SEL: MAN_SEL,
        CL_REMOVED: REMOVED
    }

    def __init__(self):
        self.__value = Marker.NOMATCH

    def get_value(self):
        return self.__value

    def set_value(self, val: str):
        if val in Marker.__enums:
            self.__value = val

    def get_color(self):
        return Marker.ENUM_TO_COLOR[self.__value]

class PnPEditorItem:
    """Represents a single row of the PnP editor"""

    def __init__(self):
        # index | name | footprint
        self.item: str = ""
        # extra descr, like 5% resistor
        self.descr: str = ""
        # component selection state
        self.marker = Marker()
        # filter entered by user / selected from the combo-box
        self.component_filter: str = ""
        # currently entered/selected component
        self.component_selection: str = ""
        # list of component combobox items
        self.component_cbitems: list[str] = []
        # label with component length
        self.component_namelength: str = ""
        # selected component rotation
        self.rotation: str = ""

class PnPEditorData:
    """Represents an entire data of the editor"""

    ROWS_PER_PAGE = 200

    def __init__(self):
        # index | name | footprint
        self.items: list[PnPEditorItem] = []
        # row index
        self.current_idx = 0
        # page index,
        self.page_index = 0

    def load(self, items: list[PnpItem]):
        pass
