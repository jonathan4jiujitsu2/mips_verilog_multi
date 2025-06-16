# -*- coding: utf-8 -*-
"""
SECOND-PASS EXTRACTOR  (run from dump_and_spawn.py)
• Attaches to the SAME AEDT session (new_desktop=False)
• Pulls everything except model history
• Inserts the history file content handed in via --hist
• Writes JSON + variables CSV
"""
import os, json, csv, argparse, datetime
from pyaedt import Desktop, Hfss

# ---------------- CLI ----------------
cli = argparse.ArgumentParser()
cli.add_argument("-hist", "--history", required=True,
                 help="Path to history file written by dump_and_spawn.py")
args = cli.parse_args()

hist_path = os.path.abspath(args.history)
if not os.path.isfile(hist_path):
    raise FileNotFoundError(hist_path)

# ---------------- attach to AEDT ----------------
desk = Desktop(new_desktop=False)   # same session
hfss = Hfss()                       # active design
if hfss is False:
    raise RuntimeError("No active HFSS design; script must be launched "
                       "from dump_and_spawn.py")

print("✓ Project:", hfss.project_name)
print("✓ Design :", hfss.design_name)

mdl = hfss.modeler
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# ---------- collectors ----------
variables = getattr(hfss.variable_manager, "variables",
            getattr(hfss.variable_manager, "properties", {}))
materials = list(hfss.materials.material_keys)

def objects_dict():
    out = {}
    for h in mdl.objects:
        n = h if isinstance(h, str) else getattr(h, "name", None)
        if not n:
            try: n = mdl.get_object_name(h)
            except Exception: continue
        if mdl.is_group(n): continue
        try: bbox = mdl.get_bounding_box(n)
        except Exception: bbox = []
        if not bbox and mdl.get_object_material(n, "") in ("", "Unknown"):
            continue
        out[n] = {
            "material"    : mdl.get_object_material(n, "") or "Unknown",
            "color"       : getattr(h, "color", None) if hasattr(h, "color") else None,
            "primitive"   : mdl.get_object_type(n) or "Unknown",
            "params"      : mdl.get_object_parameters(n) or {},
            "faces"       : mdl.get_object_faces(n) or [],
            "bounding_box": bbox
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

with open(hist_path, "r") as f:
    hist_text = f.read()

aedt_ver = getattr(desk, "release", getattr(desk, "odesktop_version", "unknown"))

data = {
    "meta": {"timestamp": timestamp,
             "project": hfss.project_name,
             "design":  hfss.design_name,
             "aedt_version": aedt_ver},
    "variables"      : variables,
    "materials"      : materials,
    "objects"        : objects_dict(),
    "analysis_setups": setups,
    "coord_systems"  : coord_systems,
    "mesh_ops"       : mesh_ops,
    "history"        : hist_text
}
data["boundaries"], data["excitations"] = bounds_ports()

# -------------- save --------------
base = f"HFSS_Extract_{hfss.project_name}_{hfss.design_name}_{timestamp}"
out_dir = os.path.dirname(hist_path)
json_path = os.path.join(out_dir, base + ".json")

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("✓ JSON written:", json_path)

if variables and EXPORT_CSV:
    csv_path = os.path.join(out_dir, base + "_variables.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["Variable", "Value"], *variables.items()])
    print("✓ CSV  written:", csv_path)

hfss.release_desktop(close_projects=False, close_desktop=False)
print("✅  Pass-2 extraction complete.")