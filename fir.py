# -*- coding: utf-8 -*-
"""
HFSS EXTRACTOR  (attach-to-active design)
Step-by-step:
  1. Open your project in AEDT.
  2. Click once on the design you want (so it is active).
  3. Run   python hfss_extractor_active.py
Outputs:
  • HFSS_Extract_<project>_<design>_<timestamp>.json
  • …_variables.csv  (can be disabled below)
"""

import os, json, csv
from datetime import datetime
from pyaedt import Desktop, Hfss

EXPORT_CSV = True                   # ← set False if CSV not needed
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

desktop = Desktop(new_desktop=False)        # attach to running AEDT
hfss    = Hfss()                            # active project / design

if hfss is False:                           # PyAEDT returns bool on failure
    raise RuntimeError("No active HFSS design – select one in AEDT and re-run.")

print("✓ Project:", hfss.project_name)
print("✓ Design :", hfss.design_name)

mdl = hfss.modeler

# ───── helpers ───── #
variables = getattr(hfss.variable_manager, "variables",
            getattr(hfss.variable_manager, "properties", {}))
materials = list(hfss.materials.material_keys)

def collect_objects():
    out = {}
    for h in mdl.objects:
        # robust name resolution
        if isinstance(h, str):
            name_list = [h]
        elif hasattr(h, "name"):
            name_list = [h.name]
        else:                                   # numeric handle
            try:
                name_list = [mdl.get_object_name(h)]
            except Exception:
                continue

        for n in name_list:
            if not mdl.does_object_exist(n) or mdl.is_group(n):
                continue
            try:
                bbox = mdl.get_bounding_box(n)
            except Exception:
                bbox = []
            if (not bbox and
                mdl.get_object_material(n, "") in ("", "Unknown")):
                continue                        # skip ghost numeric IDs
            out[n] = {
                "material"    : mdl.get_object_material(n, "") or "Unknown",
                "color"       : getattr(h, "color", None)
                                 if hasattr(h, "color") else None,
                "primitive"   : mdl.get_object_type(n) or "Unknown",
                "params"      : mdl.get_object_parameters(n) or {},
                "faces"       : mdl.get_object_faces(n) or [],
                "bounding_box": bbox,
                "history"     : mdl.get_object_history(n)
            }
    return out

def collect_bounds_ports():
    bnd, prt = {}, {}
    for bd in hfss.boundaries:
        entry = {"type": bd.type, "props": bd.props}
        try:
            entry["faces"] = hfss.boundaries.get_boundary_faces(bd.name)
        except Exception:
            entry["faces"] = []
        (prt if "port" in bd.type.lower() else bnd)[bd.name] = entry
    return bnd, prt

setups = {s.name: {"props": s.props,
                   "sweeps": {sw.name: sw.props for sw in s.sweeps}}
          for s in hfss.setups}

# coordinate-system manager (old + new API names)
csm = getattr(mdl, "coordinate_system_manager",
      getattr(mdl, "CoordinateSystemManager", None))
coord_systems = {}
if csm:
    list_cs = (csm.list_coordinate_systems if hasattr(csm, "list_coordinate_systems")
               else csm.ListCoordinateSystems)
    get_cs  = (csm.get_coordinate_system    if hasattr(csm, "get_coordinate_system")
               else csm.GetCoordinateSystem)
    for cs_name in list_cs():
        try:
            coord_systems[cs_name] = get_cs(cs_name)
        except Exception:
            coord_systems[cs_name] = {}

mesh_ops = {m: hfss.mesh.meshoperations[m].props
            for m in hfss.mesh.meshoperations}

# AEDT version property differs by build
aedt_ver = (getattr(desktop, "release", None) or
            getattr(desktop, "odesktop_version", "unknown"))

# ───── build JSON payload ───── #
data = {
    "meta": {"timestamp": ts,
             "project": hfss.project_name,
             "design":  hfss.design_name,
             "aedt_version": aedt_ver},
    "variables"      : variables,
    "materials"      : materials,
    "objects"        : collect_objects(),
    "analysis_setups": setups,
    "coord_systems"  : coord_systems,
    "mesh_ops"       : mesh_ops,
    "history"        : hfss.odesign.GetModelHistory()
}
data["boundaries"], data["excitations"] = collect_bounds_ports()

# ───── save files ───── #
base = f"HFSS_Extract_{hfss.project_name}_{hfss.design_name}_{ts}"
with open(base + ".json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
print("JSON →", base + ".json")

if EXPORT_CSV:
    with open(base + "_variables.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["Variable", "Value"], *variables.items()])
    print("CSV  →", base + "_variables.csv")

hfss.release_desktop(close_projects=False, close_desktop=False)
print("✅  Extraction complete.")