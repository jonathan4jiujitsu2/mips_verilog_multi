# hfss_extractor_active.py  –  attach to current AEDT design
# --------------------------------------------------------------------
import os, json, csv
from datetime import datetime
from pyaedt import Desktop, Hfss

# nothing to configure except optional CSV flag
EXPORT_CSV = True

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
d  = Desktop(new_desktop=False)               # attach to running AEDT

# one-liner that grabs *active* project & design:
hfss = Hfss()                                 # no args → current design
if hfss is False:                             # PyAEDT returns bool on failure
    raise RuntimeError("No active HFSS design – select one and re-run.")

print("✓ Project:", hfss.project_name)
print("✓ Design :", hfss.design_name)

mdl = hfss.modeler

# ───── collectors ───── #
vars_dict = getattr(hfss.variable_manager, "variables",
            getattr(hfss.variable_manager, "properties", {}))
mat_list  = list(hfss.materials.material_keys)

def objects():
    out = {}
    for h in mdl.objects:
        n = h.name
        try:
            bbox = mdl.get_bounding_box(n)
        except Exception:
            bbox = []
        if not bbox and mdl.get_object_material(n, "") in ("", "Unknown"):
            continue
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

def bounds_ports():
    bnd, prt = {}, {}
    for bd in hfss.boundaries:
        e = {"type": bd.type, "props": bd.props}
        try:
            e["faces"] = hfss.boundaries.get_boundary_faces(bd.name)
        except Exception:
            e["faces"] = []
        (prt if "port" in bd.type.lower() else bnd)[bd.name] = e
    return bnd, prt

setups = {s.name: {"props": s.props,
                   "sweeps": {sw.name: sw.props for sw in s.sweeps}}
          for s in hfss.setups}

csm  = mdl.CoordinateSystemManager
mesh = hfss.mesh

data = {
    "meta": {"timestamp": ts,
             "project": hfss.project_name,
             "design":  hfss.design_name,
             "aedt_version": d.release},
    "variables"      : vars_dict,
    "materials"      : mat_list,
    "objects"        : objects(),
    "analysis_setups": setups,
    "coord_systems"  : {n: csm.GetCoordinateSystem(n)
                        for n in csm.ListCoordinateSystems()},
    "mesh_ops"       : {m: mesh.meshoperations[m].props
                        for m in mesh.meshoperations},
    "history"        : hfss.odesign.GetModelHistory()
}
data["boundaries"], data["excitations"] = bounds_ports()

# save
base = f"HFSS_Extract_{hfss.project_name}_{hfss.design_name}_{ts}"
with open(base + ".json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
print("JSON →", base + ".json")

if EXPORT_CSV:
    with open(base + "_variables.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["Variable", "Value"], *vars_dict.items()])
    print("CSV  →", base + "_variables.csv")

hfss.release_desktop(close_projects=False, close_desktop=False)
print("✅  Extraction complete.")