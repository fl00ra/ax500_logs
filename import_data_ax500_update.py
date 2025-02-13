import os
import pandas as pd
from sqlalchemy import create_engine, text
import re
from sqlalchemy.exc import IntegrityError

# Database configuration
DB_USER = 'root'
DB_PASSWORD = '5kytr335t4ff'
DB_HOST = 'localhost'
DB_NAME = 'experiment_data'

engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

# Folder path for logs (also can be changed to google drive api link)
folder_path = "C:\\Users\\flora\\datareview\\logs"

# Excluded folders and keywords
EXCLUDED_FOLDERS = {'s', 'support', '!!trash'}
EXCLUDED_KEYWORDS = {'summary', 'pid', 'alerts'}

def is_valid_file(file_path, root):
    """Check if the file is valid for processing."""
    folder_name = os.path.basename(root).lower()
    if folder_name in EXCLUDED_FOLDERS:
        return False

    file_name = os.path.basename(file_path).lower()
    if any(keyword in file_name for keyword in EXCLUDED_KEYWORDS):
        return False

    # Check for duplicate markers like (1), (2) in file names
    base_name_no_marker = re.sub(r'\(\d+\)$', '', file_name)
    base_name_no_marker_with_extension = f"{base_name_no_marker}{os.path.splitext(file_name)[1]}"
    
    all_files_set = {os.path.basename(f).lower() for f in os.scandir(root)}
    if base_name_no_marker_with_extension in all_files_set and file_name != base_name_no_marker_with_extension:
        return False

    return file_path.endswith(('.csv', '.xlsx'))

def parse_file_name(file_name):
    """Extract the sorbent name and test round from the file name."""
    base_name = os.path.splitext(file_name)[0]
    match = re.match(r'^(.*?)(_?\d{6}).*$', base_name)
    if match:
        sorbent_name = match.group(1)
        test_round_match = re.search(r'_(\d+)$', base_name)
        test_round = test_round_match.group(1) if test_round_match else None
        return sorbent_name, test_round
    return base_name, None



def import_file(file_path, conn, existing_columns, batch_size=100):
    try:
        file_name = os.path.basename(file_path)
        sorbent_name, test_round = parse_file_name(file_name)

        # Read the file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            print(f"Unsupported file type: {file_path}")
            return

        # Add additional columns
        df['sorbent_name'] = sorbent_name
        df['test_round'] = test_round

        # Match columns with database table
        matching_columns = [col for col in df.columns if col in existing_columns]
        df = df[matching_columns]

        if df.empty:
            print(f"No matching columns for file: {file_path}. Skipping import.")
            return

        # Handle datetime parsing
        if 'TheTime' in df.columns:
            df['TheTime'] = pd.to_datetime(df['TheTime'], format='%m/%d/%y %H:%M:%S', errors='coerce')
            df['TheTime'] = df['TheTime'].dt.strftime('%Y-%m-%d %H:%M:%S')  # Convert to MySQL format

            invalid_rows = df[df['TheTime'].isnull()]
            if not invalid_rows.empty:
                invalid_rows.to_csv('invalid_rows_log.csv', index=False, mode='a', header=False)
            df = df[df['TheTime'].notnull()]

        # # Bulk check for duplicates by sorbent_name and test_round
        # duplicate_check_query = text("""
        #     SELECT 1 FROM ax500 
        #     WHERE sorbent_name = :sorbent_name AND test_round = :test_round LIMIT 1
        # """)
        # duplicate_check_result = conn.execute(duplicate_check_query, {
        #     'sorbent_name': sorbent_name,
        #     'test_round': test_round
        # }).fetchone()

        # # Skip the entire file if duplicates are found
        # if duplicate_check_result:
        #     print(f"Duplicate data found for sorbent '{sorbent_name}' and test round '{test_round}'. Skipping file: {file_path}")
        #     return


        # Split data into batches and insert with error handling
        for start in range(0, len(df), batch_size):
            batch = df.iloc[start:start + batch_size]
            try:
                batch.to_sql('ax500', engine, if_exists='append', index=False, method='multi')

            except IntegrityError:
                print(f"Skipping file due to duplicate rows: {file_path}")

        print(f"Successfully imported: {file_path} (sorbent: {sorbent_name}, round: {test_round})")
        
    except Exception as e:
        print(f"Error importing {file_path}: {e}")


# Main execution loop
with engine.begin() as conn:
    # Cache table columns
    existing_columns = pd.read_sql("DESCRIBE ax500", conn)['Field'].tolist()

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if is_valid_file(file_path, root):
                import_file(file_path, conn, existing_columns)
