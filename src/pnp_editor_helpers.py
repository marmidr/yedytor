#

import logging
# import multiprocessing

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

class ItemsIterator:
    """
    Iterates over project rows from CSV or items read from the `*_wip.JSON` file
    """

    def __init__(self, project: Project, wip_items: list[dict] = None):
        self._proj = project
        self._wip_items = wip_items
        self._idx = 0
        self._id_max_w = None
        self._fprint_max_w = None

    def _find_max_id_footprint_width(self):
        if self._proj:
            id_max_w = 0
            fprint_max_w = 0
            fprint_col = self._proj.pnp_columns.footprint_col
            for row in self._proj.pnp_grid.rows():
                fprint_max_w = max(fprint_max_w, len(row[fprint_col]))
                id_max_w = max(id_max_w, len(row[0]))
            self._id_max_w = id_max_w
            self._fprint_max_w = fprint_max_w

    def length(self):
        if self._wip_items:
            return len(self._wip_items)
        if self._proj:
            return len(self._proj.pnp_grid.rows())
        return 0

    def __iter__(self):
        return self

    def __next__(self):
        # if provided, prefer WiP records over the current project
        if self._wip_items:
            if self._idx < len(self._wip_items):
                wip_cmp = self._wip_items[self._idx]
                self._idx += 1

                record = {
                    'item': wip_cmp['item'],
                    'marker': wip_cmp['marker'],
                    'selection': wip_cmp['selection'],
                    'footprint': None,
                    'comment': None,
                    'cbx_items': []
                }
                return record
            raise StopIteration

        if self._proj:
            if self._idx < len(self._proj.pnp_grid.rows()):
                if not self._id_max_w:
                    self._find_max_id_footprint_width()

                row = self._proj.pnp_grid.rows()[self._idx]
                self._idx += 1

                item = "{id:{id_w}} | {ftprint:{fprint_w}} | {cmnt} ".format(
                    id=row[0], id_w=self._id_max_w,
                    ftprint=row[self._proj.pnp_columns.footprint_col], fprint_w=self._fprint_max_w,
                    cmnt=row[self._proj.pnp_columns.comment_col])

                record = {
                    'item': item,
                    'marker': None,
                    'selection': None,
                    'footprint': row[self._proj.pnp_columns.footprint_col],
                    'comment': row[self._proj.pnp_columns.comment_col],
                    'cbx_items': []
                }
                return record
            raise StopIteration

        raise StopIteration

# -----------------------------------------------------------------------------

def prepare_editor_items(components: ComponentsDB, project: Project, wip_items: list[dict] = None) -> list[dict]:
    items_iterator = ItemsIterator(project, wip_items)
    names_visible = components.names_visible()
    out = []

    for record in items_iterator:
        if record['footprint']:
            # iterating over Project items
            try_find_exact(components, names_visible, record)
        else:
            # iterating over WiP items
            if record['marker'] == Markers.MARKERS_MAP[Markers.CL_FILTER]:
                item_splitted: list[str] = record['item'].split("|")
                if len(item_splitted) == 3:
                    record['footprint'] = item_splitted[1].strip()
                    record['comment'] = item_splitted[2].strip()
                    try_find_matching(components, names_visible, record)

        out.append(record)
    return out


def try_find_exact(components: ComponentsDB, names_visible: list[str], record: dict):
    """
    Try to find exact component using footprint and comment
    """
    ftprint = record['footprint']
    cmnt = record['comment']

    try:
        expected_component = ftprint + "_" + cmnt
        names_visible.index(expected_component) # may raise exception if not found
        # if we are here - matching comonent was found
        record['selection'] = expected_component
        record['marker'] = Markers.MARKERS_MAP[Markers.CL_AUTO_SEL]
        logging.info(f"Matching component found: {expected_component}")
    except Exception:
        try_find_matching(components, names_visible, record)


def try_find_matching(components: ComponentsDB, names_visible: list[str], record: dict):
    """
    Try to match component from the DB using item footprint nad comment
    """
    ftprint = record['footprint']
    cmnt = record['comment']
    # "1206_R_1,2k" -> "1206"
    ftprint_prefix = ftprint.split("_")

    if len(ftprint_prefix) > 0:
        # create a proposal list based on a footprint and comment
        ftprint_prefix = ftprint_prefix[0]
        fltr = ftprint_prefix + " " + cmnt
        filtered_comp_names = list(item.name for item in components.items_filtered(fltr))
        if len(filtered_comp_names) > 0:
            record['selection'] = fltr.lower()
            record['cbx_items'] = filtered_comp_names
            record['marker'] = Markers.MARKERS_MAP[Markers.CL_FILTER]
            return

    # create component list proposal based only on comment
    fltr = cmnt
    filtered_comp_names = list(item.name for item in components.items_filtered(fltr))

    if len(filtered_comp_names) > 0:
        record['selection'] = fltr.lower()
        record['cbx_items'] = filtered_comp_names
        record['marker'] = Markers.MARKERS_MAP[Markers.CL_FILTER]
        return

    # remove filter and assign all components
    record['selection'] = ""
    record['cbx_items'] = names_visible
    record['marker'] = Markers.MARKERS_MAP[Markers.CL_NOMATCH]
