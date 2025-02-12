
import os
import pandas as pd
from sqlalchemy import create_engine, text
import re


DB_USER = 'root'
DB_PASSWORD = '5kytr335t4ff'
DB_HOST = 'localhost'
DB_NAME = 'experiment_data'

engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

folder_path = "C:\\Users\\flora\\datareview\\logs"

def is_valid_file(file_path, root):
    folder_name = os.path.basename(root).lower()

    # Exclude specific folders with names 's', 'support', and '!!trash'
    if folder_name in ['s', 'support', '!!trash']:
        return False

    # Exclude files with specific keywords in their names
    file_name = os.path.basename(file_path).lower()
    if any(keyword in file_name for keyword in ['summary', 'pid', 'alerts']):
        return False

    # Extract base name without duplicate markers like "(1)", "(2)"
    base_name_no_marker = re.sub(r'\(\d+\)$', '', file_name)  # Remove "(1)" or "(2)" if present
    base_name_no_marker_with_extension = f"{base_name_no_marker}{os.path.splitext(file_name)[1]}"

    # Check if the original version of the file exists in the directory
    all_files = [os.path.basename(f).lower() for f in os.listdir(root)]
    if base_name_no_marker_with_extension in all_files and file_name != base_name_no_marker_with_extension:
        # If the original file exists and this file is a duplicate, exclude it
        return False

    # Allow only .csv or .xlsx files
    return file_path.endswith(('.csv', '.xlsx'))


def parse_file_name(file_name):
    """
    extract the sorbent name and test round from the file name
    """
    # remove the file extension
    base_name = os.path.splitext(file_name)[0]

    # use regularization to extract the sorbent name (before the date) and test round
    match = re.match(r'^(.*?)(_?\d{6}).*$', base_name)
    if match:
        sorbent_name = match.group(1)  #the part before the date is sorbent name
        # check if there is a test round number at the end of the file name
        test_round_match = re.search(r'_(\d+)$', base_name)
        test_round = test_round_match.group(1) if test_round_match else None
        return sorbent_name, test_round
    return base_name, None


def import_file(file_path, conn):
    try:
        # extract sorbent name and test round from the file name
        file_name = os.path.basename(file_path)
        sorbent_name, test_round = parse_file_name(file_name)

        # read the file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            print(f"Unsupported file type: {file_path}")
            return

        # add info.
        df['sorbent_name'] = sorbent_name
        df['test_round'] = test_round

        # check if the table exists
        existing_columns = pd.read_sql("DESCRIBE ax500", conn)['Field'].tolist()
        matching_columns = [col for col in df.columns if col in existing_columns]
        df = df[matching_columns]

        # if no matching columns, skip
        if df.empty:
            print(f"No matching columns for file: {file_path}. Skipping import.")
            return

        # transfer the frame of thetime
        if 'TheTime' in df.columns:
            df['TheTime'] = pd.to_datetime(df['TheTime'], format='%m/%d/%y %H:%M:%S', errors='coerce')
            invalid_rows = df[df['TheTime'].isnull()]
            if not invalid_rows.empty:
                print(f"Invalid time rows found in {file_name}: {len(invalid_rows)}")
                invalid_rows.to_csv('invalid_rows_log.csv', index=False, mode='a', header=False)
            df = df[df['TheTime'].notnull()]



        # check if there are any duplicate entries
        for index, row in df.iterrows():
            query = text(
                "SELECT 1 FROM ax500 WHERE sorbent_name = :sorbent_name AND TheTime = :TheTime LIMIT 1"
            )
            result = conn.execute(query, {"sorbent_name": row['sorbent_name'], "TheTime": row['TheTime']}).fetchone()
            
            # if duplicate entry found, skip
            if result:
                print(f"Duplicate entry found for sorbent '{row['sorbent_name']}' at time '{row['TheTime']}'. Skipping.")
                continue

            # insert
            row.to_frame().T.to_sql('ax500', engine, if_exists='append', index=False)
        
        print(f"Successfully imported: {file_path} (sorbent: {sorbent_name}, round: {test_round})")
    except Exception as e:
        print(f"Error importing {file_path}: {e}")


# Iterate through folders and import data
with engine.connect() as conn:
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if is_valid_file(file_path, root):
                import_file(file_path, conn)