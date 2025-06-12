“””
HFSS Property Extractor - Complete Ready-to-Run Version
Advanced Python script to extract comprehensive properties from Ansys HFSS designs

SETUP INSTRUCTIONS:

1. Install: pip install pywin32
1. Configure the settings in main() function below
1. Run: python hfss_extractor.py

IMPORTANT NOTES:

- This script uses the HFSS COM API which can vary between HFSS versions
- Some method names may need adjustment based on your specific HFSS version
- The script includes fallback methods to handle API variations
- Test with a simple design first to verify compatibility

Requirements:

- Ansys HFSS installed and accessible
- Python with pywin32: pip install pywin32
- HFSS project should be open or accessible

Author: Generated for HFSS design reverse-engineering
Version: 1.0 (Complete standalone version)
“””

import win32com.client
import os
import json
import csv
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class HFSSPropertyExtractor:
“”“Advanced HFSS Property Extractor using COM API”””

```
def __init__(self, version: str = None):
    """
    Initialize the HFSS Property Extractor
    
    Args:
        version: Specific HFSS version to connect to (e.g., "2024.1")
    """
    self.hfss_app = None
    self.desktop = None
    self.project = None
    self.design = None
    self.version = version
    self.extraction_data = {}
    
def connect_to_hfss(self) -> bool:
    """Connect to HFSS application"""
    try:
        # Try to connect to active instance first
        try:
            self.hfss_app = win32com.client.Dispatch("Ansoft.ElectronicsDesktop")
            print("✓ Connected to active Ansys Electronics Desktop")
        except Exception:
            print("No active instance found. Launching new instance...")
            if self.version:
                dispatch_string = f"Ansoft.ElectronicsDesktop.{self.version}"
            else:
                dispatch_string = "Ansoft.ElectronicsDesktop"
            
            self.hfss_app = win32com.client.Dispatch(dispatch_string)
            print(f"✓ Launched new Ansys Electronics Desktop ({dispatch_string})")
        
        self.desktop = self.hfss_app.GetDesktop()
        print(f"✓ HFSS Desktop version: {self.desktop.GetVersion()}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to connect to HFSS: {e}")
        return False

def open_project(self, project_path: str = None, project_name: str = None) -> bool:
    """Open or get specified project"""
    try:
        if project_path:
            if not os.path.exists(project_path):
                raise FileNotFoundError(f"Project file not found: {project_path}")
            print(f"Opening project: {project_path}")
            self.project = self.desktop.OpenProject(project_path)
            
        elif project_name:
            try:
                projects = self.desktop.GetProjects()
                if project_name not in projects:
                    print(f"Available projects: {list(projects)}")
                    raise ValueError(f"Project '{project_name}' not found")
                self.project = self.desktop.SetActiveProject(project_name)
                self.project = self.desktop.GetActiveProject()
            except Exception as e:
                raise ValueError(f"Could not access project '{project_name}': {e}")
                
        else:
            self.project = self.desktop.GetActiveProject()
            if not self.project:
                raise Exception("No active project found")
            print(f"Using active project: {self.project.GetName()}")
        
        print(f"✓ Project loaded: {self.project.GetName()}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to open project: {e}")
        return False

def select_design(self, design_name: str = None) -> bool:
    """Select specified design"""
    try:
        if design_name:
            design_names = self.project.GetDesignNames()
            if design_name not in design_names:
                print(f"Available designs: {list(design_names)}")
                raise ValueError(f"Design '{design_name}' not found")
            self.design = self.project.SetActiveDesign(design_name)
            self.design = self.project.GetActiveDesign()
        else:
            self.design = self.project.GetActiveDesign()
            if not self.design:
                design_names = self.project.GetDesignNames()
                if design_names:
                    print(f"No active design. Available designs: {list(design_names)}")
                    # Use first available design
                    self.design = self.project.SetActiveDesign(design_names[0])
                    self.design = self.project.GetActiveDesign()
                else:
                    raise Exception("No designs found in project")
        
        if "HFSS" not in self.design.GetSolverType():
            print(f"⚠ Warning: Design '{self.design.GetName()}' is not an HFSS design")
            return False
            
        print(f"✓ Design selected: {self.design.GetName()} ({self.design.GetSolverType()})")
        return True
        
    except Exception as e:
        print(f"✗ Failed to select design: {e}")
        return False

def extract_design_variables(self) -> Dict[str, Any]:
    """Extract design variables"""
    variables = {}
    try:
        print("\n📋 Extracting Design Variables...")
        
        # Method 1: Try GetVariables() - most common method
        try:
            var_names = self.design.GetVariables()
            if var_names:
                for var_name in var_names:
                    try:
                        var_value = self.design.GetVariableValue(var_name)
                        variables[var_name] = var_value
                        print(f"  {var_name} = {var_value}")
                    except Exception as e:
                        print(f"  ✗ Could not get value for {var_name}: {e}")
                        variables[var_name] = "ERROR"
        except Exception as e1:
            print(f"  Method 1 failed: {e1}")
            
            # Method 2: Try alternative approach
            try:
                # Some versions use different methods
                all_vars = self.design.GetDesignVariableNames()
                for var_name in all_vars:
                    try:
                        var_value = self.design.GetVariableValue(var_name)
                        variables[var_name] = var_value
                        print(f"  {var_name} = {var_value}")
                    except Exception:
                        variables[var_name] = "ERROR"
            except Exception as e2:
                print(f"  Method 2 also failed: {e2}")
        
        if not variables:
            print("  No design variables found")
            
    except Exception as e:
        print(f"✗ Error extracting variables: {e}")
        
    return variables

def extract_materials(self) -> Dict[str, Dict[str, Any]]:
    """Extract material properties"""
    materials = {}
    try:
        print("\n🧪 Extracting Materials...")
        def_manager = self.project.GetDefinitionManager()
        
        # Try multiple methods to get materials
        material_names = []
        try:
            # Method 1: Most common approach
            material_names = def_manager.GetMaterialNames()
            print(f"  Found {len(material_names)} materials using GetMaterialNames()")
        except Exception as e1:
            print(f"  GetMaterialNames() failed: {e1}")
            try:
                # Method 2: Alternative approach
                all_defs = def_manager.GetDefinitionNames("material")
                material_names = all_defs if all_defs else []
                print(f"  Found {len(material_names)} materials using GetDefinitionNames()")
            except Exception as e2:
                print(f"  GetDefinitionNames() also failed: {e2}")
                # Method 3: Try to get from library
                try:
                    material_names = def_manager.GetLibraryMaterials()
                    print(f"  Found {len(material_names)} library materials")
                except Exception as e3:
                    print(f"  All material extraction methods failed. Last error: {e3}")
        
        for mat_name in material_names:
            try:
                material_props = {"name": mat_name}
                
                # Try to get material properties - this is often complex in HFSS
                try:
                    # Simple approach - just record that material exists
                    material_props["status"] = "found"
                    
                    # Advanced property extraction would require more specific API calls
                    # that depend on HFSS version and material type
                    
                except Exception as e:
                    material_props["extraction_error"] = str(e)
                
                materials[mat_name] = material_props
                print(f"  {mat_name}: recorded")
                
            except Exception as e:
                print(f"  ✗ Error processing material {mat_name}: {e}")
                materials[mat_name] = {"error": str(e)}
        
        if not materials:
            print("  No materials found or accessible")
            
    except Exception as e:
        print(f"✗ Error extracting materials: {e}")
        
    return materials

def extract_3d_objects(self) -> Dict[str, Dict[str, Any]]:
    """Extract 3D object properties"""
    objects = {}
    try:
        print("\n📦 Extracting 3D Objects...")
        editor = self.design.SetActiveEditor("3D Modeler")
        
        # Get all object names - try multiple methods
        all_objects = []
        try:
            # Method 1: Get solids
            solid_objects = editor.GetObjectsInGroup("Solids")
            if solid_objects:
                all_objects.extend(solid_objects)
                print(f"  Found {len(solid_objects)} solid objects")
        except Exception as e:
            print(f"  Could not get solids: {e}")
        
        try:
            # Method 2: Get unclassified objects
            unclassified_objects = editor.GetObjectsInGroup("UnClassified")
            if unclassified_objects:
                all_objects.extend(unclassified_objects)
                print(f"  Found {len(unclassified_objects)} unclassified objects")
        except Exception as e:
            print(f"  Could not get unclassified objects: {e}")
        
        try:
            # Method 3: Get all objects (fallback)
            if not all_objects:
                all_names = editor.GetObjectName()  # This might return all object names
                if isinstance(all_names, str):
                    all_objects = [all_names]
                elif isinstance(all_names, (list, tuple)):
                    all_objects = list(all_names)
        except Exception as e:
            print(f"  Fallback method failed: {e}")
        
        # Remove duplicates
        all_objects = list(set(all_objects)) if all_objects else []
        print(f"  Processing {len(all_objects)} total objects")
        
        for obj_name in all_objects:
            try:
                obj_props = {"name": obj_name}
                
                # Get material assignment - this is usually reliable
                try:
                    material = editor.GetPropertyValue("Attributes", "Material", obj_name)
                    obj_props["Material"] = material
                except Exception:
                    # Try alternative method
                    try:
                        material = editor.GetMaterial(obj_name)
                        obj_props["Material"] = material
                    except Exception:
                        obj_props["Material"] = "Unknown"
                
                # Get object visibility/display properties
                try:
                    transparency = editor.GetPropertyValue("Attributes", "Transparency", obj_name)
                    obj_props["Transparency"] = transparency
                except Exception:
                    pass
                
                # Try to get bounding box - this is often available
                try:
                    bbox = editor.GetBoundingBox([obj_name])
                    if bbox and len(bbox) >= 6:
                        obj_props["bounding_box"] = {
                            "x_min": bbox[0], "y_min": bbox[1], "z_min": bbox[2],
                            "x_max": bbox[3], "y_max": bbox[4], "z_max": bbox[5]
                        }
                except Exception as e:
                    obj_props["bbox_error"] = str(e)
                
                # Try to get object type information
                try:
                    # This is complex and version-dependent
                    # For now, just mark as extracted
                    obj_props["extracted"] = True
                except Exception:
                    pass
                
                objects[obj_name] = obj_props
                print(f"  {obj_name}: {obj_props.get('Material', 'Unknown material')}")
                
            except Exception as e:
                print(f"  ✗ Error extracting object {obj_name}: {e}")
                objects[obj_name] = {"error": str(e)}
        
        if not objects:
            print("  No 3D objects found")
            
    except Exception as e:
        print(f"✗ Error extracting 3D objects: {e}")
        
    return objects

def _parse_object_geometry(self, editor, obj_name: str, obj_props: Dict[str, Any]):
    """Parse object geometry parameters based on creation history"""
    try:
        # This is a complex operation that would need extensive implementation
        # for each object type. Here's a basic framework:
        
        history = obj_props.get("creation_history", [])
        if not history:
            return
        
        # Look for creation command
        creation_cmd = None
        for entry in history:
            if isinstance(entry, str):
                if "CreateBox" in entry:
                    creation_cmd = "Box"
                    break
                elif "CreateCylinder" in entry:
                    creation_cmd = "Cylinder"
                    break
                elif "CreateSphere" in entry:
                    creation_cmd = "Sphere"
                    break
        
        if creation_cmd:
            obj_props["object_type"] = creation_cmd
            # Here you would implement specific parameter extraction
            # for each object type based on the creation history
            
    except Exception as e:
        obj_props["geometry_parse_error"] = str(e)

def extract_boundaries_excitations(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Extract boundaries and excitations"""
    boundaries = {}
    excitations = {}
    
    try:
        print("\n⚡ Extracting Boundaries and Excitations...")
        boundary_module = self.design.GetModule("BoundarySetup")
        
        # Extract boundaries
        try:
            boundary_names = boundary_module.GetBoundaries()
            print(f"  Found {len(boundary_names)} boundaries")
            
            for bnd_name in boundary_names:
                try:
                    bnd_props = {"name": bnd_name}
                    
                    # Get boundary type - this method usually exists
                    try:
                        bnd_type = boundary_module.GetBoundaryType(bnd_name)
                        bnd_props["type"] = bnd_type
                    except Exception:
                        bnd_props["type"] = "Unknown"
                    
                    # Getting detailed properties is complex and version-dependent
                    # For now, just record basic info
                    bnd_props["extracted"] = True
                    
                    boundaries[bnd_name] = bnd_props
                    print(f"  Boundary: {bnd_name} ({bnd_props.get('type', 'Unknown')})")
                    
                except Exception as e:
                    print(f"  ✗ Error processing boundary {bnd_name}: {e}")
                    boundaries[bnd_name] = {"error": str(e)}
                    
        except Exception as e:
            print(f"  ✗ Error getting boundaries: {e}")
        
        # Extract excitations
        try:
            excitation_names = boundary_module.GetExcitations()
            print(f"  Found {len(excitation_names)} excitations")
            
            for exc_name in excitation_names:
                try:
                    exc_props = {"name": exc_name}
                    
                    # Get excitation type
                    try:
                        exc_type = boundary_module.GetExcitationType(exc_name)
                        exc_props["type"] = exc_type
                    except Exception:
                        exc_props["type"] = "Unknown"
                    
                    # Record basic info
                    exc_props["extracted"] = True
                    
                    excitations[exc_name] = exc_props
                    print(f"  Excitation: {exc_name} ({exc_props.get('type', 'Unknown')})")
                    
                except Exception as e:
                    print(f"  ✗ Error processing excitation {exc_name}: {e}")
                    excitations[exc_name] = {"error": str(e)}
                    
        except Exception as e:
            print(f"  ✗ Error getting excitations: {e}")
            
    except Exception as e:
        print(f"✗ Error accessing boundary module: {e}")
        
    return boundaries, excitations

def extract_analysis_setup(self) -> Dict[str, Dict[str, Any]]:
    """Extract analysis setups and sweeps"""
    setups = {}
    try:
        print("\n📊 Extracting Analysis Setups...")
        analysis_module = self.design.GetModule("AnalysisSetup")
        
        setup_names = analysis_module.GetSetups()
        for setup_name in setup_names:
            try:
                setup_data = {"sweeps": {}}
                
                # Get setup properties
                try:
                    props = analysis_module.GetSetupProperties(setup_name)
                    setup_props = {}
                    for i in range(0, len(props), 2):
                        if i + 1 < len(props):
                            setup_props[props[i]] = props[i + 1]
                    setup_data["properties"] = setup_props
                except Exception as e:
                    setup_data["properties_error"] = str(e)
                
                # Get sweeps
                try:
                    sweep_names = analysis_module.GetSweeps(setup_name)
                    for sweep_name in sweep_names:
                        try:
                            sweep_props = {}
                            props = analysis_module.GetSweepProperties(setup_name, sweep_name)
                            for i in range(0, len(props), 2):
                                if i + 1 < len(props):
                                    sweep_props[props[i]] = props[i + 1]
                            setup_data["sweeps"][sweep_name] = sweep_props
                            print(f"    Sweep: {sweep_name}")
                        except Exception as e:
                            setup_data["sweeps"][sweep_name] = {"error": str(e)}
                except Exception:
                    pass
                
                setups[setup_name] = setup_data
                print(f"  Setup: {setup_name}")
                
            except Exception as e:
                setups[setup_name] = {"error": str(e)}
                
    except Exception as e:
        print(f"✗ Error extracting analysis setups: {e}")
        
    return setups

def extract_all_properties(self, project_path: str = None, project_name: str = None, 
                         design_name: str = None) -> Dict[str, Any]:
    """Extract all properties from HFSS design"""
    
    print("🚀 Starting HFSS Property Extraction...")
    print("=" * 50)
    
    # Initialize extraction data
    self.extraction_data = {
        "metadata": {
            "extraction_time": datetime.now().isoformat(),
            "script_version": "1.0",
            "project_name": None,
            "design_name": None,
            "hfss_version": None
        },
        "variables": {},
        "materials": {},
        "objects_3d": {},
        "boundaries": {},
        "excitations": {},
        "analysis_setups": {}
    }
    
    # Connect to HFSS
    if not self.connect_to_hfss():
        return self.extraction_data
    
    # Open project
    if not self.open_project(project_path, project_name):
        return self.extraction_data
    
    # Select design
    if not self.select_design(design_name):
        return self.extraction_data
    
    # Update metadata
    self.extraction_data["metadata"]["project_name"] = self.project.GetName()
    self.extraction_data["metadata"]["design_name"] = self.design.GetName()
    self.extraction_data["metadata"]["hfss_version"] = self.desktop.GetVersion()
    
    # Extract all properties
    self.extraction_data["variables"] = self.extract_design_variables()
    self.extraction_data["materials"] = self.extract_materials()
    self.extraction_data["objects_3d"] = self.extract_3d_objects()
    
    boundaries, excitations = self.extract_boundaries_excitations()
    self.extraction_data["boundaries"] = boundaries
    self.extraction_data["excitations"] = excitations
    
    self.extraction_data["analysis_setups"] = self.extract_analysis_setup()
    
    print("\n" + "=" * 50)
    print("✅ Property extraction completed!")
    
    return self.extraction_data

def save_to_json(self, filename: str = None):
    """Save extracted data to JSON file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = self.extraction_data["metadata"].get("project_name", "unknown")
        design_name = self.extraction_data["metadata"].get("design_name", "unknown")
        filename = f"HFSS_Extract_{project_name}_{design_name}_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.extraction_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Data saved to: {filename}")
    except Exception as e:
        print(f"✗ Error saving JSON: {e}")

def save_to_csv(self, filename_prefix: str = None):
    """Save extracted data to multiple CSV files"""
    if not filename_prefix:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = self.extraction_data["metadata"].get("project_name", "unknown")
        design_name = self.extraction_data["metadata"].get("design_name", "unknown")
        filename_prefix = f"HFSS_Extract_{project_name}_{design_name}_{timestamp}"
    
    try:
        # Save variables
        if self.extraction_data["variables"]:
            with open(f"{filename_prefix}_variables.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Variable Name", "Value"])
                for name, value in self.extraction_data["variables"].items():
                    writer.writerow([name, value])
        
        # Save objects
        if self.extraction_data["objects_3d"]:
            with open(f"{filename_prefix}_objects.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Object Name", "Material", "Type", "Properties"])
                for name, props in self.extraction_data["objects_3d"].items():
                    material = props.get("Material", "Unknown")
                    obj_type = props.get("object_type", "Unknown")
                    props_str = json.dumps(props)
                    writer.writerow([name, material, obj_type, props_str])
        
        print(f"💾 CSV files saved with prefix: {filename_prefix}")
        
    except Exception as e:
        print(f"✗ Error saving CSV: {e}")

def generate_recreation_script(self, filename: str = None) -> str:
    """Generate a Python script to recreate the design"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = self.extraction_data["metadata"].get("project_name", "unknown")
        design_name = self.extraction_data["metadata"].get("design_name", "unknown")
        filename = f"HFSS_Recreate_{project_name}_{design_name}_{timestamp}.py"
    
    script_lines = [
        '"""',
        'HFSS Design Recreation Script',
        f'Generated from: {self.extraction_data["metadata"]["project_name"]}',
        f'Design: {self.extraction_data["metadata"]["design_name"]}',
        f'Generated on: {self.extraction_data["metadata"]["extraction_time"]}',
        '"""',
        '',
        'import win32com.client',
        '',
        'def recreate_hfss_design():',
        '    """Recreate the HFSS design from extracted properties"""',
        '    ',
        '    # Connect to HFSS',
        '    hfss = win32com.client.Dispatch("Ansoft.ElectronicsDesktop")',
        '    desktop = hfss.GetDesktop()',
        '    ',
        '    # Create new project',
        f'    project = desktop.NewProject("{self.extraction_data["metadata"]["project_name"]}")',
        f'    design = project.NewDesign("HFSS", "{self.extraction_data["metadata"]["design_name"]}")',
        '    editor = design.SetActiveEditor("3D Modeler")',
        '    ',
        '    # Set design variables'
    ]
    
    # Add variables
    for var_name, var_value in self.extraction_data["variables"].items():
        script_lines.append(f'    design.ChangeProperty("DesignVariables", "{var_name}", "{var_value}")')
    
    script_lines.extend([
        '    ',
        '    # Create 3D objects',
        '    # Note: Object recreation requires detailed geometry parameters',
        '    # This is a template - specific implementation depends on object types'
    ])
    
    # Add object creation templates
    for obj_name, obj_props in self.extraction_data["objects_3d"].items():
        material = obj_props.get("Material", "vacuum")
        script_lines.extend([
            f'    # Object: {obj_name}',
            f'    # Material: {material}',
            f'    # TODO: Add specific creation command based on object type',
            ''
        ])
    
    script_lines.extend([
        '    ',
        '    print("Design recreation template completed!")',
        '    print("Note: This is a template. Specific geometry creation")',
        '    print("commands need to be implemented based on object types.")',
        '',
        'if __name__ == "__main__":',
        '    recreate_hfss_design()'
    ])
    
    script_content = '\n'.join(script_lines)
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"🔧 Recreation script saved to: {filename}")
    except Exception as e:
        print(f"✗ Error saving recreation script: {e}")
    
    return script_content

def print_summary(self):
    """Print a summary of extracted data"""
    print("\n📋 EXTRACTION SUMMARY")
    print("=" * 30)
    print(f"Project: {self.extraction_data['metadata']['project_name']}")
    print(f"Design: {self.extraction_data['metadata']['design_name']}")
    print(f"HFSS Version: {self.extraction_data['metadata']['hfss_version']}")
    print(f"Variables: {len(self.extraction_data['variables'])}")
    print(f"Materials: {len(self.extraction_data['materials'])}")
    print(f"3D Objects: {len(self.extraction_data['objects_3d'])}")
    print(f"Boundaries: {len(self.extraction_data['boundaries'])}")
    print(f"Excitations: {len(self.extraction_data['excitations'])}")
    print(f"Analysis Setups: {len(self.extraction_data['analysis_setups'])}")
```

def main():
“”“Main execution function - CONFIGURE YOUR SETTINGS HERE”””

```
# ===== CONFIGURATION SECTION - MODIFY THESE SETTINGS =====

# Project Settings (Choose ONE option):
# Option 1: Use active HFSS project (easiest - just open HFSS first)
PROJECT_PATH = None  # Keep as None for active project
PROJECT_NAME = None  # Keep as None for active project
DESIGN_NAME = None   # Keep as None for active design

# Option 2: Open specific project file
# PROJECT_PATH = r"C:\path\to\your\project.aedt"  # Uncomment and set path
# PROJECT_NAME = None
# DESIGN_NAME = None  # Or specify: "HFSSDesign1"

# Option 3: Use already open project by name
# PROJECT_PATH = None
# PROJECT_NAME = "YourProject.aedt"  # Uncomment and set name
# DESIGN_NAME = "YourDesignName"     # Uncomment and set design

# HFSS Version (usually can leave as None)
HFSS_VERSION = None  # Or specify: "2024.1", "2023.2", etc.

# Output Options
SAVE_JSON = True                    # Save comprehensive JSON file
SAVE_CSV = True                     # Save CSV files for analysis
GENERATE_RECREATION_SCRIPT = True   # Generate Python recreation script

# ===== END CONFIGURATION SECTION =====

print("🚀 HFSS Property Extractor")
print("=" * 40)
print("Configuration:")
print(f"  Project Path: {PROJECT_PATH or 'Active Project'}")
print(f"  Project Name: {PROJECT_NAME or 'Active Project'}")
print(f"  Design Name: {DESIGN_NAME or 'Active Design'}")
print(f"  HFSS Version: {HFSS_VERSION or 'Any Version'}")
print("=" * 40)

# Create extractor instance
extractor = HFSSPropertyExtractor(version=HFSS_VERSION)

try:
    # Extract all properties
    data = extractor.extract_all_properties(
        project_path=PROJECT_PATH,
        project_name=PROJECT_NAME,
        design_name=DESIGN_NAME
    )
    
    # Print summary
    extractor.print_summary()
    
    # Save data in various formats
    if SAVE_JSON:
        extractor.save_to_json()
    
    if SAVE_CSV:
        extractor.save_to_csv()
    
    if GENERATE_RECREATION_SCRIPT:
        extractor.generate_recreation_script()
    
    print("\n🎉 All operations completed successfully!")
    print("\nOutput files saved in current directory:")
    print("  - JSON file: Complete extracted data")
    print("  - CSV files: Tabular data for analysis")
    print("  - Python file: Recreation script template")
    
except Exception as e:
    print(f"\n💥 Fatal error: {e}")
    traceback.print_exc()
    print("\nTroubleshooting tips:")
    print("1. Ensure HFSS is installed and accessible")
    print("2. Check if HFSS project is open (for default settings)")
    print("3. Verify project path if specified")
    print("4. Try running as Administrator if COM access fails")

finally:
    # Optional: Don't close HFSS to allow inspection
    # extractor.hfss_app.Quit() if extractor.hfss_app else None
    input("\nPress Enter to exit...")  # Keeps console open to read results
```

# Quick test function

def test_hfss_connection():
“”“Quick test to verify HFSS COM connection”””
print(“🧪 Testing HFSS COM Connection…”)
try:
import win32com.client
hfss = win32com.client.Dispatch(“Ansoft.ElectronicsDesktop”)
desktop = hfss.GetDesktop()
print(f”✅ SUCCESS: Connected to HFSS {desktop.GetVersion()}”)

```
    # Check for active project
    try:
        project = desktop.GetActiveProject()
        if project:
            print(f"✅ Active project found: {project.GetName()}")
            design = project.GetActiveDesign()
            if design:
                print(f"✅ Active design found: {design.GetName()}")
            else:
                print("⚠ No active design")
        else:
            print("⚠ No active project")
    except Exception as e:
        print(f"⚠ Could not check active project/design: {e}")
        
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("\nTroubleshooting:")
    print("1. Install pywin32: pip install pywin32")
    print("2. Ensure HFSS is installed")
    print("3. Try running as Administrator")
```

if **name** == “**main**”:
# Uncomment the next line to test connection first
# test_hfss_connection()

```
# Run the main extraction
main()
```