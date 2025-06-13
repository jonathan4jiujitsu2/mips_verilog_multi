"""
HFSS 2024 R2 Debug Script
Specifically designed to debug connection issues with Ansys Electronics Desktop 2024 R2
"""

import win32com.client
import time
import sys

def debug_hfss_2024():
    """Debug HFSS 2024 R2 connection step by step"""
    
    print("🔍 HFSS 2024 R2 Debug Script")
    print("=" * 50)
    
    # Step 1: Try different COM interface versions
    com_variants = [
        "Ansoft.ElectronicsDesktop",
        "Ansoft.ElectronicsDesktop.2024.2",
        "Ansoft.ElectronicsDesktop.2024.1", 
        "Ansoft.ElectronicsDesktop.24.2"
    ]
    
    hfss_app = None
    desktop = None
    
    for com_string in com_variants:
        try:
            print(f"\n🔄 Trying COM interface: {com_string}")
            hfss_app = win32com.client.Dispatch(com_string)
            
            print("  ✅ COM interface connected")
            print("  ⏳ Waiting 5 seconds for initialization...")
            time.sleep(5)
            
            print("  🔄 Getting Desktop...")
            desktop = hfss_app.GetDesktop()
            
            version = desktop.GetVersion()
            print(f"  ✅ SUCCESS! Connected to HFSS {version}")
            break
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            continue
    
    if not desktop:
        print("\n❌ All COM interface attempts failed!")
        return None, None
        
    # Step 2: Test basic functionality
    try:
        print(f"\n📋 HFSS Version: {desktop.GetVersion()}")
        
        # Get active project
        print("🔄 Getting active project...")
        project = desktop.GetActiveProject()
        if project:
            project_name = project.GetName()
            print(f"✅ Active Project: {project_name}")
            
            # Get active design
            print("🔄 Getting active design...")
            design = project.GetActiveDesign()
            if design:
                design_name = design.GetName()
                solver_type = design.GetSolverType()
                print(f"✅ Active Design: {design_name}")
                print(f"✅ Solver Type: {solver_type}")
                
                # Test if it's HFSS or Modal Network
                if "HFSS" in solver_type or "Modal" in solver_type:
                    print("✅ Design type is compatible")
                    
                    # Try to get 3D Modeler
                    print("🔄 Testing 3D Modeler access...")
                    try:
                        editor = design.SetActiveEditor("3D Modeler")
                        print("✅ 3D Modeler accessible")
                        
                        # Try to get objects
                        try:
                            objects = editor.GetObjectsInGroup("Solids")
                            if objects:
                                print(f"✅ Found {len(objects)} solid objects:")
                                for i, obj in enumerate(objects[:5]):  # Show first 5
                                    print(f"    {i+1}. {obj}")
                                if len(objects) > 5:
                                    print(f"    ... and {len(objects)-5} more")
                            else:
                                print("⚠️ No solid objects found")
                        except Exception as e:
                            print(f"⚠️ Could not get objects: {e}")
                            
                    except Exception as e:
                        print(f"❌ 3D Modeler access failed: {e}")
                        
                else:
                    print(f"⚠️ Unexpected solver type: {solver_type}")
                    
            else:
                print("❌ No active design found")
                designs = project.GetDesignNames()
                print(f"Available designs: {list(designs)}")
                
        else:
            print("❌ No active project found")
            projects = desktop.GetProjects()
            print(f"Available projects: {list(projects)}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
    return hfss_app, desktop


def test_extraction_methods(hfss_app, desktop):
    """Test specific extraction methods"""
    
    if not desktop:
        print("❌ No desktop connection to test")
        return
        
    try:
        project = desktop.GetActiveProject()
        design = project.GetActiveDesign()
        
        print(f"\n🧪 Testing Extraction Methods")
        print("=" * 40)
        
        # Test 1: Variables
        print("1. Testing variable extraction...")
        try:
            variables = design.GetVariables()
            if variables:
                print(f"   ✅ Found {len(variables)} variables")
                for var in variables[:3]:  # Show first 3
                    try:
                        value = design.GetVariableValue(var)
                        print(f"      {var} = {value}")
                    except:
                        print(f"      {var} = <error getting value>")
            else:
                print("   ⚠️ No variables found")
        except Exception as e:
            print(f"   ❌ Variable extraction failed: {e}")
            
        # Test 2: Materials
        print("\n2. Testing material extraction...")
        try:
            def_manager = project.GetDefinitionManager()
            materials = def_manager.GetMaterialNames()
            if materials:
                print(f"   ✅ Found {len(materials)} materials")
                for mat in materials[:5]:  # Show first 5
                    print(f"      {mat}")
            else:
                print("   ⚠️ No materials found")
        except Exception as e:
            print(f"   ❌ Material extraction failed: {e}")
            
        # Test 3: Boundaries/Excitations
        print("\n3. Testing boundary/excitation extraction...")
        try:
            boundary_module = design.GetModule("BoundarySetup")
            
            boundaries = boundary_module.GetBoundaries()
            if boundaries:
                print(f"   ✅ Found {len(boundaries)} boundaries")
                for bnd in boundaries[:3]:
                    print(f"      {bnd}")
            
            excitations = boundary_module.GetExcitations()
            if excitations:
                print(f"   ✅ Found {len(excitations)} excitations")
                for exc in excitations[:3]:
                    print(f"      {exc}")
                    
        except Exception as e:
            print(f"   ❌ Boundary/Excitation extraction failed: {e}")
            
    except Exception as e:
        print(f"❌ Testing failed: {e}")


def main():
    """Main debug function"""
    
    print("🚀 Starting HFSS 2024 R2 Debug Session")
    print("Make sure your HFSS project is open and ready!")
    input("\nPress ENTER when ready...")
    
    # Step 1: Debug connection
    hfss_app, desktop = debug_hfss_2024()
    
    if desktop:
        print("\n🎉 Connection successful!")
        
        # Step 2: Test extraction methods
        test_extraction_methods(hfss_app, desktop)
        
        print("\n✅ Debug complete! The extractor should work now.")
        print("You can now run your main extraction script.")
        
    else:
        print("\n❌ Connection failed!")
        print("\nPossible solutions:")
        print("1. Try closing and reopening HFSS")
        print("2. Wait longer for HFSS to fully load")
        print("3. Check if Modal Network designs need special handling")
        print("4. Try running immediately after opening HFSS")
        
    input("\nPress ENTER to exit...")


if __name__ == "__main__":
    main()
