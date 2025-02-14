import functools
import logger
import multiprocessing

from components import ComponentsDB
from project import Project

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
        self.__is_set = False

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, val: str):
        if val in Marker.__enums:
            self.__value = val
            self.__is_set = True
        else:
            logger.warning(f"Unknown Marker value: {val}")

    @property
    def color(self) -> str:
        return Marker.ENUM_TO_COLOR[self.__value]

    def reset(self):
        self.__value = Marker.NOMATCH
        self.__is_set = False

    def is_set(self) -> bool:
        return self.__is_set


# -----------------------------------------------------------------------------

# used for reading/parsing files
class PnPEditorItem:
    """Represents a single row of the PnP editor"""

    def __init__(self):
        # index | name | footprint
        self.item: str = ""
        # extra descr, like 5% resistor
        self.descr: str = ""
        # component selection state
        self.marker = Marker()
        # selected component rotation
        self.rotation: str = ""
        #
        self.footprint = None
        self.comment = None
        # filter entered by user / selected from the combo-box
        self.editor_filter: str = ""
        # currently entered/selected component
        self.editor_selection: str = ""
        # list of component combobox items
        self.editor_cbx_items: list[str] = []

    def __repr__(self) -> str:
        if not (self.footprint is None or self.comment is None):
            return self.footprint + "|" + self.comment
        raise RuntimeError("PnpItem without footprint/comment attributes")


class PnPEditorData:
    """Represents an entire data of the editor"""

    ROWS_PER_PAGE = 200

    def __init__(self):
        self.__items: list[PnPEditorItem] = []
        self.page_no = 0

    # TODO: return filtered items
    def items(self):
        return self.__items

    def set_items(self, items: list[PnPEditorItem]):
        self.__items = items

    def item_offset(self) -> int:
        """Item offset, resulting from current page"""
        return self.page_no * PnPEditorData.ROWS_PER_PAGE

    def items_range(self) -> range:
        return range(self.item_offset(), self.item_offset() + PnPEditorData.ROWS_PER_PAGE)

    def item_raw(self, cmp_idx: int) -> PnPEditorItem:
        """Returns an item, starting at 0"""
        if cmp_idx >= 0 and cmp_idx < len(self.__items):
            return self.__items[cmp_idx]
        return None

    def item(self, wgt_idx: int) -> PnPEditorItem:
        """Returns an item, taking current page no into account"""
        # widget row index -> component index
        cmp_idx = wgt_idx + self.item_offset()

        if cmp_idx >= 0 and cmp_idx < len(self.__items):
            return self.__items[cmp_idx]
        return None

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

    def __next__(self) -> PnPEditorItem:
        # if provided, prefer WiP records over the current project
        if self.__wip_items:
            if self.__idx < len(self.__wip_items):
                wip_cmp = self.__wip_items[self.__idx]
                self.__idx += 1

                pnpitem = PnPEditorItem()
                pnpitem.item = wip_cmp['item']
                pnpitem.marker.value = wip_cmp['marker']
                pnpitem.editor_selection = wip_cmp['selection']
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

                pnpitem = PnPEditorItem()
                pnpitem.item = item
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

def prepare_editor_data(components: ComponentsDB, project: Project, wip_items: list[dict] = None) -> PnPEditorData:
    # works well with `wip_items`, hangs the app for `project`:
    USE_MULTIPROCESS = False

    items_iterator = ItemsIterator(project, wip_items)
    names_visible = components.names_visible()
    out = PnPEditorData()

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
            items = [item for item in it]
            out.set_items(items)
    else:
        # single thread: 24s
        cache = dict()
        for pnpitem in items_iterator:
            __process_pnpitem(pnpitem, components, names_visible, cache)
            out.items().append(pnpitem)

    return out

def __process_pnpitem(pnpitem: PnPEditorItem, components: ComponentsDB, names_visible: list[str], cache: dict) -> PnPEditorItem:
    # cache the component matching results:
    USE_CACHE = True

    if USE_CACHE:
        # for 270 items: 21s -> 8s
        # for 506 items: 41s -> 7s
        if cached := cache.get(repr(pnpitem)):
            pnpitem.editor_selection = cached['selection']
            pnpitem.editor_filter = pnpitem.editor_selection
            pnpitem.editor_cbx_items = cached['cbx_items']
            pnpitem.marker.value = cached['marker']
            return pnpitem

    if pnpitem.marker.is_set():
        # iterating over WiP items
        if pnpitem.marker.value == Marker.FILTER:
            __try_find_matching(components, names_visible, pnpitem)
    else:
        # iterating over Project items
        __try_find_exact(components, names_visible, pnpitem)

    if USE_CACHE:
        cached = {
            'selection' : pnpitem.editor_selection,
            'cbx_items' : pnpitem.editor_cbx_items,
            'marker'    : pnpitem.marker.value,
        }
        cache[repr(pnpitem)] = cached

    return pnpitem


def __try_find_exact(components: ComponentsDB, names_visible: list[str], pnpitem: PnPEditorItem):
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
        pnpitem.editor_selection = expected_component
        pnpitem.editor_filter = pnpitem.editor_selection
        # record['cbx_items'] -> not needed
        pnpitem.marker.value = Marker.AUTO_SEL
        logger.info(f"  Matching component found: {expected_component}")
    except Exception:
        __try_find_matching(components, names_visible, pnpitem)


def __try_find_matching(components: ComponentsDB, names_visible: list[str], pnpitem: PnPEditorItem):
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
            pnpitem.editor_selection = fltr.lower()
            pnpitem.editor_filter = pnpitem.editor_selection
            pnpitem.editor_cbx_items = filtered_comp_names
            pnpitem.marker.value = Marker.FILTER
            # insert MRU items at the top of the `cbx_items` list
            components.mru_items.arrange(pnpitem.editor_selection, pnpitem.editor_cbx_items)
            return

    # create component list proposition based only on the comment
    fltr = cmnt
    filtered_comp_names = list(item.name for item in components.items_filtered(fltr))

    if len(filtered_comp_names) > 0:
        pnpitem.editor_selection = fltr.lower()
        pnpitem.editor_filter = pnpitem.editor_selection
        pnpitem.editor_cbx_items = filtered_comp_names
        pnpitem.marker.value = Marker.FILTER
        components.mru_items.arrange(pnpitem.editor_selection, pnpitem.editor_cbx_items)
        return

    # remove filter and assign all components
    pnpitem.editor_selection = ""
    pnpitem.editor_filter = pnpitem.editor_selection
    pnpitem.editor_cbx_items = names_visible
    pnpitem.marker.value = Marker.NOMATCH

# -----------------------------------------------------------------------------

