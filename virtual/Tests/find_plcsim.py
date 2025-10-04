import os

filename = "Siemens.Simatic.PlcSim.Advanced.exe"
search_paths = ["C:\\"]  # search the entire C: drive

found_paths = []

print(f"Searching for {filename}. This may take a while...")

for path in search_paths:
    for root, dirs, files in os.walk(path):
        if filename in files:
            found_paths.append(os.path.join(root, filename))

if found_paths:
    print("\nFound the executable at:")
    for p in found_paths:
        print(p)
else:
    print(f"\nCould not find {filename} on the drive.")
