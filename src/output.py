import logger
import os
import tkinter

from project import Project
from msg_box import MessageBox
from pnp_editor_helpers import Marker, PnPEditorData
from config import Config

# -----------------------------------------------------------------------------

def write_yamaha_csv(application, csv_path: str, csv_postfix: str, glob_proj: Project, editor_data: PnPEditorData):
    yamaha_csv_path = os.path.splitext(csv_path)[0]
    if csv_postfix:
        yamaha_csv_path += "_edited(" + csv_postfix + ").csv"
    else:
        yamaha_csv_path += "_edited.csv"

    write_errors = 0

    try:
        with open(yamaha_csv_path, "w", encoding="utf-8") as f:
            all_components : dict[str, int] = {}

            for i, pnp_item in enumerate(editor_data.items_all()):
                if not pnp_item.editor_selection:
                    continue

                if pnp_item.marker.value == Marker.REMOVED:
                    logger.debug(f"Skipped: '{pnp_item.id}'")
                    continue

                # source document row:
                pnp_grid_row = glob_proj.pnp_grid.rows()[i]

                yamaha_columns = (
                    pnp_item.editor_selection,
                    pnp_item.id,
                    pnp_item.comment,

                    pnp_grid_row[glob_proj.pnp_columns.xcoord_col],
                    pnp_grid_row[glob_proj.pnp_columns.ycoord_col],
                    "",
                    pnp_item.rotation,
                    pnp_grid_row[glob_proj.pnp_columns.layer_col] if glob_proj.pnp_columns.layer_col >= 0 else ""
                )

                n_components = all_components.get(pnp_item.editor_selection, 0)
                all_components[pnp_item.editor_selection] = n_components + 1

                # original row content + descr + empty column:
                out_row = pnp_grid_row.copy()
                out_row.append(pnp_item.descr)
                out_row_str = ";".join([f'"{item}"' for item in out_row]) + ";;"
                # append new columns in Yamaha-expected order
                out_row_str += ";".join([f'"{item}"' for item in yamaha_columns]) + ";\n"

                try:
                    f.write(out_row_str)
                except UnicodeEncodeError as e:
                    logger.error(f"Encoding error in: {i}. {out_row_str} -> {e}")
                    write_errors += 1
                except Exception as e:
                    logger.error(f"Unknown error in: {i}. {out_row_str} -> {e}")
                    write_errors += 1

        if write_errors == 0:
            logger.info(f"Yamaha PnP saved to: {yamaha_csv_path}")
            _write_components_summary(csv_path, all_components)
            MessageBox(app=application, dialog_type="o",
                        message="Yamaha PnP saved to:\n\n" +
                                f"{os.path.dirname(yamaha_csv_path)}/\n" +
                                f"{os.path.basename(yamaha_csv_path)}",
                        callback=lambda btn: btn)
        else:
            logger.warning(f"Yamaha PnP saved to: {yamaha_csv_path} with {write_errors} errors")
            MessageBox(app=application, dialog_type="o",
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
        with open(summary_path, "w", encoding="utf-8") as f:
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
