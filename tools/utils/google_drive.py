import os
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from tools.common.messenger import Messenger

class GoogleDriveTool:
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        # Check if we already have an OAuth token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)
            
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif self.credentials_path.exists():
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.SCOPES)
                # This will open a browser window for authentication
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(str(self.token_path), 'w') as token:
                    token.write(creds.to_json())
            else:
                raise FileNotFoundError(f"Missing {self.credentials_path} file for Google Drive API. Please create one in Google Cloud Console.")

        return build('drive', 'v3', credentials=creds)

    def find_file(self, name: str, folder_id: str = None) -> list:
        """Searches for files by name in a specific folder."""
        query = f"name = '{name}' and trashed = false"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        return results.get('files', [])

    def upload_file(self, file_path: Path, mime_type: str, folder_id: str = None, display_name: str = None) -> str:
        """Uploads a file to Google Drive and returns the File ID."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        name = display_name if display_name else file_path.name
        
        # Check for duplicates
        existing_files = self.find_file(name, folder_id)
        if existing_files:
            Messenger.warning(f"File '{name}' already exists on Drive (ID: {existing_files[0]['id']}). Skipping upload.")
            return existing_files[0]['id']

        file_metadata = {'name': name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)

        Messenger.info(f"Uploading {file_path.name} to Google Drive...")
        
        file = self.service.files().create(
            body=file_metadata, 
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        Messenger.success(f"File uploaded successfully! Link: {file.get('webViewLink')}")
        return file.get('id')
