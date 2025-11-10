"""
Google Drive service module for handling Drive API operations.
"""

import os
import time
import json
from typing import Dict, List, Optional, Tuple

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io

from fastapi import HTTPException

# Constants
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]

# Add common image MIME types
IMAGE_MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "svg": "image/svg+xml",
    "bmp": "image/bmp",
    "tiff": "image/tiff",
    "tif": "image/tiff",
}


class DriveService:
    """Class for handling Google Drive operations."""

    def __init__(
        self,
        token_file: str,
        client_secret_file: str,
        drive_root_id: str,
        cache_file: str,
        cache_ttl: int = 600,
    ):
        self.token_file = token_file
        self.client_secret_file = client_secret_file
        self.drive_root_id = drive_root_id
        self.cache_file = cache_file
        self.cache_ttl = cache_ttl
        self.folder_cache = []
        self.cache_last_update = 0

    def get_drive_service(self):
        """Initialize and return an authenticated Drive service."""
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        # If credentials don't exist or are invalid, user must authorize
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(GoogleRequest())
                with open(self.token_file, "w") as token:
                    token.write(creds.to_json())
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Google Drive není autorizován. Navštivte /authorize.",
                )
        return build("drive", "v3", credentials=creds)

    def create_auth_url(self, redirect_uri: str) -> tuple:
        """Create OAuth authorization URL."""
        flow = Flow.from_client_secrets_file(
            self.client_secret_file,
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )
        auth_url, state = flow.authorization_url(
            prompt="consent", access_type="offline", include_granted_scopes="true"
        )
        return auth_url, state

    def fetch_token(self, code: str, redirect_uri: str) -> None:
        """Fetch and save OAuth token."""
        flow = Flow.from_client_secrets_file(
            self.client_secret_file,
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open(self.token_file, "w") as token:
            token.write(creds.to_json())

    def save_cache_to_file(self) -> None:
        """Save the folder cache to a local JSON file."""
        try:
            cache_data = {
                "folders": self.folder_cache,
                "last_update": self.cache_last_update,
            }
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"[INFO] Folder cache saved to {self.cache_file}")
        except Exception as e:
            print(f"[ERROR] Failed to save folder cache to file: {e}")

    def load_cache_from_file(self) -> bool:
        """Load the folder cache from a local JSON file.

        Returns:
            bool: True if cache was successfully loaded and is still valid, False otherwise.
        """
        if not os.path.exists(self.cache_file):
            return False

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            last_update = cache_data.get("last_update", 0)
            folders = cache_data.get("folders", [])

            # Check if cache is still valid
            if int(time.time()) - last_update <= self.cache_ttl and folders:
                self.folder_cache = folders
                self.cache_last_update = last_update
                print(
                    f"[INFO] Loaded folder cache from file: {len(self.folder_cache)} folders"
                )
                return True
            else:
                print(f"[INFO] Cached folder data expired or empty")
                return False

        except Exception as e:
            print(f"[ERROR] Failed to load folder cache from file: {e}")
            return False

    def fetch_folders_from_drive(self) -> List[Dict[str, str]]:
        """Fetch all folders and their paths from Google Drive, including ID."""
        service = self.get_drive_service()
        folders: Dict[str, Dict] = {}
        paths: Dict[str, str] = {}
        page_token = None

        # 1. Get all folders
        while True:
            results = (
                service.files()
                .list(
                    q=f"mimeType='application/vnd.google-apps.folder' and trashed=false",
                    spaces="drive",
                    fields="nextPageToken, files(id, name, parents)",
                    pageToken=page_token,
                )
                .execute()
            )
            for f in results.get("files", []):
                folders[f["id"]] = {"name": f["name"], "parents": f.get("parents", [])}
            page_token = results.get("nextPageToken", None)
            if not page_token:
                break

        # 2. Recursively build paths
        def build_path(folder_id: str) -> str:
            if folder_id in paths:
                return paths[folder_id]
            folder = folders[folder_id]
            if not folder["parents"]:
                paths[folder_id] = f"/{folder['name']}"
                return paths[folder_id]
            parent_id = folder["parents"][0]
            if parent_id not in folders:
                paths[folder_id] = f"/{folder['name']}"
                return paths[folder_id]
            parent_path = build_path(parent_id)
            paths[folder_id] = f"{parent_path}/{folder['name']}"
            return paths[folder_id]

        all_folders = []
        for folder_id in folders:
            path = build_path(folder_id)
            if self.drive_root_id in path and "/." not in path:
                all_folders.append({"path": path, "id": folder_id})
        return sorted(all_folders, key=lambda x: x["path"])

    def update_folder_cache(self) -> None:
        """Update the folder cache from Drive API."""
        try:
            self.folder_cache = self.fetch_folders_from_drive()
            self.cache_last_update = int(time.time())
            print(f"[INFO] Folders cache updated: {len(self.folder_cache)} folders.")
            # Save the updated cache to file
            self.save_cache_to_file()
        except Exception as e:
            print(f"[ERROR] Failed to update folder cache: {e}")

    def ensure_cache(self) -> None:
        """Ensure the cache is loaded and up-to-date."""
        # Try to load from file if cache is empty or expired
        if not self.folder_cache or (
            int(time.time()) - self.cache_last_update > self.cache_ttl
        ):
            if not self.load_cache_from_file():
                # If loading from file failed or cache is expired, fetch from Drive
                self.update_folder_cache()

    def find_folder_id_by_path(self, folder_path: str) -> Optional[str]:
        """Find folder ID by its path (e.g. /A/B/C)."""
        service = self.get_drive_service()
        parts = [p for p in folder_path.strip("/").split("/") if p]
        parent_id = "root"
        for part in parts:
            query = f"name='{part}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
            results = (
                service.files()
                .list(q=query, spaces="drive", fields="files(id, name)")
                .execute()
            )
            files = results.get("files", [])
            if not files:
                return None
            parent_id = files[0]["id"]
        return parent_id

    def find_file_in_folder(self, folder_id: str, filename: str) -> Optional[str]:
        """Find a file in a specific folder by name."""
        service = self.get_drive_service()
        query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        results = (
            service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )
        files = results.get("files", [])
        if files:
            return files[0]["id"]
        return None

    def append_text_to_drive_file(self, file_id: str, text: str) -> None:
        """Append text to an existing Drive file."""
        service = self.get_drive_service()

        # Download content
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        content = fh.getvalue().decode("utf-8")

        # Add text
        new_content = content + "\n" + text

        # Upload
        media_body = MediaIoBaseUpload(
            io.BytesIO(new_content.encode("utf-8")), mimetype="text/markdown"
        )
        service.files().update(fileId=file_id, media_body=media_body).execute()

    def create_file_in_folder(self, folder_id: str, filename: str, text: str) -> str:
        """Create a new file in a specific folder."""
        service = self.get_drive_service()
        file_metadata = {
            "name": filename,
            "parents": [folder_id],
            "mimeType": "text/markdown",
        }

        media_body = MediaIoBaseUpload(
            io.BytesIO(text.encode("utf-8")), mimetype="text/markdown"
        )
        file = (
            service.files()
            .create(body=file_metadata, media_body=media_body, fields="id")
            .execute()
        )
        return file["id"]

    def save_image_to_drive(
        self,
        folder_id: str,
        image_data: bytes,
        filename: str,
        content_type: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Save an image file to Google Drive.

        Args:
            folder_id: ID of the folder to save the image in
            image_data: Binary image data
            filename: Original filename of the image
            content_type: MIME type of the image, or None to detect from extension

        Returns:
            Tuple of (file_id, web_view_link) where web_view_link is URL to view the image
        """
        service = self.get_drive_service()

        # If no content type provided, try to detect from filename extension
        if not content_type:
            extension = filename.split(".")[-1].lower() if "." in filename else ""
            content_type = IMAGE_MIME_TYPES.get(extension, "application/octet-stream")

        file_metadata = {
            "name": filename,
            "parents": [folder_id],
        }

        media_body = MediaIoBaseUpload(
            io.BytesIO(image_data), mimetype=content_type, resumable=True
        )

        file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media_body,
                fields="id,webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )

        return file["id"], file.get("webViewLink", "")
