import logging
import os
import json
from typing import Optional, List, Dict, Any
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from ratelimit import limits, sleep_and_retry, RateLimitException
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """
    A manager class for interacting with Google Sheets, providing reusable methods for common operations.
    """
    
    def __init__(self, credentials_file: Optional[str] = None):
        self.credentials_file = credentials_file or os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not self.credentials_file:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not set in .env")
        self.gc = self._get_gspread_client()
        self.drive_service = self._get_drive_service()
    
    def _get_gspread_client(self) -> gspread.Client:
        """Initialize and return the gspread client."""
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            return gspread.service_account_from_dict(credentials)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load credentials: {e}")
            raise
    
    def _get_drive_service(self):
        """Initialize and return the Google Drive service."""
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            creds = service_account.Credentials.from_service_account_info(credentials)
            return build('drive', 'v3', credentials=creds)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load drive service credentials: {e}")
            raise
    
    def get_worksheet(self, sheet_id: Optional[str] = None, file_name: Optional[str] = None, sheet_name: str = "Sheet1") -> gspread.Worksheet:
        """Retrieve a worksheet by ID or name."""
        if sheet_id:
            sheet = self.gc.open_by_key(sheet_id).worksheet(sheet_name)
            logger.info(f"Using sheet ID {sheet_id}, sheet name {sheet_name}")
        elif file_name:
            sheet = self.gc.open(file_name).worksheet(sheet_name)
            logger.info(f"Using file name {file_name}, sheet name {sheet_name}")
        else:
            raise ValueError("Either sheet_id or file_name must be provided.")
        return sheet
    
    def sheet_df(self, sheet_id: Optional[str] = None, file_name: Optional[str] = None, sheet_name: str = "Sheet1") -> pd.DataFrame:
        """Retrieve the contents of a Google Sheet as a pandas DataFrame."""
        try:
            sheet = self.get_worksheet(sheet_id, file_name, sheet_name)
            df = get_as_dataframe(sheet, evaluate_formulas=True, header=0)
            return df.dropna(how='all')  # Clean empty rows
        except Exception as e:
            logger.error(f"Error retrieving DataFrame: {e}")
            raise
    
    @sleep_and_retry
    @limits(calls=3, period=60)
    def append_to_sheet(self, df: pd.DataFrame, sheet_id: Optional[str] = None, file_name: Optional[str] = None, sheet_name: str = "Sheet1") -> None:
        """Append a DataFrame to the end of the sheet."""
        if df.empty:
            logger.warning("DataFrame is empty; nothing to append.")
            return
        try:
            sheet = self.get_worksheet(sheet_id, file_name, sheet_name)
            last_row = len(sheet.get_all_values())
            set_with_dataframe(sheet, df, row=last_row + 1, include_index=False, include_column_header=False)
            logger.info(f"Appended {len(df)} rows to sheet.")
        except gspread.exceptions.APIError as e:
            logger.error(f"APIError during append: {e}")
            raise RateLimitException("Rate limit exceeded", 60) from e
        except Exception as e:
            logger.error(f"Unexpected error during append: {e}")
            raise
    
    @sleep_and_retry
    @limits(calls=2, period=60)
    def df_to_sheet(self, df: pd.DataFrame, sheet_id: Optional[str] = None, file_name: Optional[str] = None, sheet_name: str = "Sheet1") -> None:
        """Write the entire DataFrame to the sheet, replacing its contents."""
        try:
            sheet = self.get_worksheet(sheet_id, file_name, sheet_name)
            sheet.clear()
            set_with_dataframe(sheet, df, include_index=False, include_column_header=True)
            logger.info(f"Wrote {len(df)} rows to sheet, replacing contents.")
        except gspread.exceptions.APIError as e:
            logger.error(f"APIError during write: {e}")
            raise RateLimitException("Rate limit exceeded", 60) from e
        except Exception as e:
            logger.error(f"Unexpected error during write: {e}")
            raise
    
    def insert_key_value(self, key: str, value: Any, sheet_id: Optional[str] = None, file_name: Optional[str] = None, sheet_name: str = "Sheet1") -> None:
        """Insert or update a key-value pair in the sheet."""
        try:
            sheet = self.get_worksheet(sheet_id, file_name, sheet_name)
            cell = sheet.find(str(key))
            if cell:
                sheet.update_cell(cell.row, 2, value)
                logger.info(f"Updated key '{key}' with value '{value}' at row {cell.row}")
            else:
                sheet.append_row([key, value])
                logger.info(f"Inserted new key '{key}' with value '{value}'")
        except Exception as e:
            logger.error(f"Error inserting key-value: {e}")
            raise
    
    def list_sheets(self) -> List[Dict[str, str]]:
        """List all spreadsheets in the Google account."""
        try:
            spreadsheets = self.gc.openall()
            return [{'id': s.id, 'title': s.title} for s in spreadsheets]
        except Exception as e:
            logger.error(f"Error listing sheets: {e}")
            raise

    def list_shared_drive_sheets(self, drive_id: str) -> List[Dict[str, str]]:
        """List all spreadsheets in the specified shared drive."""
        try:
            from .drive import GoogleDriveManager
            drive_manager = GoogleDriveManager(self.credentials_file)
            files = drive_manager.list_files(
                folder_id=drive_id, 
                filetype='application/vnd.google-apps.spreadsheet'
            )
            return [{'id': f['id'], 'title': f['name']} for f in files]
        except Exception as e:
            logger.error(f"Error listing shared drive sheets: {e}")
            raise

    def create_spreadsheet(self, title: str, folder_id: Optional[str] = None, public_share: bool = False) -> str:
        """Create a new Google Spreadsheet."""
        try:
            # Determine the target folder/drive
            target_folder_id = folder_id
            if not target_folder_id:
                # If no folder_id provided, try to use a shared drive (required for service accounts)
                from .drive import GoogleDriveManager
                drive_manager = GoogleDriveManager(self.credentials_file)
                shared_drives = drive_manager.list_shared_drives()
                if shared_drives:
                    target_folder_id = shared_drives[0]['id']
                    logger.info(f"Using shared drive '{shared_drives[0]['name']}' for spreadsheet creation")
                else:
                    raise ValueError("No shared drives available. Service accounts can only create spreadsheets in shared drives.")

            # Create spreadsheet directly in Drive using Drive API
            from .drive import GoogleDriveManager
            drive_manager = GoogleDriveManager(self.credentials_file)

            file_metadata = {
                'name': title,
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [target_folder_id]
            }

            file = drive_manager.service.files().create(
                body=file_metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()

            spreadsheet_id = file.get('id')
            logger.info(f"Created spreadsheet '{title}' with ID: {spreadsheet_id}")

            # Make publicly accessible if requested
            if public_share:
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                drive_manager.service.permissions().create(
                    fileId=spreadsheet_id,
                    body=permission,
                    supportsAllDrives=True
                ).execute()
                logger.info(f"Made spreadsheet '{title}' publicly accessible")

            return spreadsheet_id
        except Exception as e:
            logger.error(f"Error creating spreadsheet: {e}")
            raise