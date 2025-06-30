import os
import pandas as pd
import numpy as np

def inspect_eeg_data():
    """
    Inspect the structure of EEG data files.
    """
    current_dir = os.getcwd()
    target_files = ["task1_memorize_filtered.csv", "task2_viewing_filtered.csv", "task3_recall_filtered.csv"]
    
    print("EEG Data Inspection Report")
    print("="*50)
    
    found_files = []
    
    # Walk through directories
    for root, dirs, files in os.walk(current_dir):
        subject_folder = os.path.basename(root)
        
        for filename in files:
            if any(target in filename for target in target_files):
                file_path = os.path.join(root, filename)
                found_files.append((subject_folder, filename, file_path))
    
    print(f"Found {len(found_files)} EEG files")
    print("\nFile structure:")
    
    subjects = {}
    for subject, filename, filepath in found_files:
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append(filename)
    
    for subject, files in subjects.items():
        print(f"\n{subject}:")
        for file in files:
            print(f"  - {file}")
    
    # Inspect one file to understand data structure
    if found_files:
        sample_file = found_files[0][2]
        print(f"\nInspecting sample file: {sample_file}")
        
        try:
            # Try semicolon separator first
            df = pd.read_csv(sample_file, sep=';')
        except:
            # Try comma separator
            df = pd.read_csv(sample_file, sep=',')
        
        print(f"Data shape: {df.shape}")
        print(f"Sampling rate: Assuming 250 Hz")
        print(f"Duration: {df.shape[0]/250:.2f} seconds")
        print(f"Channels: {list(df.columns)}")
        print(f"\nFirst few rows:")
        print(df.head())
        
        print(f"\nData statistics:")
        print(f"Min value: {df.min().min():.2f}")
        print(f"Max value: {df.max().max():.2f}")
        print(f"Mean value: {df.mean().mean():.2f}")
    
    return found_files

if __name__ == "__main__":
    inspect_eeg_data()