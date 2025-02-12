import os
import pandas as pd
import re

folder_path = "C:\\Users\\flora\\datareview\\logs"

def is_valid_file(file_path, root):
    folder_name = os.path.basename(root).lower()

    # Exclude specific folders
    if folder_name in ['s', 'support', '!!trash']:
        return False

    # Exclude files with specific keywords in their names
    file_name = os.path.basename(file_path).lower()
    if any(keyword in file_name for keyword in ['summary', 'pid', 'alerts']):
        return False

    # Extract base name without duplicate markers like "(1)", "(2)"
    base_name_no_marker = re.sub(r'\(\d+\)$', '', file_name)
    base_name_no_marker_with_extension = f"{base_name_no_marker}{os.path.splitext(file_name)[1]}"

    # Check if the original version of the file exists
    all_files = [os.path.basename(f).lower() for f in os.listdir(root)]
    if base_name_no_marker_with_extension in all_files and file_name != base_name_no_marker_with_extension:
        return False

    # Allow only .csv or .xlsx files
    return file_path.endswith(('.csv', '.xlsx'))


def calculate_total_records(folder_path):
    total_records = 0
    valid_files = 0
    invalid_files = 0

    # Traverse through the folder and process files
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if is_valid_file(file_path, root):
                try:
                    # Read the file and count rows
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    elif file_path.endswith('.xlsx'):
                        df = pd.read_excel(file_path, engine='openpyxl')
                    else:
                        print(f"Unsupported file format: {file_path}")
                        invalid_files += 1
                        continue

                    rows_in_file = len(df)
                    total_records += rows_in_file
                    valid_files += 1

                    print(f"File: {file_path} | Rows: {rows_in_file}")
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    invalid_files += 1

    print("\n--- Summary ---")
    print(f"Total valid files processed: {valid_files}")
    print(f"Total invalid files skipped: {invalid_files}")
    print(f"Total records across all valid files: {total_records}")

    return total_records


# Run the check
total_records = calculate_total_records(folder_path)
print(f"\nTotal records in all valid files: {total_records}")
