# -*- coding: utf-8 -*-
r"""
hfss_rebuild_from_dump.py
-------------------------
Recreate an HFSS 3-D design (geometry, variables, materials, ports/boundaries,
analysis setups) from the JSON produced by hfss_extractor_pyaedt.py.

Dependencies
------------
    python -m pip install --user pyaedt

Usage
-----
    python hfss_rebuild_from_dump.py -d HFSS_Extract_<...>.json
    python hfss_rebuild_from_dump.py -d dump.json -o C:\Temp\Rebuilt.aedt -v 2024.2
"""

import os, json, argparse
from pyaedt import Desktop, Hfss


# ───────────────────────── CLI parsing ───────────────────────── #
cli = argparse.ArgumentParser(description="Rebuild HFSS model from JSON dump")
cli.add_argument("-d", "--dump", required=True, help="path to JSON dump file")
cli.add_argument("-o", "--output",
                 help="new .aedt project to create (else add design to open project)")
cli.add_argument("-v", "--version", help="AEDT version, e.g. 2024.2")
args = cli.parse_args()

dump_path   = os.path.abspath(args.dump)
new_project = os.path.abspath(args.output) if args.output else None
aedt_ver    = args.version or None

if not os.path.isfile(dump_path):
    raise FileNotFoundError(dump_path)

# ───────────────────── attach / open AEDT ───────────────────── #
dsk = Desktop(specified_version=aedt_ver, new_desktop=False)

if new_project:
    # brand-new project file
    hfss = Hfss(projectname=new_project,
                designname="Rebuilt_Model",
                solution_type="DrivenModal",
                specified_version=aedt_ver,
                new_desktop=False,
                close_on_exit=False)
else:
    # add design inside active project
    cur_prj = dsk.active_project()                       # call the method!
    if cur_prj is None:
        raise RuntimeError("No project open and no -o/--output given")
    hfss = Hfss(project=cur_prj,
                designname="Rebuilt_Model",
                solution_type="DrivenModal",
                specified_version=aedt_ver,
                new_desktop=False,
                close_on_exit=False)

print("→ Rebuilding into", hfss.project_name, "/", hfss.design_name)

# ───────────────────── load dump file ───────────────────────── #
with open(dump_path, "r", encoding="utf-8") as f:
    dump = json.load(f)

# ───────────────────── 1. variables ─────────────────────────── #
for k, v in dump["variables"].items():
    hfss[k] = v

# ───────────────────── 2. materials ─────────────────────────── #
for m in dump["materials"]:
    if m not in hfss.materials.material_keys:
        hfss.materials.add_material(m)

mdl = hfss.modeler

def as_float(val):
    try:
        return float(str(val).rstrip("mm"))
    except Exception:
        return 0.0

# ───────────────────── 3. geometry ──────────────────────────── #
for name, obj in dump["objects"].items():
    prim = obj.get("primitive", "box").lower()
    p    = obj.get("params", {})
    mat  = obj["material"]

    # create primitive by type
    if prim == "box":
        pos  = [p.get(k, "0mm") for k in ("XPosition", "YPosition", "ZPosition")]
        size = [p.get("XSize", "1mm"), p.get("YSize", "1mm"), p.get("ZSize", "1mm")]
        o = mdl.create_box(pos, size, name=name)
    elif prim == "cylinder":
        axis   = p.get("Axis", "Z")
        center = [p.get(k, "0mm") for k in ("XCenter", "YCenter", "ZCenter")]
        radius = p.get("Radius", "1mm")
        height = p.get("Height", "1mm")
        o = mdl.create_cylinder(cs_axis=axis, position=center,
                                radius=radius, height=height, name=name)
    elif prim == "sphere":
        center = [p.get(k, "0mm") for k in ("XCenter", "YCenter", "ZCenter")]
        radius = p.get("Radius", "1mm")
        o = mdl.create_sphere(position=center, radius=radius, name=name)
    else:
        # fallback: bounding-box block
        bb = obj["bounding_box"]
        size = [as_float(bb["x_max"]) - as_float(bb["x_min"]),
                as_float(bb["y_max"]) - as_float(bb["y_min"]),
                as_float(bb["z_max"]) - as_float(bb["z_min"])]
        pos  = [bb["x_min"], bb["y_min"], bb["z_min"]]
        o = mdl.create_box(pos, size, name=name)

    o.material_name = mat
    if obj.get("color") is not None:
        o.color = tuple(obj["color"])

# ───────────────────── 4. ports & boundaries ────────────────── #
bmod = hfss.boundaries
for b in dump["boundaries"].values():
    faces = b.get("faces", [])
    if not faces:
        continue
    t = b["type"].lower()
    if "radiat" in t:
        bmod.create_radiation_boundary(faces, name=b["name"])
    elif "perfecte" in t or "pec" in t:
        bmod.create_perfect_e_boundary(faces, name=b["name"])
    # extend with other boundary types as needed

for p in dump["excitations"].values():
    faces = p.get("faces", [])
    if not faces:
        continue
    t = p["type"].lower()
    if "wave" in t:
        num = int(p["props"].get("PortNum", 1))
        bmod.create_wave_port(faces, port_number=num, name=p["name"])
    elif "lumped" in t:
        bmod.create_lumped_port(faces, name=p["name"])

# ───────────────────── 5. analysis setups ───────────────────── #
for s_name, s in dump["analysis_setups"].items():
    stp = hfss.analysis_setup.create_setup(s_name, s["props"])
    for sw_name, sw in s["sweeps"].items():
        stp.add_sweep(sw_name, sw)

hfss.save_project()
print("✅  Finished – project saved at:", hfss.project_path)