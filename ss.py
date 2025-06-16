# hfss_extractor_full.py  —  rock-solid version
# -------------------------------------------------------------
import os, json, csv
from datetime import datetime
from pyaedt import Desktop, Hfss

# ────────── USER OPTIONS ──────────
PROJECT_PATH = None        # r"C:\path\file.aedt" or None
DESIGN_NAME  = None        # "Design1"          or None
AEDT_VERSION = None        # "2024.2"           or None
EXPORT_CSV   = True
# ──────────────────────────────────

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
desktop = Desktop(specified_version=AEDT_VERSION, new_desktop=False)

# ───────── project ─────────
if PROJECT_PATH and os.path.isfile(PROJECT_PATH):
    prj = desktop.open_project(PROJECT_PATH)
else:
    prj = desktop.active_project()
if prj is None:
    raise RuntimeError("No project open — open one in AEDT or set PROJECT_PATH")

# ───────── design resolver ─────────
def resolve_design_name(project, requested=None):
    if requested:                                   # 1
        return requested
    # 2-3 active_design
    ad = getattr(project, "active_design", None)
    if ad:
        return ad if isinstance(ad, str) else ad.GetName()
    # 4 design_names property
    names = getattr(project, "design_names", None)
    if names:
        return names[0]
    # 5 helper get_design_names()
    if hasattr(project, "get_design_names"):
        names = project.get_design_names()
        if names:
            return names[0]
    # 6 COM fallback
    try:
        names = project.GetDesignNames()
        if names:
            return names[0]
    except Exception:
        pass
    raise RuntimeError("Cannot determine a design name; set DESIGN_NAME")

design_name = resolve_design_name(prj, DESIGN_NAME)
if getattr(prj, "active_design", None) != design_name:
    if hasattr(prj, "set_active_design"):
        prj.set_active_design(design_name)
    else:  # COM
        prj.SetActiveDesign(design_name)

# ───────── attach HFSS ─────────
hfss = Hfss(project=prj, designname=design_name,
            specified_version=AEDT_VERSION,
            new_desktop=False, close_on_exit=False)

print("✓ Project:", hfss.project_name)
print("✓ Design :", hfss.design_name)

mdl = hfss.modeler

# ───────── collectors ─────────
def vars_dict():
    vm = hfss.variable_manager
    return getattr(vm, "variables",
           getattr(vm, "properties", {}))

def materials_list():
    return list(hfss.materials.material_keys)

def objects_dict():
    out = {}
    for h in mdl.objects:
        names = [h.name] if hasattr(h, "name") else mdl.get_object_name(h)
        names = names if isinstance(names, list) else [names]
        for n in names:
            if not mdl.does_object_exist(n) or mdl.is_group(n):
                continue
            try:
                bbox = mdl.get_bounding_box(n)
            except Exception:
                bbox = []
            if (not bbox and
                mdl.get_object_material(n, "") in ("", "Unknown")):
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

def setups_dict():
    return {s.name: {"props": s.props,
                     "sweeps": {sw.name: sw.props for sw in s.sweeps}}
            for s in hfss.setups}

csm  = mdl.CoordinateSystemManager
mesh = hfss.mesh

# ───────── data package ─────────
data = {
    "meta": {"timestamp": ts,
             "project": hfss.project_name,
             "design":  hfss.design_name,
             "aedt_version": desktop.release},
    "variables"      : vars_dict(),
    "materials"      : materials_list(),
    "objects"        : objects_dict(),
    "analysis_setups": setups_dict(),
    "coord_systems"  : {n: csm.GetCoordinateSystem(n)
                        for n in csm.ListCoordinateSystems()},
    "mesh_ops"       : {m: mesh.meshoperations[m].props
                        for m in mesh.meshoperations},
    "history"        : hfss.odesign.GetModelHistory()
}
data["boundaries"], data["excitations"] = bounds_ports()

# ───────── save ─────────
base = f"HFSS_Extract_{hfss.project_name}_{hfss.design_name}_{ts}"
with open(base + ".json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
print("JSON  →", base + ".json")

if EXPORT_CSV:
    with open(base + "_variables.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["Variable", "Value"],
                                 *data["variables"].items()])
    print("CSV   →", base + "_variables.csv")

hfss.release_desktop(close_projects=False, close_desktop=False)
print("✅  Extraction complete.")