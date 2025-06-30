import os

def delete_unfiltered_csv_files():
    """
    Delete CSV files that don't have '_filtered' in their filename.
    Iterates through all subdirectories in the current directory.
    """
    # Get current directory
    current_dir = os.getcwd()
    print(f"Scanning directory: {current_dir}")
    print("Looking for unfiltered CSV files to delete...")
    print("-" * 50)
    
    deleted_count = 0
    found_csv_count = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(current_dir):
        for filename in files:
            # Check if it's a CSV file
            if filename.lower().endswith('.csv'):
                found_csv_count += 1
                
                # Check if it's NOT a filtered file
                if '_filtered' not in filename:
                    file_path = os.path.join(root, filename)
                    
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                        deleted_count += 1
                        
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
    
    print("-" * 50)
    print(f"Summary:")
    print(f"Total CSV files found: {found_csv_count}")
    print(f"Unfiltered files deleted: {deleted_count}")
    print(f"Filtered files kept: {found_csv_count - deleted_count}")

def main():
    """
    Main function with confirmation prompt.
    """
    print("WARNING: This will permanently delete all CSV files that don't contain '_filtered' in their name.")
    confirmation = input("Are you sure you want to continue? (yes/no): ").lower().strip()
    
    if confirmation in ['yes', 'y']:
        delete_unfiltered_csv_files()
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()