import os
import sys

def find_dll(root_path, dll_name):
    """Search for DLL file recursively"""
    print(f"Searching for {dll_name} in {root_path}...")
    print("This may take a minute...\n")
    
    matches = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            if dll_name.lower() in filename.lower() and filename.endswith('.dll'):
                full_path = os.path.join(dirpath, filename)
                matches.append(full_path)
                print(f"✓ Found: {full_path}")
    
    if not matches:
        print(f"❌ No files matching '{dll_name}' found in {root_path}")
    else:
        print(f"\n✓ Total matches: {len(matches)}")
    
    return matches

if __name__ == "__main__":
    # Search in Program Files
    search_paths = [
        r"C:\Program Files\Common Files\Siemens",
        r"C:\Program Files (x86)\Siemens",
        r"C:\Program Files\Siemens"
    ]
    
    dll_patterns = [
        "Siemens.Simatic.Simulation",
        "PlcSim.Advanced.API",
        "SimulationRuntime"
    ]
    
    all_matches = []
    
    for path in search_paths:
        if os.path.exists(path):
            print(f"\n{'='*60}")
            print(f"Searching: {path}")
            print('='*60)
            
            for pattern in dll_patterns:
                matches = find_dll(path, pattern)
                all_matches.extend(matches)
        else:
            print(f"⚠ Path not found: {path}")
    
    print("\n" + "="*60)
    print("SUMMARY - All DLLs found:")
    print("="*60)
    for dll in all_matches:
        print(dll)
    
    if not all_matches:
        print("No API DLLs found. The API may not be installed.")
    
    input("\nPress Enter to exit...")