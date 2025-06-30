import os
import numpy as np
import pandas as pd
from scipy import signal

def apply_bandpass_filter(data, lowcut=0.5, highcut=40, sampling_rate=250, order=4):
    """
    Apply bandpass filter to EEG data.
    
    Args:
        data (np.ndarray): EEG data (samples x channels)
        lowcut (float): Low cutoff frequency in Hz
        highcut (float): High cutoff frequency in Hz
        sampling_rate (int): Sampling rate in Hz
        order (int): Filter order
    
    Returns:
        np.ndarray: Filtered EEG data
    """
    # Calculate Nyquist frequency
    nyquist = sampling_rate / 2
    
    # Normalize frequencies
    low_norm = lowcut / nyquist
    high_norm = highcut / nyquist
    
    # Design Butterworth bandpass filter
    b, a = signal.butter(order, [low_norm, high_norm], btype='bandpass')
    
    # Apply filter to each channel
    filtered_data = np.zeros_like(data)
    for channel in range(data.shape[1]):
        filtered_data[:, channel] = signal.filtfilt(b, a, data[:, channel])
    
    return filtered_data

def process_eeg_file(file_path):
    """
    Process a single EEG CSV file with bandpass filtering.
    
    Args:
        file_path (str): Path to the CSV file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Processing: {file_path}")
        
        # Read CSV file with semicolon separator
        eeg_data = pd.read_csv(file_path, sep=';')
        
        # Convert to numpy array for filtering
        data_array = eeg_data.values
        
        # Apply bandpass filter (0.5-40 Hz)
        filtered_array = apply_bandpass_filter(
            data_array, 
            lowcut=0.5, 
            highcut=40, 
            sampling_rate=250, 
            order=4
        )
        
        # Create filtered DataFrame with original column names
        filtered_df = pd.DataFrame(filtered_array, columns=eeg_data.columns)
        
        # Generate output filename
        base_name = os.path.splitext(file_path)[0]
        output_path = f"{base_name}_filtered.csv"
        
        # Save filtered data
        filtered_df.to_csv(output_path, sep=';', index=False)
        
        print(f"  -> Saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """
    Main function to iterate through folders and process target CSV files.
    """
    # Target filenames to look for
    target_files = ["task1_memorize.csv", "task2_viewing.csv", "task3_recall.csv"]
    
    # Get current directory
    current_dir = os.getcwd()
    print(f"Scanning directory: {current_dir}")
    print(f"Looking for files: {target_files}")
    print("-" * 50)
    
    processed_count = 0
    found_count = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(current_dir):
        for filename in files:
            if filename in target_files:
                found_count += 1
                file_path = os.path.join(root, filename)
                
                if process_eeg_file(file_path):
                    processed_count += 1
                
                print()  # Empty line for readability
    
    print(f"Summary: Found {found_count} files, successfully processed {processed_count}")

if __name__ == "__main__":
    main()