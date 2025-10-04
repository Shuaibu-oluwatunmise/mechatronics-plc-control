import os

# Folders to search - adjust if needed
search_paths = [
    "D:\\",  # Replace with your mounted drive letter for PLCSIM ISO (e.g. D:, E:)
    "C:\\Program Files",
    "C:\\Program Files (x86)"
]

# File/folder name keywords
keywords = ["api", "sdk", "plcsim"]

# File extensions of interest
extensions = [".msi", ".exe", ".dll"]

def search_files(base_path):
    for root, dirs, files in os.walk(base_path):
        for name in files:
            lower_name = name.lower()
            if any(key in lower_name for key in keywords) and any(lower_name.endswith(ext) for ext in extensions):
                print("FOUND FILE:", os.path.join(root, name))
        for d in dirs:
            lower_d = d.lower()
            if any(key in lower_d for key in keywords):
                print("FOUND DIR:", os.path.join(root, d))

if __name__ == "__main__":
    for path in search_paths:
        if os.path.exists(path):
            print(f"\n--- Searching in {path} ---")
            search_files(path)
        else:
            print(f"\n[!] Path not found: {path}")
