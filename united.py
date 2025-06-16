# -*- coding: utf-8 -*-
"""
HFSS Property Extractor – FULL HISTORY
Creates HFSS_Extract_<project>_<design>_<timestamp>.json (+ _variables.csv)
with:
  • design & project variables
  • user materials
  • every solid / sheet  (material, colour, primitive params, faces, bbox)
  • per-object history  + full project history
  • ports, boundaries
  • coordinate systems, mesh operations, analysis setups, sweeps, reports
"""

import os, json, csv
from datetime import datetime
from pyaedt import Desktop, Hfss

# ────────── USER SETTINGS ────────── #
PROJECT_PATH = None     # r"C:\path\file.aedt" or None to attach
DESIGN_NAME  = None     # None = active design
AEDT_VERSION = None     # "2024.2" or None = auto
EXPORT_CSV   = True
# ─────────────────────────────────── #

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
d  = Desktop(specified_version=AEDT_VERSION, new_desktop=False)

# attach / open project ---------------------------------------------------
if PROJECT_PATH and os.path.isfile(PROJECT_PATH):
    prj = d.open_project(PROJECT_PATH)
else:
    prj = d.active_project()                     # ← CALL the method
if prj is None:
    raise RuntimeError("No active project – open one or set PROJECT_PATH")

# create / attach design --------------------------------------------------
if DESIGN_NAME:
    hfss = Hfss(projectname=prj.name, designname=DESIGN_NAME,
                specified_version=AEDT_VERSION, new_desktop=False,
                close_on_exit=False)
else:
    hfss = Hfss(project=prj, specified_version=AEDT_VERSION,
                new_desktop=False, close_on_exit=False)

print("✓ Project:", hfss.project_name)
print("✓ Design :", hfss.design_name)

# ───────── helpers ───────── #
def get_variables():
    vm = hfss.variable_manager
    for attr in ("variables", "properties"):
        if hasattr(vm, attr):
            return getattr(vm, attr)
    return {n: hfss.odesign.GetVariableValue(n)
            for n in hfss.odesign.GetVariables()}

def get_materials():
    return {m: {"name": m} for m in hfss.materials.material_keys}

def get_objects():
    mdl, out = hfss.modeler, {}
    for handle in mdl.objects:
        names = [handle.name] if hasattr(handle, "name") else mdl.get_object_name(handle)
        if isinstance(names, str):
            names = [names]
        for n in names:
            hist  = mdl.get_object_history(n)
            faces = mdl.get_object_faces(n)
            try:
                prim  = mdl.get_object_type(n)
                parms = mdl.get_object_parameters(n)
            except Exception:
                prim, parms = "Unknown", {}
            try:
                bbox = mdl.get_bounding_box(n)
            except Exception:
                bbox = []
            out[n] = {
                "material"     : mdl.get_object_material(n, "") if mdl.does_object_exist(n) else "Unknown",
                "color"        : getattr(handle, "color", None),
                "primitive"    : prim,
                "params"       : parms,
                "faces"        : faces,
                "bounding_box" : bbox,
                "history"      : hist
            }
    return out

def get_bounds_ports():
    bmod, bnd, exc = hfss.boundaries, {}, {}
    for b in bmod:
        entry = {"type": b.type, "props": b.props}
        try:
            entry["faces"] = bmod.get_boundary_faces(b.name)
        except Exception:
            entry["faces"] = []
        (exc if "port" in b.type.lower() else bnd)[b.name] = entry
    return bnd, exc

def get_setups():
    return {s.name: {"props": s.props,
                     "sweeps": {sw.name: sw.props for sw in s.sweeps}}
            for s in hfss.setups}

def get_coord_systems():
    csm = hfss.modeler.CoordinateSystemManager
    return {n: csm.GetCoordinateSystem(n) for n in csm.ListCoordinateSystems()}

def get_mesh_ops():
    mm = hfss.mesh
    return {m: mm.meshoperations[m].props for m in mm.meshoperations}

def get_reports():
    return {r.name: r.report_type for r in hfss.post.reports}

# ───────── collect all data ───────── #
data = {
    "meta": {"timestamp": ts, "project": hfss.project_name,
             "design": hfss.design_name, "aedt_version": d.release},
    "variables"       : get_variables(),
    "materials"       : get_materials(),
    "objects"         : get_objects(),
    "analysis_setups" : get_setups(),
    "coord_systems"   : get_coord_systems(),
    "mesh_ops"        : get_mesh_ops(),
    "reports"         : get_reports(),
    "history"         : hfss.odesign.GetModelHistory()
}
data["boundaries"], data["excitations"] = get_bounds_ports()

# ───────── save JSON / CSV ───────── #
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
print("✅  Extraction finished.")