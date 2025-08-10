"""
Google Drive Cloud Provider Implementation
Implements the CloudProvider interface for Google Drive integration
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    import io
except ImportError as e:
    raise ImportError(f"Google API libraries not installed: {e}. Run 'pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib'")

from .base_provider import CloudProvider, AuthenticationError, UploadError, DownloadError, CloudProviderError
from ...config.settings import GOOGLE_DRIVE_SCOPES, CREDENTIALS_FILE

logger = logging.getLogger(__name__)


class GoogleDriveProvider(CloudProvider):
    """
    Google Drive implementation of the CloudProvider interface.
    
    Handles authentication, file upload/download, and folder management
    for Google Drive using the Google Drive API v3.
    """
    
    def __init__(self):
        super().__init__("Google Drive")
        self.service = None
        self.credentials = None
        self.scopes = GOOGLE_DRIVE_SCOPES
    
    def authenticate(self, credentials_path: Optional[Path] = None, **kwargs) -> bool:
        """
        Authenticate with Google Drive using OAuth 2.0.
        
        Args:
            credentials_path: Path to the Google API credentials JSON file
            **kwargs: Additional authentication parameters
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Use provided credentials path or default
            if credentials_path is None:
                # Look for credentials in config directory
                config_dir = Path(__file__).parent.parent.parent / "config"
                credentials_path = config_dir / "google_credentials.json"
            
            if not credentials_path.exists():
                raise AuthenticationError(f"Credentials file not found: {credentials_path}")
            
            # Check for existing token
            token_path = CREDENTIALS_FILE
            creds = None
            
            if token_path.exists():
                try:
                    creds = Credentials.from_authorized_user_file(str(token_path), self.scopes)
                    self.logger.debug("Loaded existing credentials from token file")
                except Exception as e:
                    self.logger.warning(f"Failed to load existing token: {e}")
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        self.logger.info("Refreshed expired credentials")
                    except Exception as e:
                        self.logger.warning(f"Failed to refresh credentials: {e}")
                        creds = None
                
                if not creds:
                    # Start OAuth flow
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path), self.scopes
                    )
                    creds = flow.run_local_server(port=8080)
                    self.logger.info("Completed OAuth authentication flow")
                
                # Save the credentials for the next run
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                self.logger.info(f"Saved credentials to {token_path}")
            
            # Build the service
            self.service = build('drive', 'v3', credentials=creds)
            self.credentials = creds
            self.is_authenticated = True
            
            # Test the connection
            user_info = self.get_user_info()
            self.logger.info(f"Successfully authenticated as {user_info.get('name', 'Unknown User')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            self.is_authenticated = False
            raise AuthenticationError(f"Google Drive authentication failed: {e}")
    
    def is_connected(self) -> bool:
        """Check if currently connected to Google Drive."""
        if not self.is_authenticated or not self.service:
            return False
        
        try:
            # Test connection with a simple API call
            self.service.about().get(fields="user").execute()
            return True
        except Exception as e:
            self.logger.warning(f"Connection test failed: {e}")
            self.is_authenticated = False
            return False
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get information about the authenticated user."""
        if not self.is_connected():
            raise CloudProviderError("Not connected to Google Drive")
        
        try:
            # Get user info
            about = self.service.about().get(fields="user,storageQuota").execute()
            user = about.get('user', {})
            storage = about.get('storageQuota', {})
            
            return {
                'name': user.get('displayName', 'Unknown'),
                'email': user.get('emailAddress', 'Unknown'),
                'photo_url': user.get('photoLink'),
                'storage_used': int(storage.get('usage', 0)),
                'storage_limit': int(storage.get('limit', 0)),
                'storage_used_in_drive': int(storage.get('usageInDrive', 0))
            }
        except HttpError as e:
            raise CloudProviderError(f"Failed to get user info: {e}")
    
    def create_folder(self, folder_path: str, parent_id: Optional[str] = None) -> str:
        """Create a folder in Google Drive."""
        if not self.is_connected():
            raise CloudProviderError("Not connected to Google Drive")
        
        try:
            folder_metadata = {
                'name': folder_path,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                folder_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            self.logger.info(f"Created folder '{folder_path}' with ID: {folder_id}")
            return folder_id
            
        except HttpError as e:
            raise CloudProviderError(f"Failed to create folder '{folder_path}': {e}")
    
    def upload_file(self, local_path: Path, remote_path: str, 
                   parent_id: Optional[str] = None, 
                   progress_callback: Optional[callable] = None) -> str:
        """Upload a file to Google Drive."""
        if not self.is_connected():
            raise CloudProviderError("Not connected to Google Drive")
        
        if not local_path.exists():
            raise UploadError(f"Local file does not exist: {local_path}")
        
        try:
            file_metadata = {'name': remote_path}
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            # Determine MIME type based on file extension
            mime_type = self._get_mime_type(local_path)
            
            media = MediaFileUpload(
                str(local_path),
                mimetype=mime_type,
                resumable=True
            )
            
            request = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status and progress_callback:
                    progress_callback(status.resumable_progress, local_path.stat().st_size)
            
            file_id = response.get('id')
            self.logger.info(f"Uploaded '{local_path.name}' as '{remote_path}' with ID: {file_id}")
            return file_id
            
        except HttpError as e:
            raise UploadError(f"Failed to upload '{local_path}': {e}")
        except Exception as e:
            raise UploadError(f"Unexpected error uploading '{local_path}': {e}")
    
    def download_file(self, file_id: str, local_path: Path,
                     progress_callback: Optional[callable] = None) -> bool:
        """Download a file from Google Drive."""
        if not self.is_connected():
            raise CloudProviderError("Not connected to Google Drive")
        
        try:
            # Get file metadata first
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', 'unknown')
            
            # Create parent directories if they don't exist
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the file
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status and progress_callback:
                    progress_callback(status.resumable_progress * 100, 100)
            
            # Write to local file
            with open(local_path, 'wb') as f:
                f.write(fh.getvalue())
            
            self.logger.info(f"Downloaded '{file_name}' to '{local_path}'")
            return True
            
        except HttpError as e:
            raise DownloadError(f"Failed to download file ID '{file_id}': {e}")
        except Exception as e:
            raise DownloadError(f"Unexpected error downloading file ID '{file_id}': {e}")
    
    def list_files(self, folder_id: Optional[str] = None, 
                  folder_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in a Google Drive folder."""
        if not self.is_connected():
            raise CloudProviderError("Not connected to Google Drive")
        
        try:
            # Build query
            query = ""
            if folder_id:
                query = f"'{folder_id}' in parents"
            elif folder_path:
                # Find folder by path first
                folder_id = self.find_folder(folder_path)
                if folder_id:
                    query = f"'{folder_id}' in parents"
                else:
                    return []  # Folder not found
            
            # Add trashed filter
            if query:
                query += " and trashed=false"
            else:
                query = "trashed=false"
            
            results = self.service.files().list(
                q=query,
                fields="files(id,name,mimeType,size,modifiedTime,parents)"
            ).execute()
            
            files = results.get('files', [])
            
            # Convert to standard format
            file_list = []
            for file in files:
                file_info = {
                    'id': file['id'],
                    'name': file['name'],
                    'type': 'folder' if file['mimeType'] == 'application/vnd.google-apps.folder' else 'file',
                    'size': int(file.get('size', 0)) if file.get('size') else 0,
                    'modified_time': file.get('modifiedTime'),
                    'mime_type': file.get('mimeType')
                }
                file_list.append(file_info)
            
            return file_list
            
        except HttpError as e:
            raise CloudProviderError(f"Failed to list files: {e}")
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive."""
        if not self.is_connected():
            raise CloudProviderError("Not connected to Google Drive")
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            self.logger.info(f"Deleted file with ID: {file_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Failed to delete file ID '{file_id}': {e}")
            return False
    
    def find_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Find a folder by name in Google Drive."""
        if not self.is_connected():
            raise CloudProviderError("Not connected to Google Drive")
        
        try:
            # Build query
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id,name)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                folder_id = files[0]['id']
                self.logger.debug(f"Found folder '{folder_name}' with ID: {folder_id}")
                return folder_id
            
            return None
            
        except HttpError as e:
            self.logger.error(f"Failed to find folder '{folder_name}': {e}")
            return None
    
    def get_storage_info(self) -> Dict[str, int]:
        """Get Google Drive storage quota information."""
        if not self.is_connected():
            raise CloudProviderError("Not connected to Google Drive")
        
        try:
            about = self.service.about().get(fields="storageQuota").execute()
            storage = about.get('storageQuota', {})
            
            used = int(storage.get('usage', 0))
            limit = int(storage.get('limit', 0))
            
            return {
                'used': used,
                'total': limit,
                'available': max(0, limit - used) if limit > 0 else 0
            }
            
        except HttpError as e:
            raise CloudProviderError(f"Failed to get storage info: {e}")
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Determine MIME type based on file extension."""
        extension = file_path.suffix.lower()
        
        mime_types = {
            '.json': 'application/json',
            '.txt': 'text/plain',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            '.zip': 'application/zip',
            '.tar.gz': 'application/gzip',
            '.log': 'text/plain'
        }
        
        # Handle compound extensions
        if file_path.name.endswith('.tar.gz'):
            return mime_types['.tar.gz']
        
        return mime_types.get(extension, 'application/octet-stream')
    
    def find_file_by_name(self, file_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Find a file by name in Google Drive."""
        if not self.is_connected():
            raise CloudProviderError("Not connected to Google Drive")
        
        try:
            # Build query
            query = f"name='{file_name}' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id,name)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                file_id = files[0]['id']
                self.logger.debug(f"Found file '{file_name}' with ID: {file_id}")
                return file_id
            
            return None
            
        except HttpError as e:
            self.logger.error(f"Failed to find file '{file_name}': {e}")
            return None
