import os
import numpy as np
import pandas as pd
from scipy import signal
import warnings

def check_file_access(file_path):
    """Check if file can be accessed and read."""
    problems = []
    
    try:
        if not os.path.exists(file_path):
            problems.append("File does not exist")
            return problems
        
        if not os.access(file_path, os.R_OK):
            problems.append("File is not readable (permission issue)")
        
        # Try to get file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            problems.append("File is empty (0 bytes)")
        elif file_size < 100:
            problems.append(f"File is very small ({file_size} bytes) - possibly incomplete")
            
    except Exception as e:
        problems.append(f"File access error: {e}")
    
    return problems

def check_csv_format(file_path):
    """Check CSV format and structure issues."""
    problems = []
    
    try:
        # Try reading with different separators
        separators_to_try = [';', ',', '\t']
        successful_read = False
        used_separator = None
        
        for sep in separators_to_try:
            try:
                df = pd.read_csv(file_path, sep=sep, nrows=5)
                if df.shape[1] > 1:  # More than one column suggests correct separator
                    successful_read = True
                    used_separator = sep
                    break
            except:
                continue
        
        if not successful_read:
            problems.append("Cannot parse CSV with any common separator")
            return problems
        
        if used_separator != ';':
            problems.append(f"Using separator '{used_separator}' instead of expected ';'")
        
        # Read full file with correct separator
        df = pd.read_csv(file_path, sep=used_separator)
        
        # Check basic structure
        if df.shape[0] == 0:
            problems.append("File has no data rows (only header)")
        
        if df.shape[1] < 2:
            problems.append(f"Too few columns ({df.shape[1]}) - expected multiple EEG channels")
        
        # Check for expected EEG channel count (typically 19 channels based on your example)
        if df.shape[1] != 19:
            problems.append(f"Unexpected number of channels ({df.shape[1]}) - expected 19")
        
        # Check for duplicate column names
        if df.columns.duplicated().any():
            problems.append("Duplicate column names found")
        
    except UnicodeDecodeError as e:
        problems.append(f"File encoding issue: {e}")
    except Exception as e:
        problems.append(f"CSV format error: {e}")
    
    return problems

def check_data_content(file_path):
    """Check data content and quality issues."""
    problems = []
    
    try:
        # Determine separator (reuse logic from format check)
        separators_to_try = [';', ',', '\t']
        df = None
        
        for sep in separators_to_try:
            try:
                df = pd.read_csv(file_path, sep=sep)
                if df.shape[1] > 1:
                    break
            except:
                continue
        
        if df is None:
            problems.append("Cannot read file for data analysis")
            return problems
        
        # Check for completely empty data
        if df.empty:
            problems.append("DataFrame is completely empty")
            return problems
        
        # Check each column for data issues
        for col_idx, col_name in enumerate(df.columns):
            col_data = df[col_name]
            
            # Check if column is numeric
            if not pd.api.types.is_numeric_dtype(col_data):
                # Try to convert to numeric
                numeric_col = pd.to_numeric(col_data, errors='coerce')
                non_numeric_count = numeric_col.isna().sum() - col_data.isna().sum()
                if non_numeric_count > 0:
                    problems.append(f"Column '{col_name}' has {non_numeric_count} non-numeric values")
            else:
                numeric_col = col_data
            
            # Check for all NaN
            if numeric_col.isna().all():
                problems.append(f"Column '{col_name}' is entirely NaN/missing")
                continue
            
            # Check for mostly NaN
            nan_percentage = (numeric_col.isna().sum() / len(numeric_col)) * 100
            if nan_percentage > 50:
                problems.append(f"Column '{col_name}' is {nan_percentage:.1f}% NaN/missing")
            
            # Check for zero variance (constant values)
            valid_data = numeric_col.dropna()
            if len(valid_data) > 1 and valid_data.std() == 0:
                problems.append(f"Column '{col_name}' has zero variance (all same value: {valid_data.iloc[0]})")
            
            # Check for extreme values that might cause filter issues
            if len(valid_data) > 0:
                data_range = valid_data.max() - valid_data.min()
                if abs(valid_data.max()) > 10000 or abs(valid_data.min()) > 10000:
                    problems.append(f"Column '{col_name}' has extreme values (range: {valid_data.min():.2f} to {valid_data.max():.2f})")
                
                # Check for infinite values
                if np.isinf(valid_data).any():
                    problems.append(f"Column '{col_name}' contains infinite values")
        
        # Check overall data quality
        total_numeric_values = df.select_dtypes(include=[np.number]).count().sum()
        total_cells = df.shape[0] * df.shape[1]
        
        if total_numeric_values < total_cells * 0.8:
            problems.append(f"Less than 80% of data is numeric ({total_numeric_values}/{total_cells})")
        
        # Check if data length is sufficient for filtering
        if df.shape[0] < 100:
            problems.append(f"Very few data points ({df.shape[0]}) - may cause filter instability")
        
    except Exception as e:
        problems.append(f"Data content analysis error: {e}")
    
    return problems

def check_filter_compatibility(file_path):
    """Check if data is compatible with bandpass filtering."""
    problems = []
    
    try:
        # Read the data
        separators_to_try = [';', ',', '\t']
        df = None
        
        for sep in separators_to_try:
            try:
                df = pd.read_csv(file_path, sep=sep)
                if df.shape[1] > 1:
                    break
            except:
                continue
        
        if df is None:
            return ["Cannot read file for filter compatibility check"]
        
        # Convert to numeric
        numeric_df = df.apply(pd.to_numeric, errors='coerce')
        
        # Check if we have enough valid data
        valid_data = numeric_df.dropna()
        if len(valid_data) < 50:
            problems.append("Insufficient valid data points for reliable filtering")
            return problems
        
        # Try to simulate the filter design with sample data
        try:
            # Test filter parameters
            sampling_rate = 250
            lowcut = 0.5
            highcut = 40
            order = 4
            
            nyquist = sampling_rate / 2
            low_norm = lowcut / nyquist
            high_norm = highcut / nyquist
            
            # Check if frequency bounds are valid
            if low_norm >= 1.0 or high_norm >= 1.0:
                problems.append("Filter frequency bounds exceed Nyquist frequency")
            
            if low_norm >= high_norm:
                problems.append("Low cutoff frequency >= High cutoff frequency")
            
            # Try to design the filter
            b, a = signal.butter(order, [low_norm, high_norm], btype='bandpass')
            
            # Test filter on a small sample of actual data
            for col in numeric_df.columns[:min(3, len(numeric_df.columns))]:  # Test first 3 columns
                col_data = numeric_df[col].dropna()
                if len(col_data) >= 50:
                    try:
                        # Test filtfilt with actual data
                        test_sample = col_data.head(min(100, len(col_data))).values
                        filtered_sample = signal.filtfilt(b, a, test_sample)
                        
                        # Check if filter output is reasonable
                        if np.all(filtered_sample == 0):
                            problems.append(f"Filter produces all zeros for column '{col}'")
                        elif not np.all(np.isfinite(filtered_sample)):
                            problems.append(f"Filter produces non-finite values for column '{col}'")
                            
                    except Exception as filter_error:
                        problems.append(f"Filter fails on column '{col}': {filter_error}")
                        
        except Exception as design_error:
            problems.append(f"Filter design error: {design_error}")
            
    except Exception as e:
        problems.append(f"Filter compatibility check error: {e}")
    
    return problems

def diagnose_eeg_file(file_path):
    """Run comprehensive diagnostics on an EEG CSV file."""
    print(f"\n{'='*60}")
    print(f"DIAGNOSING: {file_path}")
    print(f"{'='*60}")
    
    all_problems = []
    
    # 1. File Access Check
    print("1. Checking file access...")
    access_problems = check_file_access(file_path)
    if access_problems:
        all_problems.extend([f"ACCESS: {p}" for p in access_problems])
        print(f"   [X] {len(access_problems)} access problem(s) found")
        # If file can't be accessed, skip other checks
        if "File does not exist" in access_problems or "not readable" in str(access_problems):
            return all_problems
    else:
        print("   [OK] File access OK")
    
    # 2. CSV Format Check
    print("2. Checking CSV format...")
    format_problems = check_csv_format(file_path)
    if format_problems:
        all_problems.extend([f"FORMAT: {p}" for p in format_problems])
        print(f"   [X] {len(format_problems)} format problem(s) found")
    else:
        print("   [OK] CSV format OK")
    
    # 3. Data Content Check
    print("3. Checking data content...")
    content_problems = check_data_content(file_path)
    if content_problems:
        all_problems.extend([f"CONTENT: {p}" for p in content_problems])
        print(f"   [X] {len(content_problems)} content problem(s) found")
    else:
        print("   [OK] Data content OK")
    
    # 4. Filter Compatibility Check
    print("4. Checking filter compatibility...")
    filter_problems = check_filter_compatibility(file_path)
    if filter_problems:
        all_problems.extend([f"FILTER: {p}" for p in filter_problems])
        print(f"   [X] {len(filter_problems)} filter problem(s) found")
    else:
        print("   [OK] Filter compatibility OK")
    
    # Summary
    if all_problems:
        print(f"\nPROBLEMS FOUND ({len(all_problems)} total):")
        for problem in all_problems:
            print(f"   - {problem}")
    else:
        print(f"\n[OK] NO PROBLEMS DETECTED - File should process correctly")
    
    return all_problems

def main():
    """
    Main function to scan directory and diagnose EEG files.
    """
    # Target filenames to look for
    target_files = ["task1_memorize.csv", "task2_viewing.csv", "task3_recall.csv"]
    
    # Get current directory
    current_dir = os.getcwd()
    print(f"EEG FILE DIAGNOSTICS")
    print(f"Scanning directory: {current_dir}")
    print(f"Target files: {target_files}")
    
    found_files = []
    problematic_files = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(current_dir):
        for filename in files:
            if filename in target_files:
                file_path = os.path.join(root, filename)
                found_files.append(file_path)
                
                problems = diagnose_eeg_file(file_path)
                if problems:
                    problematic_files.append((file_path, problems))
    
    # Final Summary
    print(f"\n{'='*80}")
    print(f"DIAGNOSTIC SUMMARY")
    print(f"{'='*80}")
    print(f"Total target files found: {len(found_files)}")
    print(f"Problematic files: {len(problematic_files)}")
    print(f"Clean files: {len(found_files) - len(problematic_files)}")
    
    if problematic_files:
        print(f"\nPROBLEMATIC FILES SUMMARY:")
        for file_path, problems in problematic_files:
            print(f"\nFile: {file_path}")
            for problem in problems:
                print(f"   - {problem}")
    
    if len(found_files) == 0:
        print(f"\nWARNING: No target files found. Check if you're in the correct directory.")

if __name__ == "__main__":
    main()