# -*- coding: utf-8 -*-
"""
HFSS Rebuilder – Executes full model history to recreate an exact clone.
Supports:
  • variables, materials
  • geometry via ExecuteScript(history)
  • ports, boundaries, coordinate systems, mesh ops
  • analysis setups & sweeps
"""

import os, json, argparse
from pyaedt import Desktop, Hfss

# ───────── CLI ───────── #
cli = argparse.ArgumentParser()
cli.add_argument("-d", "--dump", required=True, help="extractor JSON path")
cli.add_argument("-o", "--output", help="new *.aedt file to create")
cli.add_argument("-v", "--version", help="AEDT version, e.g. 2024.2")
args = cli.parse_args()

dump_path = os.path.abspath(args.dump)
if not os.path.isfile(dump_path):
    raise FileNotFoundError(dump_path)

dsk = Desktop(specified_version=args.version, new_desktop=False)

# project / design --------------------------------------------------------
if args.output:
    hfss = Hfss(projectname=os.path.abspath(args.output),
                designname="Rebuilt_Model",
                solution_type="DrivenModal",
                specified_version=args.version,
                new_desktop=False, close_on_exit=False)
else:
    prj = dsk.active_project()
    if prj is None:
        raise RuntimeError("Open a project or supply -o")
    hfss = Hfss(project=prj,
                designname="Rebuilt_Model",
                solution_type="DrivenModal",
                specified_version=args.version,
                new_desktop=False, close_on_exit=False)

print("→ Rebuilding into", hfss.project_name, "/", hfss.design_name)

with open(dump_path, "r", encoding="utf-8") as f:
    dump = json.load(f)

# 1 ▪ execute history (full design or per object) -------------------------
if dump.get("history"):
    hfss.odesign.ExecuteScript(dump["history"])
else:
    for o in dump["objects"].values():
        if o["history"]:
            hfss.odesign.ExecuteScript(o["history"])

mdl = hfss.modeler

# 2 ▪ variables & materials ----------------------------------------------
for k, v in dump["variables"].items():
    hfss[k] = v
for m in dump["materials"]:
    if m not in hfss.materials.material_keys:
        hfss.materials.add_material(m)

# re-apply material & colour (ExecuteScript already created solids) -------
for n, o in dump["objects"].items():
    if not mdl.does_object_exist(n):
        continue
    s = mdl.get_object_from_name(n)
    s.material_name = o["material"]
    if o.get("color"):
        s.color = tuple(o["color"])

# 3 ▪ coordinate systems --------------------------------------------------
csm = mdl.CoordinateSystemManager
for n, props in dump["coord_systems"].items():
    if n not in csm.ListCoordinateSystems():
        csm.CreateCoordinateSystem(props)

# 4 ▪ mesh operations -----------------------------------------------------
mm = hfss.mesh
for mop_name, mop_props in dump["mesh_ops"].items():
    if mop_name not in mm.meshoperations:
        mm.meshoperations.create_meshoperation_from_settings(mop_name, mop_props)

# 5 ▪ boundaries & ports --------------------------------------------------
bmod = hfss.boundaries
for b in dump["boundaries"].values():
    if b["name"] in bmod:
        continue
    bmod.add_boundary(b["type"], b["faces"], b["props"])

for p in dump["excitations"].values():
    if p["name"] in bmod:
        continue
    t = p["type"].lower()
    faces = p["faces"]
    if "wave" in t:
        bmod.create_wave_port(faces, port_number=int(p["props"].get("PortNum", 1)),
                              name=p["name"])
    elif "lumped" in t:
        bmod.create_lumped_port(faces, name=p["name"])

# 6 ▪ analysis setups -----------------------------------------------------
present = {s.name: s for s in hfss.setups}
for s_name, s in dump["analysis_setups"].items():
    stp = present.get(s_name) or hfss.create_setup(s_name, s["props"])
    if hasattr(stp, "add_sweep"):
        for sw_name, sw in s["sweeps"].items():
            stp.add_sweep(sw_name, sw)

hfss.save_project()
print("✅  Rebuild finished – saved at:", hfss.project_path)