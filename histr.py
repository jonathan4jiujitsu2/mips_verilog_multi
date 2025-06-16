# -*- coding: utf-8 -*-
"""
HFSS REBUILDER – EXECUTES FULL HISTORY
Recreates geometry by executing each object's history script (or entire
design history) for a perfect clone.  Then reapplies ports, boundaries,
mesh operations, coordinate systems, variables, materials and setups.

Examples
--------
  python hfss_rebuild_history.py -d dump.json
  python hfss_rebuild_history.py -d dump.json -o "%USERPROFILE%\\Rebuilt.aedt"
"""
import os, json, argparse
from pyaedt import Desktop, Hfss

# ────────── CLI ────────── #
cli = argparse.ArgumentParser()
cli.add_argument("-d", "--dump", required=True, help="extractor JSON")
cli.add_argument("-o", "--output", help="new *.aedt project")
cli.add_argument("-v", "--version", help="AEDT version, e.g. 2024.2")
args = cli.parse_args()
dump_path = os.path.abspath(args.dump)
if not os.path.isfile(dump_path):
    raise FileNotFoundError(dump_path)

dsk = Desktop(specified_version=args.version, new_desktop=False)

# ────────── project / design ────────── #
if args.output:
    hfss = Hfss(projectname=os.path.abspath(args.output),
                designname="Rebuilt_Model", solution_type="DrivenModal",
                new_desktop=False, close_on_exit=False)
else:
    prj = dsk.active_project()
    if prj is None:
        raise RuntimeError("Open a project or use -o")
    hfss = Hfss(project=prj, designname="Rebuilt_Model",
                solution_type="DrivenModal", new_desktop=False,
                close_on_exit=False)

print("→ Rebuilding into", hfss.project_name, "/", hfss.design_name)

with open(dump_path, "r", encoding="utf-8") as f:
    dump = json.load(f)

# ───── 1: execute full project history first (fast) ───── #
if dump.get("history"):
    hfss.odesign.ExecuteScript(dump["history"])
else:
    # or per-object history (slower but safer when IDs changed)
    for obj in dump["objects"].values():
        if obj["history"]:
            hfss.odesign.ExecuteScript(obj["history"])

mdl = hfss.modeler

# ───── 2: variables & materials ───── #
for k, v in dump["variables"].items():
    hfss[k] = v
for m in dump["materials"]:
    if m not in hfss.materials.material_keys:
        hfss.materials.add_material(m)

# ───── 3: re-apply materials / colours (after ExecuteScript) ───── #
for name, obj in dump["objects"].items():
    if not mdl.does_object_exist(name):
        continue
    s = mdl.get_object_from_name(name)
    s.material_name = obj["material"]
    if obj.get("color"): s.color = tuple(obj["color"])

# ───── 4: coordinate systems ───── #
csm = mdl.CoordinateSystemManager
for cs_name, props in dump["coord_systems"].items():
    if cs_name not in csm.ListCoordinateSystems():
        csm.CreateCoordinateSystem(props)

# ───── 5: mesh operations ───── #
mesh = hfss.mesh
for mop_name, mop_props in dump["mesh_ops"].items():
    if mop_name not in mesh.meshoperations:
        mesh.meshoperations.create_meshoperation_from_settings(mop_name, mop_props)

# ───── 6: ports & boundaries ───── #
bmod = hfss.boundaries
for b in dump["boundaries"].values():
    if b["name"] in bmod:
        continue
    if "port" in b["type"].lower():
        continue   # handled later
    bmod.add_boundary(b["type"], b["faces"], b["props"])

for p in dump["excitations"].values():
    if p["name"] in bmod:
        continue
    t = p["type"].lower()
    faces = p["faces"]
    if "wave" in t:
        bmod.create_wave_port(faces, name=p["name"],
                              port_number=int(p["props"].get("PortNum", 1)))
    elif "lumped" in t:
        bmod.create_lumped_port(faces, name=p["name"])

# ───── 7: analysis setups ───── #
existing_setups = {s.name: s for s in hfss.setups}
for s_name, s in dump["analysis_setups"].items():
    stp = existing_setups.get(s_name) or hfss.create_setup(s_name, s["props"])
    if hasattr(stp, "add_sweep"):
        for sw_name, sw in s["sweeps"].items():
            stp.add_sweep(sw_name, sw)

hfss.save_project()
print("✅  Rebuild finished – project:", hfss.project_path)