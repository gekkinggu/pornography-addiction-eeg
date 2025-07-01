import os
import glob

def delete_non_filtered_csv_files(directory):
    """
    Iterate through folders and delete CSV files that don't end with '_filtered'
    """
    deleted_count = 0
    
    # Get all subdirectories in the current directory
    for root, dirs, files in os.walk(directory):
        # Look for CSV files in each directory
        csv_files = glob.glob(os.path.join(root, "*.csv"))
        
        for csv_file in csv_files:
            try:
                # Get the filename without extension
                filename = os.path.splitext(os.path.basename(csv_file))[0]
                
                # Check if filename ends with '_filtered'
                if not filename.endswith('_filtered'):
                    print(f"Deleting: {csv_file}")
                    os.remove(csv_file)
                    deleted_count += 1
                else:
                    print(f"Keeping: {csv_file}")
                    
            except Exception as e:
                print(f"Error processing {csv_file}: {str(e)}")
    
    print(f"\nDeletion completed! Deleted {deleted_count} CSV files.")

# Run the deletion function on current directory
current_directory = r"c:\Users\rivaa\Documents\MEDICAL TECHNOLOGY\Semester 4\Ilmu Data Medis\_FINAL PROJECT\dataset_processed_1"

# Ask for confirmation before proceeding
print("WARNING: This will permanently delete CSV files that don't end with '_filtered'")
print(f"Directory: {current_directory}")
confirmation = input("Are you sure you want to proceed? (yes/no): ")

if confirmation.lower() in ['yes', 'y']:
    delete_non_filtered_csv_files(current_directory)
else:
    print("Operation cancelled.")