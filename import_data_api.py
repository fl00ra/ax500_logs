from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import os
import io

# Google Drive API credentials
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'C:\\Users\\flora\\datareview\\logs-ax500-0d8f8243677e.json'  # Replace with your JSON credentials file path

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# Shared folder ID (extracted from the shared link)
FOLDER_ID = '1hSKArYPGUqbEsD8W1woWaxorbfHa28Ei'  # Your folder ID
LOCAL_FOLDER = "C:\\Users\\flora\\datareview\\logs"  # Local path to download files

def list_and_download_files(folder_id, local_folder):
    """List files in the shared folder and download them locally"""
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    # List files in the folder
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    items = results.get('files', [])
    if not items:
        print("No files found.")
        return

    print(f"Found {len(items)} files in the shared folder.")
    for item in items:
        file_id = item['id']
        file_name = item['name']
        local_file_path = os.path.join(local_folder, file_name)

        # Skip download if the file already exists
        if os.path.exists(local_file_path):
            print(f"File already exists, skipping: {file_name}")
            continue

        # Download file
        request = drive_service.files().get_media(fileId=file_id)
        with io.FileIO(local_file_path, 'wb') as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloading: {file_name} - {int(status.progress() * 100)}% complete.")

    print("File download complete.")

# Execute the download task
list_and_download_files(FOLDER_ID, LOCAL_FOLDER)