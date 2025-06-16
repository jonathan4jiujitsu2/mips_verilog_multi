# -*- coding: utf-8 -*-

“””
HFSS EXTRACTOR - full model history + ports, boundaries, mesh ops, setups
Outputs:

- HFSS_Extract_<project>*<design>*<timestamp>.json
- HFSS_Extract_<project>*<design>*<timestamp>_variables.csv
  “””

import os
import json
import csv
from datetime import datetime
from pyaedt import Desktop, Hfss

# USER OPTIONS

PROJECT_PATH = None  # r”C:\file.aedt” or None to attach to open project
DESIGN_NAME = None   # “MyDesign” or None = active design
AEDT_VERSION = None  # “2024.2” or None
EXPORT_CSV = True

def main():
ts = datetime.now().strftime(”%Y%m%d_%H%M%S”)

```
# Connect to Desktop
try:
    desktop = Desktop(specified_version=AEDT_VERSION, new_desktop=False)
    print("Connected to Desktop")
except Exception as e:
    print(f"Error connecting to Desktop: {e}")
    return

# Get project
try:
    if PROJECT_PATH and os.path.isfile(PROJECT_PATH):
        project_hdl = desktop.open_project(PROJECT_PATH)
        print(f"Opened project from: {PROJECT_PATH}")
    else:
        project_hdl = desktop.active_project()
        if project_hdl is None:
            print("No project open - open one in AEDT or set PROJECT_PATH")
            return
        print(f"Using active project: {project_hdl.name}")
except Exception as e:
    print(f"Error getting project: {e}")
    return

# Get design name
try:
    if DESIGN_NAME:
        design_name = DESIGN_NAME
        print(f"Using specified design: {design_name}")
    else:
        print("Auto-detecting design...")
        names = None
        
        try:
            if hasattr(project_hdl, "design_names"):
                names = project_hdl.design_names
            elif hasattr(project_hdl, "get_design_names"):
                names = project_hdl.get_design_names()
            else:
                names = list(project_hdl.GetDesignNames())
        except Exception as e:
            print(f"Error getting design names: {e}")
            return
        
        if not names:
            print("Project has no designs - set DESIGN_NAME explicitly")
            return
        
        print(f"Available designs: {names}")
        design_name = names[0]
        print(f"Selected design: {design_name}")
    
    # Set active design
    print("Setting active design...")
    try:
        if hasattr(project_hdl, "set_active_design"):
            project_hdl.set_active_design(design_name)
        else:
            project_hdl.SetActiveDesign(design_name)
    except Exception as e:
        print(f"Warning setting active design: {e}")
    
except Exception as e:
    print(f"Error handling design selection: {e}")
    return

# Connect to HFSS
try:
    print("Connecting to HFSS...")
    hfss = Hfss(
        project=project_hdl,
        designname=design_name,
        specified_version=AEDT_VERSION,
        new_desktop=False,
        close_on_exit=False
    )
    print(f"Project: {hfss.project_name}")
    print(f"Design: {hfss.design_name}")
except Exception as e:
    print(f"Error connecting to HFSS: {e}")
    try:
        print("Trying alternative connection...")
        hfss = Hfss(
            project=project_hdl.name,
            designname=design_name,
            specified_version=AEDT_VERSION,
            new_desktop=False,
            close_on_exit=False
        )
        print(f"Connected - Project: {hfss.project_name}")
        print(f"Connected - Design: {hfss.design_name}")
    except Exception as e2:
        print(f"Alternative connection failed: {e2}")
        return

# Extract data
print("Extracting data...")
data = extract_hfss_data(hfss, ts, desktop.release)

# Save files
save_data(data, hfss.project_name, hfss.design_name, ts)

# Cleanup
try:
    hfss.release_desktop(close_projects=False, close_desktop=False)
    print("Extraction complete.")
except Exception as e:
    print(f"Warning during cleanup: {e}")
    print("Extraction complete with cleanup warning.")
```

def extract_hfss_data(hfss, timestamp, aedt_version):
“”“Extract all HFSS data”””
mdl = hfss.modeler

```
data = {
    "meta": {
        "timestamp": timestamp,
        "project": hfss.project_name,
        "design": hfss.design_name,
        "aedt_version": aedt_version
    },
    "variables": get_variables(hfss),
    "materials": get_materials(hfss),
    "objects": get_objects(mdl),
    "analysis_setups": get_setups(hfss),
    "coord_systems": get_coord_systems(mdl),
    "mesh_ops": get_mesh_ops(hfss),
    "history": get_history(hfss)
}

boundaries, excitations = get_boundaries_and_ports(hfss)
data["boundaries"] = boundaries
data["excitations"] = excitations

print(f"Extracted {len(data['objects'])} objects")
print(f"Extracted {len(data['boundaries'])} boundaries")
print(f"Extracted {len(data['excitations'])} excitations")
print(f"Extracted {len(data['variables'])} variables")

return data
```

def get_variables(hfss):
“”“Extract design variables”””
try:
vm = hfss.variable_manager
if hasattr(vm, “variables”):
return vm.variables
elif hasattr(vm, “properties”):
return vm.properties
else:
return {}
except Exception as e:
print(f”Warning getting variables: {e}”)
return {}

def get_materials(hfss):
“”“Extract materials”””
try:
return list(hfss.materials.material_keys)
except Exception as e:
print(f”Warning getting materials: {e}”)
return []

def get_objects(mdl):
“”“Extract geometric objects”””
objects = {}
try:
for obj in mdl.objects:
try:
if hasattr(obj, “name”):
names = [obj.name]
else:
names = mdl.get_object_name(obj)
if isinstance(names, str):
names = [names]

```
            for name in names:
                if not mdl.does_object_exist(name) or mdl.is_group(name):
                    continue
                
                try:
                    bbox = mdl.get_bounding_box(name)
                except:
                    bbox = []
                
                material = mdl.get_object_material(name, "")
                if not bbox and material in ("", "Unknown"):
                    continue
                
                objects[name] = {
                    "material": material or "Unknown",
                    "color": getattr(obj, "color", None),
                    "primitive": mdl.get_object_type(name) or "Unknown",
                    "params": mdl.get_object_parameters(name) or {},
                    "faces": mdl.get_object_faces(name) or [],
                    "bounding_box": bbox,
                    "history": mdl.get_object_history(name)
                }
        except Exception as e:
            obj_name = getattr(obj, "name", "unknown")
            print(f"Warning processing object {obj_name}: {e}")
            continue
except Exception as e:
    print(f"Warning getting objects: {e}")

return objects
```

def get_boundaries_and_ports(hfss):
“”“Extract boundaries and excitation ports”””
boundaries = {}
excitations = {}

```
try:
    for boundary in hfss.boundaries:
        try:
            entry = {
                "type": boundary.type,
                "props": boundary.props
            }
            
            try:
                entry["faces"] = hfss.boundaries.get_boundary_faces(boundary.name)
            except:
                entry["faces"] = []
            
            if "port" in boundary.type.lower():
                excitations[boundary.name] = entry
            else:
                boundaries[boundary.name] = entry
                
        except Exception as e:
            print(f"Warning processing boundary {boundary.name}: {e}")
            continue
except Exception as e:
    print(f"Warning getting boundaries: {e}")

return boundaries, excitations
```

def get_setups(hfss):
“”“Extract analysis setups”””
try:
setups = {}
for setup in hfss.setups:
setups[setup.name] = {
“props”: setup.props,
“sweeps”: {}
}
for sweep in setup.sweeps:
setups[setup.name][“sweeps”][sweep.name] = sweep.props
return setups
except Exception as e:
print(f”Warning getting setups: {e}”)
return {}

def get_coord_systems(mdl):
“”“Extract coordinate systems”””
try:
csm = mdl.CoordinateSystemManager
coord_systems = {}
for name in csm.ListCoordinateSystems():
coord_systems[name] = csm.GetCoordinateSystem(name)
return coord_systems
except Exception as e:
print(f”Warning getting coordinate systems: {e}”)
return {}

def get_mesh_ops(hfss):
“”“Extract mesh operations”””
try:
mesh = hfss.mesh
mesh_ops = {}
for op_name in mesh.meshoperations:
mesh_ops[op_name] = mesh.meshoperations[op_name].props
return mesh_ops
except Exception as e:
print(f”Warning getting mesh operations: {e}”)
return {}

def get_history(hfss):
“”“Extract model history”””
try:
return hfss.odesign.GetModelHistory()
except Exception as e:
print(f”Warning getting model history: {e}”)
return []

def save_data(data, project_name, design_name, timestamp):
“”“Save extracted data to files”””
base_filename = f”HFSS_Extract_{project_name}*{design_name}*{timestamp}”

```
# Save JSON
try:
    json_filename = base_filename + ".json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"JSON saved: {json_filename}")
except Exception as e:
    print(f"Error saving JSON: {e}")

# Save CSV
if EXPORT_CSV and data["variables"]:
    try:
        csv_filename = base_filename + "_variables.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Variable", "Value"])
            for var, value in data["variables"].items():
                writer.writerow([var, value])
        print(f"CSV saved: {csv_filename}")
    except Exception as e:
        print(f"Error saving CSV: {e}")
```

if **name** == “**main**”:
main()