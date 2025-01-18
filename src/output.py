import logger
import os
import tkinter

from project import Project
from msg_box import MessageBox
from pnp_editor_helpers import Markers
from config import Config

# -----------------------------------------------------------------------------

def write_yamaha_csv(app, csv_path: str, glob_proj: Project,
                     cbx_component: list[tkinter.Widget], cbx_rotation: list[tkinter.Widget],
                     lbl_marker: list[tkinter.Widget], entry_descr: list[tkinter.Widget]):

    yamaha_csv_path = os.path.splitext(csv_path)[0]
    yamaha_csv_path += "_edited.csv"

    write_errors = 0

    try:
        with open(yamaha_csv_path, "w", encoding="UTF-8") as f:
            all_components = {}

            for i, row in enumerate(glob_proj.pnp_grid.rows()):
                selected_component = cbx_component[i].get()
                selected_rotation = cbx_rotation[i].get()
                marker_bg = lbl_marker[i].cget("background")
                descr = entry_descr[i].get()

                if not selected_component:
                    continue

                if marker_bg == Markers.CL_REMOVED:
                    logger.debug(f"Skipped: '{row[glob_proj.pnp_columns.id_col]} | "
                                f"{row[glob_proj.pnp_columns.comment_col]}'")
                    continue

                yamaha_columns = (
                    selected_component,
                    row[glob_proj.pnp_columns.id_col],
                    row[glob_proj.pnp_columns.comment_col],
                    row[glob_proj.pnp_columns.xcoord_col],
                    row[glob_proj.pnp_columns.ycoord_col],
                    "",
                    selected_rotation,
                    row[glob_proj.pnp_columns.layer_col] if glob_proj.pnp_columns.layer_col >= 0 else ""
                )

                n = all_components.get(selected_component, 0)
                all_components[selected_component] = n + 1

                # original document content + empty column
                row.append(descr)
                row_str = ";".join([f'"{item}"' for item in row]) + ";;"
                # append new columns in Yamaha-expected order
                row_str += ";".join([f'"{item}"' for item in yamaha_columns]) + ";\n"

                try:
                    f.write(row_str)
                except UnicodeEncodeError as e:
                    logger.error(f"Encoding error in: {i}. {row_str} -> {e}")
                    write_errors += 1
                except Exception as e:
                    logger.error(f"Unknown error in: {i}. {row_str} -> {e}")
                    write_errors += 1

        if write_errors == 0:
            logger.info(f"Yamaha PnP saved to: {yamaha_csv_path}")
            _write_components_summary(csv_path, all_components)
        else:
            logger.warning(f"Yamaha PnP saved to: {yamaha_csv_path} with {write_errors} errors")
            MessageBox(app=app, dialog_type="o",
                        message=f"Encoding errors occured!\n\n{write_errors} items not saved",
                        callback=lambda btn: btn)

    except Exception as e:
        logger.error(f"{e}")

def _write_components_summary(csv_path: str, all_components = dict[str, int]):
    summary_path = os.path.splitext(csv_path)[0]
    summary_path += "_summary.txt"
    sorted_components = list(all_components.keys())
    sorted_components.sort()
    summary_comp_count = Config.instance().summary_comp_count

    try:
        with open(summary_path, "w", encoding="UTF-8") as f:
            total_elements = 0
            for c in sorted_components:
                total_elements = total_elements + all_components[c]
                if summary_comp_count:
                    report = f"{all_components[c]:3} × {c}\n"
                else:
                    report = f"{c}\n"
                f.write(report)

            f.write( "------------\n")
            f.write(f"Components: {len(sorted_components):4}\n")
            f.write(f"Total PnP:  {total_elements:4}\n")

    except Exception as e:
        logger.error(f"Cannot open file -> {e}")
