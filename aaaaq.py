# -*- coding: utf-8 -*-
"""
HFSS EXTRACTOR (attach to active design, gRPC-safe)
 • Open project in AEDT, select the design you want.
 • Run:  python hfss_extractor_active.py
Outputs:
    JSON   HFSS_Extract_<project>_<design>_<timestamp>.json
    CSV    HFSS_Extract_<project>_<design>_<timestamp>_variables.csv
"""

import os, json, csv
from datetime import datetime
from pyaedt import Desktop, Hfss

EXPORT_CSV = True
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

desk = Desktop(new_desktop=False)   # attach to running Electronics Desktop
hfss = Hfss()                       # grab active project & design
if hfss is False:
    raise RuntimeError("No active HFSS design – highlight one in AEDT and re-run.")

print("✓ Project:", hfss.project_name)
print("✓ Design :", hfss.design_name)

mdl = hfss.modeler

# ───── helpers ───── #
variables = getattr(hfss.variable_manager, "variables",
            getattr(hfss.variable_manager, "properties", {}))
materials = list(hfss.materials.material_keys)

def objects_dict():
    out = {}
    for h in mdl.objects:
        name = h if isinstance(h, str) else getattr(h, "name", None)
        if not name:                             # numeric handle → look up
            try: name = mdl.get_object_name(h)
            except Exception: continue
        if not mdl.does_object_exist(name) or mdl.is_group(name):
            continue
        try: bbox = mdl.get_bounding_box(name)
        except Exception: bbox = []
        if (not bbox and mdl.get_object_material(name, "") in ("", "Unknown")):
            continue
        out[name] = {
            "material"    : mdl.get_object_material(name, "") or "Unknown",
            "color"       : getattr(h, "color", None) if hasattr(h, "color") else None,
            "primitive"   : mdl.get_object_type(name) or "Unknown",
            "params"      : mdl.get_object_parameters(name) or {},
            "faces"       : mdl.get_object_faces(name) or [],
            "bounding_box": bbox,
            "history"     : mdl.get_object_history(name)
        }
    return out

def bounds_ports():
    bnd, prt = {}, {}
    for bd in hfss.boundaries:
        entry = {"type": bd.type, "props": bd.props}
        try: entry["faces"] = hfss.boundaries.get_boundary_faces(bd.name)
        except Exception: entry["faces"] = []
        (prt if "port" in bd.type.lower() else bnd)[bd.name] = entry
    return bnd, prt

setups = {s.name: {"props": s.props,
                   "sweeps": {sw.name: sw.props for sw in s.sweeps}}
          for s in hfss.setups}

# coordinate systems (old + new API)
csm = getattr(mdl, "coordinate_system_manager",
      getattr(mdl, "CoordinateSystemManager", None))
coord_systems = {}
if csm:
    list_cs = csm.list_coordinate_systems if hasattr(csm, "list_coordinate_systems") else csm.ListCoordinateSystems
    get_cs  = csm.get_coordinate_system    if hasattr(csm, "get_coordinate_system")    else csm.GetCoordinateSystem
    for cs in list_cs():
        try: coord_systems[cs] = get_cs(cs)
        except Exception: coord_systems[cs] = {}

mesh_ops = {m: hfss.mesh.meshoperations[m].props for m in hfss.mesh.meshoperations}

# ───── SAFE history grab ───── #
try:
    design_history = hfss.odesign.GetModelHistory()
except Exception:                       # blocked gRPC → build history manually
    print("⚠  GetModelHistory blocked; stitching history from objects.")
    design_history = "\n".join(obj["history"] for obj in objects_dict().values() if obj["history"])

aedt_ver = getattr(desk, "release", getattr(desk, "odesktop_version", "unknown"))

data = {
    "meta": {"timestamp": ts,
             "project": hfss.project_name,
             "design":  hfss.design_name,
             "aedt_version": aedt_ver},
    "variables"      : variables,
    "materials"      : materials,
    "objects"        : objects_dict(),
    "analysis_setups": setups,
    "coord_systems"  : coord_systems,
    "mesh_ops"       : mesh_ops,
    "history"        : design_history
}
data["boundaries"], data["excitations"] = bounds_ports()

# ───── save ───── #
base = f"HFSS_Extract_{hfss.project_name}_{hfss.design_name}_{ts}"
with open(base + ".json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
print("JSON →", base + ".json")

if EXPORT_CSV:
    with open(base + "_variables.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["Variable", "Value"], *variables.items()])
    print("CSV  →", base + "_variables.csv")

hfss.release_desktop(close_projects=False, close_desktop=False)
print("✅  Extraction complete — ready for rebuild.")