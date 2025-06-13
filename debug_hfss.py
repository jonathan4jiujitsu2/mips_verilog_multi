"""
Find Real HFSS Process
Locate the actual HFSS process that supports COM interface
"""

import subprocess
import win32com.client
import time

def find_all_ansys_processes():
    """Find all Ansys-related processes"""
    print("🔍 Finding All Ansys Processes...")
    print("-" * 40)
    
    try:
        # Get all running processes
        result = subprocess.run(['tasklist', '/fo', 'csv'], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            ansys_processes = []
            
            for line in lines[1:]:  # Skip header
                if any(keyword in line.lower() for keyword in ['ansys', 'ansoft', 'hfss', 'electronics']):
                    # Parse CSV format
                    parts = line.split('","')
                    if len(parts) >= 2:
                        process_name = parts[0].strip('"')
                        pid = parts[1].strip('"')
                        ansys_processes.append((process_name, pid))
            
            if ansys_processes:
                print("✅ Found Ansys-related processes:")
                for process_name, pid in ansys_processes:
                    print(f"  {process_name} (PID: {pid})")
            else:
                print("❌ No Ansys processes found")
                
            return ansys_processes
        
    except Exception as e:
        print(f"❌ Error finding processes: {e}")
        return []


def check_window_titles():
    """Check for HFSS window titles"""
    print("\n🔍 Checking Window Titles...")
    print("-" * 40)
    
    try:
        # Use tasklist to get window titles
        result = subprocess.run(['tasklist', '/v', '/fo', 'csv'], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            hfss_windows = []
            
            for line in lines[1:]:  # Skip header
                if any(keyword in line.lower() for keyword in ['electronics desktop', 'hfss', 'ansys']):
                    parts = [p.strip('"') for p in line.split('","')]
                    if len(parts) >= 9:  # Window title is usually the last column
                        process_name = parts[0]
                        window_title = parts[-1]
                        if window_title and window_title != "N/A":
                            hfss_windows.append((process_name, window_title))
            
            if hfss_windows:
                print("✅ Found HFSS-related windows:")
                for process_name, window_title in hfss_windows:
                    print(f"  {process_name}: {window_title}")
            else:
                print("❌ No HFSS windows found")
                
            return hfss_windows
        
    except Exception as e:
        print(f"❌ Error checking windows: {e}")
        return []


def test_specific_com_interfaces():
    """Test specific COM interfaces that might work"""
    print("\n🔍 Testing Specific COM Interfaces...")
    print("-" * 40)
    
    # Extended list of possible COM interfaces
    com_interfaces = [
        "Ansoft.ElectronicsDesktop",
        "AnsoftElectronicsDesktop",
        "Ansys.ElectronicsDesktop",
        "ElectronicsDesktop.Application",
        "Ansoft.ElectronicsDesktop.1",
        "AnsoftED.Application",
        "HFSS.Application",
        "Ansoft.HFSS"
    ]
    
    successful_interfaces = []
    
    for interface in com_interfaces:
        print(f"Testing: {interface}")
        
        # Test GetActiveObject first (for running instances)
        try:
            app = win32com.client.GetActiveObject(interface)
            print(f"  ✅ GetActiveObject({interface}) - SUCCESS!")
            
            # Try to get desktop
            try:
                if hasattr(app, 'GetDesktop'):
                    desktop = app.GetDesktop()
                    version = desktop.GetVersion()
                    print(f"     Desktop version: {version}")
                    successful_interfaces.append((interface, "GetActiveObject", app, desktop))
                elif hasattr(app, 'Desktop'):
                    desktop = app.Desktop
                    print(f"     Desktop property accessible")
                    successful_interfaces.append((interface, "GetActiveObject", app, desktop))
                else:
                    print(f"     No Desktop method found")
            except Exception as e:
                print(f"     Desktop access failed: {e}")
                
        except Exception as e:
            print(f"  ❌ GetActiveObject({interface}) failed: {e}")
            
        # Test Dispatch (creates new instance)
        try:
            app = win32com.client.Dispatch(interface)
            print(f"  ✅ Dispatch({interface}) - SUCCESS!")
            
            # Wait for initialization
            time.sleep(2)
            
            # Try to get desktop
            try:
                if hasattr(app, 'GetDesktop'):
                    desktop = app.GetDesktop()
                    version = desktop.GetVersion()
                    print(f"     Desktop version: {version}")
                    successful_interfaces.append((interface, "Dispatch", app, desktop))
                elif hasattr(app, 'Desktop'):
                    desktop = app.Desktop
                    print(f"     Desktop property accessible")
                    successful_interfaces.append((interface, "Dispatch", app, desktop))
                else:
                    print(f"     No Desktop method found")
            except Exception as e:
                print(f"     Desktop access failed: {e}")
                
        except Exception as e:
            print(f"  ❌ Dispatch({interface}) failed: {e}")
    
    return successful_interfaces


def enable_com_interface_in_hfss():
    """Instructions to enable COM interface in HFSS"""
    print("\n🔧 How to Enable COM Interface in HFSS:")
    print("-" * 50)
    print("If COM isn't working, try these steps in HFSS:")
    print("")
    print("1. In HFSS menu: Tools → Options → General Options")
    print("2. Look for 'Enable COM Interface' or similar option")
    print("3. Enable it and restart HFSS")
    print("")
    print("OR")
    print("")
    print("1. In HFSS menu: Tools → Run Script")
    print("2. This activates the scripting interface")
    print("3. Try running the extractor after this")
    print("")
    print("OR")
    print("")
    print("1. Close HFSS completely")
    print("2. Run HFSS as Administrator (if possible)")
    print("3. Open your project")
    print("4. Try the extractor again")


def main():
    """Main diagnostic function"""
    print("🚀 HFSS Process & COM Interface Detective")
    print("=" * 50)
    
    # Step 1: Find all Ansys processes
    processes = find_all_ansys_processes()
    
    # Step 2: Check window titles
    windows = check_window_titles()
    
    # Step 3: Test COM interfaces
    successful_com = test_specific_com_interfaces()
    
    # Step 4: Results
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC RESULTS")
    print("=" * 50)
    
    if successful_com:
        print("✅ SUCCESS! Found working COM interfaces:")
        for interface, method, app, desktop in successful_com:
            print(f"   {interface} via {method}")
        
        print("\n🎉 Your HFSS extractor should use:")
        best_interface = successful_com[0]  # Use the first working one
        print(f'   win32com.client.{best_interface[1]}("{best_interface[0]}")')
        
    else:
        print("❌ No working COM interfaces found")
        print("\nPossible issues:")
        if not processes:
            print("- HFSS might not be running properly")
        else:
            print("- HFSS is running but COM interface is disabled")
            print("- Need to enable scripting/automation in HFSS")
        
        enable_com_interface_in_hfss()
    
    return successful_com


if __name__ == "__main__":
    input("Make sure HFSS is fully loaded with your project, then press ENTER...")
    main()
    input("\nPress ENTER to exit...")
