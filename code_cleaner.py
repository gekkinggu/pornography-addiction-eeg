import os
import pandas as pd
import glob

def clean_csv_files(directory):
    """
    Iterate through folders and clean CSV files by removing NaN values and empty rows
    """
    # Get all subdirectories in the current directory
    for root, dirs, files in os.walk(directory):
        # Look for CSV files in each directory
        csv_files = glob.glob(os.path.join(root, "*.csv"))
        
        for csv_file in csv_files:
            try:
                print(f"Processing: {csv_file}")
                
                # Read the CSV file
                df = pd.read_csv(csv_file, sep=';')
                
                # Remove rows that are completely empty or contain only NaN values
                df_cleaned = df.dropna(how='all')
                
                # Remove rows where all values are empty strings or whitespace
                df_cleaned = df_cleaned[~df_cleaned.apply(lambda x: x.astype(str).str.strip().eq('').all(), axis=1)]
                
                # Remove individual NaN values (optional - you can choose to fill them instead)
                df_cleaned = df_cleaned.dropna()
                
                # Save the cleaned dataframe back to the original file
                df_cleaned.to_csv(csv_file, sep=';', index=False)
                
                print(f"Cleaned: {csv_file} - Removed {len(df) - len(df_cleaned)} rows")
                
            except Exception as e:
                print(f"Error processing {csv_file}: {str(e)}")

# Run the cleaning function on current directory
current_directory = r"c:\Users\rivaa\Documents\MEDICAL TECHNOLOGY\Semester 4\Ilmu Data Medis\_FINAL PROJECT\dataset_processed_1"
clean_csv_files(current_directory)
print("CSV cleaning completed!")