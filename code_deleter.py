import os

# List of allowed CSV filenames (without extension)
allowed_names = {"task1_memorize", "task2_viewing", "task3_recall"}

# Get the current directory
base_dir = os.getcwd()

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".csv"):
            name_without_ext = os.path.splitext(file)[0]
            if name_without_ext not in allowed_names:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")