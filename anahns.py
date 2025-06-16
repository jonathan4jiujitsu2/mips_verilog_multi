# -*- coding: utf-8 -*-

“””
HFSS EXTRACTOR — full model history + ports, boundaries, mesh ops, setups…
Outputs
• HFSS_Extract_<project>*<design>*<timestamp>.json
• HFSS_Extract_<project>*<design>*<timestamp>_variables.csv
“””

import os, json, csv
from datetime import datetime
from pyaedt import Desktop, Hfss

# ───────── USER OPTIONS ─────────

PROJECT_PATH = None        # r”C:\file.aedt”  or None to attach to open project
DESIGN_NAME  = None        # “MyDesign”       or None = active design
AEDT_VERSION = None        # “2024.2”         or None
EXPORT_CSV   = True

# ────────────────────────────────

ts = datetime.now().strftime(”%Y%m%d_%H%M%S”)

try:
desktop = Desktop(specified_version=AEDT_VERSION, new_desktop=False)
print(“✓ Connected to Desktop”)
except Exception as e:
print(f”❌ Error connecting to Desktop: {e}”)
raise

# 1 ▪ project ———————————————————––

try:
if PROJECT_PATH and os.path.isfile(PROJECT_PATH):
project_hdl = desktop.open_project(PROJECT_PATH)
print(f”✓ Opened project from: {PROJECT_PATH}”)
else:
project_hdl = desktop.active_project()
if project_hdl is None:
raise RuntimeError(“No project open — open one in AEDT or set PROJECT_PATH”)
print(f”✓ Using active project: {project_hdl.name}”)
except Exception as e:
print(f”❌ Error getting project: {e}”)
raise

# 2 ▪ design (robust with better error handling) ———————––

try:
if DESIGN_NAME:
design_name = DESIGN_NAME
print(f”✓ Using specified design: {design_name}”)
else:
print(“🔍 Auto-detecting design…”)

```
    # Try multiple methods to get design names
    names = None
    try:
        if hasattr(project_hdl, "design_names"):
            names = project_hdl.design_names
            print("  → Got designs via .design_names")
        elif hasattr(project_hdl, "get_design_names"):
            names = project_hdl.get_design_names()
            print("  → Got designs via .get_design_names()")
        else:
            names = list(project_hdl.GetDesignNames())
            print("  → Got designs via COM .GetDesignNames()")
    except Exception as e:
        print(f"  ⚠️ Error getting design names: {e}")
        
    if not names:
        raise RuntimeError("Project has no designs; set DESIGN_NAME explicitly")
    
    print(f"  → Available designs: {names}")
    design_name = names[0]
    print(f"  → Selected first design: {design_name}")
    
# Force set active design using multiple approaches
print("🔧 Setting active design...")
try:
    if hasattr(project_hdl, "set_active_design"):
        project_hdl.set_active_design(design_name)
        print("  → Set via .set_active_design()")
    else:
        project_hdl.SetActiveDesign(design_name)
        print("  → Set via COM .SetActiveDesign()")
except Exception as e:
    print(f"  ⚠️ Warning setting active design: {e}")
    # Continue anyway, might still work
    
# Verify active design is set
try:
    if hasattr(project_hdl, "active_design"):
        current = project_hdl.active_design
    else:
        current_obj = project_hdl.GetActiveDesign()
        current = current_obj.GetName() if current_obj else None
    print(f"  → Current active design: {current}")
except Exception as e:
    print(f"  ⚠️ Could not verify active design: {e}")
```

except Exception as e:
print(f”❌ Error handling design selection: {e}”)
raise

# 3 ▪ attach HFSS with better error handling —————————–

try:
print(“🔌 Connecting to HFSS…”)
hfss = Hfss(project=project_hdl,              # pass real Project handle
designname=design_name,
specified_version=AEDT_VERSION,
new_desktop=False, close_on_exit=False)

```
print("✓ Project:", hfss.project_name)
print("✓ Design :", hfss.design_name)
```

except Exception as e:
print(f”❌ Error connecting to HFSS: {e}”)
print(“🔄 Trying alternative connection method…”)
try:
# Alternative: use project name instead of handle
hfss = Hfss(project=project_hdl.name,
designname=design_name,
specified_version=AEDT_VERSION,
new_desktop=False, close_on_exit=False)
print(“✓ Connected via alternative method”)
print(“✓ Project:”, hfss.project_name)
print(“✓ Design :”, hfss.design_name)
except Exception as e2:
print(f”❌ Alternative connection also failed: {e2}”)
raise

mdl = hfss.modeler

# ───────── helper collectors ─────────

def grab_vars():
“”“Extract all design variables”””
try:
vm = hfss.variable_manager
return getattr(vm, “variables”,
getattr(vm, “properties”, {}))
except Exception as e:
print(f”⚠️ Warning getting variables: {e}”)
return {}

def grab_mats():
“”“Extract all materials”””
try:
return list(hfss.materials.material_keys)
except Exception as e:
print(f”⚠️ Warning getting materials: {e}”)
return []

def grab_objects():
“”“Extract all geometric objects with properties”””
out = {}
try:
for h in mdl.objects:
try:
names = [h.name] if hasattr(h, “name”) else mdl.get_object_name(h)
if isinstance(names, str):
names = [names]

```
            for n in names:
                if not mdl.does_object_exist(n) or mdl.is_group(n):
                    continue
                try:
                    bbox = mdl.get_bounding_box(n)
                except Exception:
                    bbox = []
                if (not bbox and
                    mdl.get_object_material(n, "") in ("", "Unknown")):
                    continue            # skip ghost numeric IDs
                
                out[n] = {
                    "material"    : mdl.get_object_material(n, "") or "Unknown",
                    "color"       : getattr(h, "color", None),
                    "primitive"   : mdl.get_object_type(n) or "Unknown",
                    "params"      : mdl.get_object_parameters(n) or {},
                    "faces"       : mdl.get_object_faces(n) or [],
                    "bounding_box": bbox,
                    "history"     : mdl.get_object_history(n)
                }
        except Exception as e:
            print(f"⚠️ Warning processing object {getattr(h, 'name', 'unknown')}: {e}")
            continue
except Exception as e:
    print(f"⚠️ Warning getting objects: {e}")
return out
```

def grab_bounds_ports():
“”“Extract boundaries and excitation ports”””
bnd, prt = {}, {}
try:
for bd in hfss.boundaries:
try:
e = {“type”: bd.type, “props”: bd.props}
try:
e[“faces”] = hfss.boundaries.get_boundary_faces(bd.name)
except Exception:
e[“faces”] = []
(prt if “port” in bd.type.lower() else bnd)[bd.name] = e
except Exception as e:
print(f”⚠️ Warning processing boundary {bd.name}: {e}”)
continue
except Exception as e:
print(f”⚠️ Warning getting boundaries: {e}”)
return bnd, prt

def grab_setups():
“”“Extract analysis setups and sweeps”””
try:
return {s.name: {“props”: s.props,
“sweeps”: {sw.name: sw.props for sw in s.sweeps}}
for s in hfss.setups}
except Exception as e:
print(f”⚠️ Warning getting setups: {e}”)
return {}

# ───────── data extraction ─────────

print(“📊 Extracting data…”)

try:
csm  = mdl.CoordinateSystemManager
mesh = hfss.mesh

```
data = {
    "meta": {"timestamp": ts,
             "project": hfss.project_name,
             "design":  hfss.design_name,
             "aedt_version": desktop.release},
    "variables"      : grab_vars(),
    "materials"      : grab_mats(),
    "objects"        : grab_objects(),
    "analysis_setups": grab_setups(),
    "coord_systems"  : {},
    "mesh_ops"       : {},
    "history"        : []
}

# Coordinate systems
try:
    data["coord_systems"] = {n: csm.GetCoordinateSystem(n)
                            for n in csm.ListCoordinateSystems()}
except Exception as e:
    print(f"⚠️ Warning getting coordinate systems: {e}")

# Mesh operations
try:
    data["mesh_ops"] = {m: mesh.meshoperations[m].props
                       for m in mesh.meshoperations}
except Exception as e:
    print(f"⚠️ Warning getting mesh operations: {e}")

# Model history
try:
    data["history"] = hfss.odesign.GetModelHistory()
except Exception as e:
    print(f"⚠️ Warning getting model history: {e}")

# Boundaries and ports
data["boundaries"], data["excitations"] = grab_bounds_ports()

print(f"✓ Extracted {len(data['objects'])} objects")
print(f"✓ Extracted {len(data['boundaries'])} boundaries")
print(f"✓ Extracted {len(data['excitations'])} excitations")
print(f"✓ Extracted {len(data['variables'])} variables")
```

except Exception as e:
print(f”❌ Error during data extraction: {e}”)
raise

# ───────── save files ─────────

try:
base = f”HFSS_Extract_{hfss.project_name}*{hfss.design_name}*{ts}”

```
# Save JSON
with open(base + ".json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
print("📄 JSON  →", base + ".json")

# Save CSV if requested
if EXPORT_CSV and data["variables"]:
    with open(base + "_variables.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["Variable", "Value"],
                                 *data["variables"].items()])
    print("📊 CSV   →", base + "_variables.csv")
```

except Exception as e:
print(f”❌ Error saving files: {e}”)
raise

# ───────── cleanup ─────────

try:
hfss.release_desktop(close_projects=False, close_desktop=False)
print(“✅ Extraction complete.”)
except Exception as e:
print(f”⚠️ Warning during cleanup: {e}”)
print(“✅ Extraction complete (with cleanup warning).”)