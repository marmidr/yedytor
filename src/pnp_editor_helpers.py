import functools
import logging
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

class PnpItem:
    def __init__(self):
        self.item = ""
        self.marker = None
        self.selection = None
        self.footprint = ""
        self.comment = ""
        self.cbx_items = list()
        self.rotation = ""

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
        self._proj = project
        self._proj_rows = None
        self._wip_items = wip_items
        self._idx = 0
        self._id_max_w = None
        self._fprint_max_w = None

    def _find_max_id_footprint_width(self):
        if self._proj:
            id_max_w = 0
            fprint_max_w = 0
            fprint_col = self._proj.pnp_columns.footprint_col
            rows = self._proj.pnp_grid.rows()
            for row in rows:
                fprint_max_w = max(fprint_max_w, len(row[fprint_col]))
                id_max_w = max(id_max_w, len(row[0]))
            self._id_max_w = id_max_w
            self._fprint_max_w = fprint_max_w

    def length(self) -> int:
        if self._wip_items:
            return len(self._wip_items)
        if self._proj:
            return len(self._proj.pnp_grid.rows())
        return 0

    def __iter__(self):
        return self

    def __next__(self) -> PnpItem:
        # if provided, prefer WiP records over the current project
        if self._wip_items:
            if self._idx < len(self._wip_items):
                wip_cmp = self._wip_items[self._idx]
                self._idx += 1

                pnpitem = PnpItem()
                pnpitem.item = wip_cmp['item']
                pnpitem.marker = wip_cmp['marker']
                pnpitem.selection = wip_cmp['selection']
                pnpitem.footprint = None
                pnpitem.comment = None
                pnpitem.rotation = wip_cmp['rotation']

                # "C42  | SMC_B              | 100u/10V "
                item_splitted: list[str] = pnpitem.item.split("|")
                if len(item_splitted) == 3:
                    pnpitem.footprint = item_splitted[1].strip()
                    pnpitem.comment = item_splitted[2].strip()
                else:
                    raise RuntimeError(f"Invalid item: '{pnpitem.item}'")

                return pnpitem

            # print(f"STOP1")
            raise StopIteration

        if self._proj:
            if self._proj_rows is None:
                # cache the list, because each call to rows() creates a new list
                self._proj_rows = self._proj.pnp_grid.rows()

            if self._idx < len(self._proj_rows):
                if not self._id_max_w:
                    self._find_max_id_footprint_width()

                row = self._proj_rows[self._idx]
                self._idx += 1

                item = "{id:{id_w}} | {ftprint:{fprint_w}} | {cmnt} ".format(
                    id=row[0],
                    id_w=self._id_max_w,
                    ftprint=row[self._proj.pnp_columns.footprint_col],
                    fprint_w=self._fprint_max_w,
                    cmnt=row[self._proj.pnp_columns.comment_col]
                )

                pnpitem = PnpItem()
                pnpitem.item = item
                pnpitem.marker = None
                pnpitem.selection = None
                pnpitem.footprint = row[self._proj.pnp_columns.footprint_col]
                pnpitem.comment = row[self._proj.pnp_columns.comment_col]
                pnpitem.rotation = row[self._proj.pnp_columns.rot_col]
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
        process_fn = functools.partial(_process_pnpitem, components=components, names_visible=names_visible, cache=cache)

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
            _process_pnpitem(pnpitem, components, names_visible, cache)
            out.append(pnpitem)

    return out

def _process_pnpitem(pnpitem: PnpItem, components: ComponentsDB, names_visible: list[str], cache: dict) -> PnpItem:
    # cache the component matching results:
    USE_CACHE = True

    if USE_CACHE:
        # for 270 items: 21s -> 8s
        # for 506 items: 41s -> 7s
        if cached := cache.get(repr(pnpitem)):
            pnpitem.selection = cached['selection']
            pnpitem.cbx_items = cached['cbx_items']
            pnpitem.marker = cached['marker']
            return pnpitem

    if pnpitem.marker:
        # iterating over WiP items
        if pnpitem.marker == Markers.MARKERS_MAP[Markers.CL_FILTER]:
            _try_find_matching(components, names_visible, pnpitem)
    else:
        # iterating over Project items
        _try_find_exact(components, names_visible, pnpitem)

    if USE_CACHE:
        cached = {
            'selection' : pnpitem.selection,
            'cbx_items' : pnpitem.cbx_items,
            'marker' : pnpitem.marker,
        }
        cache[repr(pnpitem)] = cached

    return pnpitem


def _try_find_exact(components: ComponentsDB, names_visible: list[str], pnpitem: PnpItem):
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
        logging.info(f"  Matching component found: {expected_component}")
    except Exception:
        _try_find_matching(components, names_visible, pnpitem)


def _try_find_matching(components: ComponentsDB, names_visible: list[str], pnpitem: PnpItem):
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
            return

    # create component list proposition based only on the comment
    fltr = cmnt
    filtered_comp_names = list(item.name for item in components.items_filtered(fltr))

    if len(filtered_comp_names) > 0:
        pnpitem.selection = fltr.lower()
        pnpitem.cbx_items = filtered_comp_names
        pnpitem.marker = Markers.MARKERS_MAP[Markers.CL_FILTER]
        return

    # remove filter and assign all components
    pnpitem.selection = ""
    pnpitem.cbx_items = names_visible
    pnpitem.marker = Markers.MARKERS_MAP[Markers.CL_NOMATCH]
