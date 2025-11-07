import logging
import os
import json
from typing import Optional, List, Dict, Any, BinaryIO
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaInMemoryUpload
from dotenv import load_dotenv
import io

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """
    A manager class for interacting with Google Drive, providing reusable methods for common operations.
    """

    def __init__(self, credentials_file: Optional[str] = None):
        self.credentials_file = credentials_file or os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not self.credentials_file:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not set in .env")
        self.service = self._get_drive_service()

    def _get_drive_service(self):
        """Initialize and return the Google Drive service."""
        try:
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
            creds = service_account.Credentials.from_service_account_info(credentials)
            return build('drive', 'v3', credentials=creds)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error("Failed to load drive service credentials: %s", e)
            raise

    def list_files(self, folder_id: Optional[str] = None, query: Optional[str] = None, filetype: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in a folder or with a custom query."""
        try:
            q_parts = []
            if folder_id:
                q_parts.append(f"'{folder_id}' in parents")
            if filetype:
                q_parts.append(f"mimeType='{filetype}'")
            if query:
                q_parts.append(query)
            q = " and ".join(q_parts) if q_parts else None

            results = self.service.files().list(
                q=q,
                fields="files(id, name, mimeType, modifiedTime, size)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            return results.get('files', [])
        except Exception as e:
            logger.error("Error listing files: %s", e)
            raise

    def upload_file(self, file_path: str, folder_id: Optional[str] = None, file_name: Optional[str] = None) -> str:
        """Upload a file to Google Drive."""
        try:
            file_name = file_name or os.path.basename(file_path)
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            logger.info("Uploaded file %s with ID: %s", file_name, file.get('id'))
            return file.get('id')
        except Exception as e:
            logger.error("Error uploading file: %s", e)
            raise

    def create_file(self, name: str, content: str, folder_id: Optional[str] = None, mime_type: str = 'text/plain', public_share: bool = False) -> str:
        """Create a new file in Google Drive with the given content."""
        try:
            file_metadata = {'name': name}

            # If no folder_id provided, try to use a shared drive (required for service accounts)
            if not folder_id:
                shared_drives = self.list_shared_drives()
                if shared_drives:
                    folder_id = shared_drives[0]['id']
                    logger.info("Using shared drive '%s' for file creation", shared_drives[0]['name'])
                else:
                    raise ValueError("No shared drives available. Service accounts can only create files in shared drives.")

            file_metadata['parents'] = [folder_id]

            media = MediaInMemoryUpload(content.encode('utf-8'), mimetype=mime_type, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()

            file_id = file.get('id')
            logger.info("Created file %s with ID: %s", name, file_id)

            # Make file publicly accessible if requested
            if public_share:
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                self.service.permissions().create(
                    fileId=file_id,
                    body=permission,
                    supportsAllDrives=True
                ).execute()
                logger.info("Made file %s publicly accessible", name)

            return file_id
        except Exception as e:
            logger.error("Error creating file: %s", e)
            raise

    def download_file(self, file_id: str, local_path: str) -> None:
        """Download a file from Google Drive."""
        try:
            request = self.service.files().get_media(fileId=file_id)
            with io.FileIO(local_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    logger.info("Download %d%%.", int(status.progress() * 100))
            logger.info("Downloaded file to %s", local_path)
        except Exception as e:
            logger.error("Error downloading file: %s", e)
            raise

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> str:
        """Create a new folder in Google Drive."""
        try:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]

            file = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            logger.info("Created folder %s with ID: %s", name, file.get('id'))
            return file.get('id')
        except Exception as e:
            logger.error("Error creating folder: %s", e)
            raise

    def delete_file(self, file_id: str) -> None:
        """Delete a file or folder from Google Drive."""
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info("Deleted file/folder with ID: %s", file_id)
        except Exception as e:
            logger.error("Error deleting file: %s", e)
            raise

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a file."""
        try:
            file = self.service.files().get(fileId=file_id, fields='*').execute()
            return file
        except Exception as e:
            logger.error("Error getting file info: %s", e)
            raise

    def move_file(self, file_id: str, new_parent_id: str) -> None:
        """Move a file to a different folder."""
        try:
            # First, get the current parents
            file = self.service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents', []))

            # Move the file to the new folder
            self.service.files().update(
                fileId=file_id,
                addParents=new_parent_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            logger.info("Moved file %s to folder %s", file_id, new_parent_id)
        except Exception as e:
            logger.error("Error moving file: %s", e)
            raise

    def copy_file(self, file_id: str, name: Optional[str] = None, parent_id: Optional[str] = None) -> str:
        """Create a copy of a file."""
        try:
            copy_metadata = {}
            if name:
                copy_metadata['name'] = name
            if parent_id:
                copy_metadata['parents'] = [parent_id]

            copied_file = self.service.files().copy(
                fileId=file_id,
                body=copy_metadata,
                fields='id'
            ).execute()
            logger.info("Copied file to new ID: %s", copied_file.get('id'))
            return copied_file.get('id')
        except Exception as e:
            logger.error("Error copying file: %s", e)
            raise

    def list_shared_drives(self) -> List[Dict[str, Any]]:
        """List all shared drives accessible to the service account."""
        try:
            results = self.service.drives().list(
                fields="drives(id, name, createdTime)"
            ).execute()
            return results.get('drives', [])
        except Exception as e:
            logger.error("Error listing shared drives: %s", e)
            raise

    def list_shared_drive_files(self, drive_id: str) -> List[Dict[str, Any]]:
        """List all files in a specific shared drive."""
        try:
            results = self.service.files().list(
                q=f"'{drive_id}' in parents",
                fields="files(id, name, mimeType, modifiedTime, size)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora='drive',
                driveId=drive_id
            ).execute()
            return results.get('files', [])
        except Exception as e:
            logger.error("Error listing shared drive files: %s", e)
            raise