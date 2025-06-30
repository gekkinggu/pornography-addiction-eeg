import os

"""
CODE FOR RENAMING THE FILE NAMES FROM RAW
"""

# Mapping of old names to new names
name_map = {
    "EC": "eyes_closed",
    "EO": "eyes_open",
    "H": "happy",
    "C": "calm",
    "S": "sad",
    "F": "fear",
    "M": "task1_memorize",
    "ET": "task2_viewing",
    "R": "task3_recall"
}

# Get current working directory
base_dir = os.getcwd()

# Iterate through each folder in the current directory
for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith('.csv'):
                name, ext = os.path.splitext(filename)
                if name in name_map:
                    new_name = name_map[name] + ext
                    src = os.path.join(folder_path, filename)
                    dst = os.path.join(folder_path, new_name)
                    os.rename(src, dst)
                    print(f"Renamed {src} -> {dst}")

