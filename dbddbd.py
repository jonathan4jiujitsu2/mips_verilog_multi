# -*- coding: utf-8 -*-
"""
HFSS EXTRACTOR – FULL HISTORY
Creates HFSS_Extract_<proj>_<design>_<timestamp>.json (+ variables CSV)
with: variables, materials, objects (incl. history + faces), ports,
boundaries, analysis setups, mesh operations, coordinate systems, reports,
and full project history.

Run with HFSS open, or give PROJECT_PATH / DESIGN_NAME below.
"""

import os, json, csv
from datetime import datetime
from pyaedt import Desktop, Hfss


# ───── user tweakables ───── #
PROJECT_PATH = None     # r"C:\path\project.aedt" or None
DESIGN_NAME  = None
AEDT_VERSION = None
EXPORT_CSV   = True
# ─────────────────────────── #

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
d  = Desktop(specified_version=AEDT_VERSION, new_desktop=False)
if PROJECT_PATH and os.path.isfile(PROJECT_PATH):
    prj = d.open_project(PROJECT_PATH)
else:
    prj = d.active_project
if not prj:
    raise RuntimeError("No project; open one or set PROJECT_PATH")

hfss = Hfss(project=prj if DESIGN_NAME is None else None,
            projectname=prj.name if DESIGN_NAME else None,
            designname=DESIGN_NAME,
            specified_version=AEDT_VERSION, new_desktop=False, close_on_exit=False)

# ───────── helpers ────────── #
def variables():                        # dict name ➜ value
    vm = hfss.variable_manager
    for attr in ("variables", "properties"):
        if hasattr(vm, attr):
            return getattr(vm, attr)
    out = {}
    for n in hfss.odesign.GetVariables():
        out[n] = hfss.odesign.GetVariableValue(n)
    return out

def materials():
    return {m: {"name": m} for m in hfss.materials.material_keys}

def objects():
    mdl = hfss.modeler
    out = {}
    for o in mdl.objects:
        names = [o.name] if hasattr(o, "name") else mdl.get_object_name(o)
        if isinstance(names, str):
            names = [names]
        for n in names:
            hist = mdl.get_object_history(n)
            face_ids = mdl.get_object_faces(n)
            try:
                prim = mdl.get_object_type(n)
                params = mdl.get_object_parameters(n)
            except Exception:
                prim, params = "Unknown", {}
            try:
                bbox = mdl.get_bounding_box(n)
            except Exception:
                bbox = []
            out[n] = {
                "material": mdl.get_object_material(n, "") if mdl.does_object_exist(n) else "Unknown",
                "color": getattr(o, "color", None),
                "primitive": prim, "params": params,
                "faces": face_ids, "bounding_box": bbox,
                "history": hist
            }
    return out

def boundary_and_ports():
    bmod = hfss.boundaries
    bounds, ports = {}, {}
    for b in bmod:
        entry = {"type": b.type, "props": b.props}
        try:
            entry["faces"] = bmod.get_boundary_faces(b.name)
        except Exception:
            entry["faces"] = []
        (ports if "port" in b.type.lower() else bounds)[b.name] = entry
    return bounds, ports

def setups():
    out = {}
    for s in hfss.setups:
        out[s.name] = {
            "props": s.props,
            "sweeps": {sw.name: sw.props for sw in s.sweeps}
        }
    return out

def coord_systems():
    csman = hfss.modeler.CoordinateSystemManager
    names = csman.ListCoordinateSystems()
    return {n: csman.GetCoordinateSystem(n) for n in names}

def mesh_ops():
    mm = hfss.mesh
    return {m: mm.meshoperations[m].props for m in mm.meshoperations}

def reports():
    rpt = {}
    for rep in hfss.post.reports:
        rpt[rep.name] = rep.report_type
    return rpt

# ───────── collect everything ───────── #
data = {
    "meta": {"timestamp": ts, "project": hfss.project_name,
             "design": hfss.design_name, "aedt_version": d.release},
    "variables": variables(),
    "materials": materials(),
    "objects":   objects(),
    "analysis_setups": setups(),
    "coord_systems": coord_systems(),
    "mesh_ops": mesh_ops(),
    "reports": reports(),
    "history": hfss.odesign.GetModelHistory()
}
data["boundaries"], data["excitations"] = boundary_and_ports()

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
print("✅  Extraction finished.")