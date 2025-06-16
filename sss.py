# -*- coding: utf-8 -*-
"""
HFSS EXTRACTOR — full model history + all entities
Creates
  • HFSS_Extract_<project>_<design>_<timestamp>.json
  • HFSS_Extract_<project>_<design>_<timestamp>_variables.csv
"""

import os, json, csv
from datetime import datetime
from pyaedt import Desktop, Hfss

# ───────────── USER OPTIONS ───────────── #
PROJECT_PATH = None        # r"C:\path\file.aedt"  or None → attach to open
DESIGN_NAME  = None        # "MyDesign"            or None → active design
AEDT_VERSION = None        # "2024.2"              or None
EXPORT_CSV   = True
# ───────────────────────────────────────── #

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
desktop = Desktop(specified_version=AEDT_VERSION, new_desktop=False)

# 1 ▪ project -------------------------------------------------------------
if PROJECT_PATH and os.path.isfile(PROJECT_PATH):
    project_hdl = desktop.open_project(PROJECT_PATH)
else:
    project_hdl = desktop.active_project()
if project_hdl is None:
    raise RuntimeError("No project open — open one in AEDT or set PROJECT_PATH")

# 2 ▪ design (robust) -----------------------------------------------------
if DESIGN_NAME:
    design_name = DESIGN_NAME               # user specified
else:
    active_des = project_hdl.GetActiveDesign()     # PROJECT method  ← ()
    if active_des is None:
        raise RuntimeError("Project has no active design; set DESIGN_NAME")
    design_name = active_des.GetName()              # always a string

# 3 ▪ attach HFSS ---------------------------------------------------------
hfss = Hfss(projectname=project_hdl.name,           # <-- pass .name
            designname=design_name,
            specified_version=AEDT_VERSION,
            new_desktop=False, close_on_exit=False)

print("✓ Project:", hfss.project_name)
print("✓ Design :", hfss.design_name)

mdl = hfss.modeler

# ───────── helper collectors ───────── #
def grab_vars():
    vm = hfss.variable_manager
    return getattr(vm, "variables",
           getattr(vm, "properties", {}))

def grab_mats():
    return list(hfss.materials.material_keys)

def grab_objects():
    out = {}
    for h in mdl.objects:
        names = [h.name] if hasattr(h, "name") else mdl.get_object_name(h)
        if isinstance(names, str):
            names = [names]
        for n in names:
            if not mdl.does_object_exist(n) or mdl.is_group(n):
                continue
            try:
                bbox = mdl.get_bounding_box(n)
            except Exception:
                bbox = []
            if not bbox and mdl.get_object_material(n, "") in ("", "Unknown"):
                continue          # skip ghost numeric IDs
            out[n] = {
                "material"    : mdl.get_object_material(n, "") or "Unknown",
                "color"       : getattr(h, "color", None),
                "primitive"   : mdl.get_object_type(n) or "Unknown",
                "params"      : mdl.get_object_parameters(n) or {},
                "faces"       : mdl.get_object_faces(n) or [],
                "bounding_box": bbox,
                "history"     : mdl.get_object_history(n)
            }
    return out

def grab_bounds_ports():
    bnd, prt = {}, {}
    for bd in hfss.boundaries:
        e = {"type": bd.type, "props": bd.props}
        try:
            e["faces"] = hfss.boundaries.get_boundary_faces(bd.name)
        except Exception:
            e["faces"] = []
        (prt if "port" in bd.type.lower() else bnd)[bd.name] = e
    return bnd, prt

def grab_setups():
    return {s.name: {"props": s.props,
                     "sweeps": {sw.name: sw.props for sw in s.sweeps}}
            for s in hfss.setups}

csm  = mdl.CoordinateSystemManager
mesh = hfss.mesh

data = {
    "meta": {"timestamp": ts,
             "project": hfss.project_name,
             "design":  hfss.design_name,
             "aedt_version": desktop.release},
    "variables"      : grab_vars(),
    "materials"      : grab_mats(),
    "objects"        : grab_objects(),
    "analysis_setups": grab_setups(),
    "coord_systems"  : {n: csm.GetCoordinateSystem(n)
                        for n in csm.ListCoordinateSystems()},
    "mesh_ops"       : {m: mesh.meshoperations[m].props
                        for m in mesh.meshoperations},
    "history"        : hfss.odesign.GetModelHistory()
}
data["boundaries"], data["excitations"] = grab_bounds_ports()

# ───────── save ───────── #
base = f"HFSS_Extract_{hfss.project_name}_{hfss.design_name}_{ts}"
with open(base + ".json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
print("JSON  →", base + ".json")

if EXPORT_CSV:
    with open(base + "_variables.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Variable", "Value"])
        for k, v in data["variables"].items(): w.writerow([k, v])
    print("CSV   →", base + "_variables.csv")

hfss.release_desktop(close_projects=False, close_desktop=False)
print("✅  Extraction complete.")