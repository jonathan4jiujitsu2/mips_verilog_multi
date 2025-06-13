# -*- coding: utf-8 -*-
"""
HFSS Property Extractor — PyAEDT Edition
=======================================

• Attaches to the *already-running* Electronics Desktop session (new_desktop=False).
• Works on Python 3.x only (no IronPython issues, no admin rights needed).
• Dumps variables, materials, 3-D objects, boundaries, excitations, and setups
  to JSON and optional CSV files.

Install once:
    pip install --user pyaedt
"""

import json, csv, os
from datetime import datetime
from typing import Dict, Any, Tuple, List

from pyaedt import Desktop, Hfss


# --------------------------------------------------------------------------- #
# ---------------------------  HELPER FUNCTIONS  ---------------------------- #
# --------------------------------------------------------------------------- #
def extract_variables(hfss: Hfss) -> Dict[str, Any]:
    return hfss.modeler.variable_manager.variables  # {name: value}


def extract_materials(hfss: Hfss) -> Dict[str, Dict[str, Any]]:
    mats = {}
    for mat_name, mat_obj in hfss.materials.material_keys.items():
        mats[mat_name] = mat_obj.material_appearance
    return mats


def extract_objects(hfss: Hfss) -> Dict[str, Dict[str, Any]]:
    objs = {}
    for obj in hfss.modeler.objects:  # iterator over Object3d instances
        bb = obj.bounding_box  # [xmin, ymin, zmin, xmax, ymax, zmax]
        objs[obj.name] = {
            "material": obj.material_name,
            "color": obj.color,
            "bounding_box": {
                "x_min": bb[0], "y_min": bb[1], "z_min": bb[2],
                "x_max": bb[3], "y_max": bb[4], "z_max": bb[5],
            },
        }
    return objs


def extract_boundaries_and_excitations(hfss: Hfss) -> Tuple[Dict, Dict]:
    boundaries, excitations = {}, {}
    for b in hfss.boundaries:
        b_dict = {"type": b.type, "props": b.props}
        if b.type.lower() in {"waveport", "lumpedport", "port"}:
            excitations[b.name] = b_dict
        else:
            boundaries[b.name] = b_dict
    return boundaries, excitations


def extract_setups(hfss: Hfss) -> Dict[str, Dict[str, Any]]:
    setups = {}
    for s in hfss.setups:
        sweeps = {sw.name: sw.props for sw in s.sweeps}
        setups[s.name] = {"props": s.props, "sweeps": sweeps}
    return setups


def save_json(data: Dict[str, Any], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("JSON  ->", file_path)


def save_csv(extractor_data: Dict[str, Any], file_prefix: str) -> None:
    # Variables
    with open(file_prefix + "_variables.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Variable", "Value"])
        for k, v in extractor_data["variables"].items(): w.writerow([k, v])

    # Objects
    with open(file_prefix + "_objects.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Object", "Material", "Bounding-Box"])
        for k, v in extractor_data["objects"].items():
            w.writerow([k, v["material"], json.dumps(v["bounding_box"])])

    print("CSV   ->", file_prefix + "_*.csv")


# --------------------------------------------------------------------------- #
# ------------------------------  MAIN  ------------------------------------- #
# --------------------------------------------------------------------------- #
def main() -> None:
    # -------- user-adjustable section -------------------------------------- #
    PROJECT_PATH = None        # r"C:\path\to\project.aedt"  or None = active
    DESIGN_NAME  = None        # "ReducedHeight_1"           or None = active
    AEDT_VERSION = "2024.2"    # or None -> whatever is running
    EXPORT_CSV   = True
    # ----------------------------------------------------------------------- #

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1) Attach to running Electronics Desktop
    d = Desktop(AEDT_VERSION, new_desktop=False, non_graphical=False)
    print("✓ Connected to AEDT", d.release)

    # 2) Open / activate project
    if PROJECT_PATH and os.path.isfile(PROJECT_PATH):
        prj = d.open_project(PROJECT_PATH)
    else:
        prj = d.active_project
    print("✓ Project:", prj.name)

    # 3) Activate design
    if DESIGN_NAME:
        hfss = Hfss(DESIGN_NAME, project=prj)
    else:
        hfss = Hfss(project=prj)  # grabs active HFSS design
    print("✓ Design :", hfss.design_name)

    # 4) Extract everything
    data = {
        "meta": {
            "timestamp": ts,
            "project": prj.name,
            "design": hfss.design_name,
            "aedt_version": d.release,
        },
        "variables": extract_variables(hfss),
        "materials": extract_materials(hfss),
        "objects"  : extract_objects(hfss),
        "boundaries": {}, "excitations": {},
        "setups": extract_setups(hfss),
    }
    data["boundaries"], data["excitations"] = extract_boundaries_and_excitations(hfss)

    # 5) Save
    base = f"HFSS_Extract_{prj.name}_{hfss.design_name}_{ts}"
    save_json(data, base + ".json")
    if EXPORT_CSV:
        save_csv(data, base)

    # 6) Tidy up (keep HFSS session alive)
    hfss.release_desktop(close_projects=False, close_desktop=False)
    print("✅ Extraction complete.")


if __name__ == "__main__":
    main()