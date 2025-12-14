from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io
import os
import time

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
FOLDER_ID = "1TsuB2vWHVOgwWiSjBbUBtysHXkkZYQN4"
DOWNLOAD_DIR = "./Athletes"
SKIP_ATHLETES = {
    "Arlen Peters"
}

creds = Credentials.from_service_account_file(
    "credentials.json", scopes=SCOPES
)

service = build("drive", "v3", credentials=creds)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_csv_only(file_id, file_name, local_path, mime_type):
    # Google Sheets → export to CSV
    if mime_type == "application/vnd.google-apps.spreadsheet":
        local_path = local_path + ".csv"
        request = service.files().export_media(
            fileId=file_id,
            mimeType="text/csv"
        )

    # Native CSV files
    elif file_name.lower().endswith(".csv"):
        request = service.files().get_media(
            fileId=file_id,
            supportsAllDrives=True
        )

    # Everything else → skip
    else:
        print(f"Skipping non-CSV file: {file_name}")
        return

    fh = io.FileIO(local_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"  {file_name}: {int(status.progress() * 100)}%")


def download_folder(folder_id, local_path, drive_id=None, depth=0, target_root=None):
    """
    depth = 0 → shared root
    depth = 1 → athlete folder (ignored)
    depth = 2 → inner folder (local root)
    depth >=3 → flattened
    """

    # At inner-folder level, lock in the local root
    if depth == 2:
        target_root = local_path
        os.makedirs(target_root, exist_ok=True)

    page_token = None

    while True:
        try:
            response = service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="nextPageToken, files(id, name, mimeType)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora="drive" if drive_id else "allDrives",
                driveId=drive_id,
                pageSize=1000,
                pageToken=page_token
            ).execute()

            for item in response.get("files", []):

                if item["mimeType"] == "application/vnd.google-apps.folder":
                    # Skip specific athletes
                    if depth == 1 and item["name"] in SKIP_ATHLETES:
                        print(f"Skipping athlete folder: {item['name']}")
                        continue
                    
                    # Only create local folder at depth 2
                    next_local = (
                        os.path.join(local_path, item["name"])
                        if depth == 1 else local_path
                    )

                    download_folder(
                        item["id"],
                        next_local,
                        drive_id,
                        depth + 1,
                        target_root
                    )

                else:
                    # Write CSVs into target_root
                    if target_root is None:
                        continue

                    download_csv_only(
                        item["id"],
                        item["name"],
                        os.path.join(target_root, item["name"]),
                        item["mimeType"]
                    )

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                print("Drive API internal error — retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise

# -------- RUN --------
download_folder(FOLDER_ID, DOWNLOAD_DIR)
