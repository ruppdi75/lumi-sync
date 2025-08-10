"""
pCloud Provider Implementation
Implements the CloudProvider interface for pCloud integration
"""

import json
import os
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import hashlib
import time

from .base_provider import CloudProvider, AuthenticationError, UploadError, DownloadError, CloudProviderError

logger = logging.getLogger(__name__)


class PCloudProvider(CloudProvider):
    """
    pCloud implementation of the CloudProvider interface.
    
    Handles authentication, file upload/download, and folder management
    for pCloud using the pCloud API.
    """
    
    def __init__(self):
        super().__init__("pCloud")
        self.api_base = "https://api.pcloud.com"
        self.auth_token = None
        self.user_info = None
        self.lumisync_folder_id = None
    
    def authenticate(self, credentials_path: Optional[Path] = None, **kwargs) -> bool:
        """
        Authenticate with pCloud using username and password.
        
        Args:
            credentials_path: Path to credentials file (optional)
            **kwargs: Should contain 'username' and 'password'
            
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            username = kwargs.get('username')
            password = kwargs.get('password')
            
            if not username or not password:
                # Try to load from credentials file
                if credentials_path and credentials_path.exists():
                    with open(credentials_path, 'r') as f:
                        creds = json.load(f)
                        username = creds.get('username')
                        password = creds.get('password')
                
                if not username or not password:
                    raise AuthenticationError("Username and password are required for pCloud authentication")
            
            # pCloud uses digest authentication
            response = requests.get(f"{self.api_base}/userinfo", params={
                'username': username,
                'password': password
            })
            
            if response.status_code != 200:
                raise AuthenticationError(f"HTTP error: {response.status_code}")
            
            data = response.json()
            
            if data.get('result') != 0:
                error_msg = data.get('error', 'Unknown authentication error')
                raise AuthenticationError(f"pCloud authentication failed: {error_msg}")
            
            self.auth_token = data.get('auth')
            self.user_info = data
            self.is_authenticated = True
            
            # Create Lumi-Sync folder if it doesn't exist
            self._ensure_lumisync_folder()
            
            logger.info(f"Successfully authenticated with pCloud as {username}")
            return True
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Network error during pCloud authentication: {str(e)}")
        except Exception as e:
            logger.error(f"pCloud authentication error: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def _ensure_lumisync_folder(self):
        """Create Lumi-Sync folder if it doesn't exist"""
        try:
            # Check if Lumi-Sync folder exists
            response = requests.get(f"{self.api_base}/listfolder", params={
                'auth': self.auth_token,
                'folderid': 0,  # Root folder
                'nofiles': 1    # Only get folders
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 0:
                    folders = data.get('metadata', {}).get('contents', [])
                    for folder in folders:
                        if folder.get('name') == 'Lumi-Sync' and folder.get('isfolder'):
                            self.lumisync_folder_id = folder.get('folderid')
                            logger.info("Found existing Lumi-Sync folder")
                            return
            
            # Create Lumi-Sync folder if it doesn't exist
            response = requests.get(f"{self.api_base}/createfolder", params={
                'auth': self.auth_token,
                'folderid': 0,  # Root folder
                'name': 'Lumi-Sync'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 0:
                    self.lumisync_folder_id = data.get('metadata', {}).get('folderid')
                    logger.info("Created Lumi-Sync folder successfully")
                else:
                    logger.warning(f"Failed to create Lumi-Sync folder: {data.get('error')}")
            
        except Exception as e:
            logger.error(f"Error ensuring Lumi-Sync folder: {str(e)}")
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get authenticated user information.
        
        Returns:
            Dictionary containing user information
        """
        if not self.is_authenticated or not self.user_info:
            raise AuthenticationError("Not authenticated with pCloud")
        
        return {
            'email': self.user_info.get('email', 'Unknown'),
            'name': f"{self.user_info.get('firstname', '')} {self.user_info.get('lastname', '')}".strip(),
            'storage_used': self.user_info.get('usedquota', 0),
            'storage_total': self.user_info.get('quota', 0)
        }
    
    def upload_file(self, local_path: Path, remote_path: str, 
                   progress_callback: Optional[callable] = None) -> str:
        """
        Upload a file to pCloud.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path (relative to Lumi-Sync folder)
            progress_callback: Optional callback for progress updates
            
        Returns:
            File ID of uploaded file
            
        Raises:
            UploadError: If upload fails
        """
        if not self.is_authenticated:
            raise UploadError("Not authenticated with pCloud")
        
        if not local_path.exists():
            raise UploadError(f"Local file does not exist: {local_path}")
        
        try:
            # Use Lumi-Sync folder as base
            folder_id = self.lumisync_folder_id or 0
            
            # Create subdirectories if needed
            if '/' in remote_path:
                folder_path = '/'.join(remote_path.split('/')[:-1])
                folder_id = self._create_folder_path(folder_path, folder_id)
            
            filename = remote_path.split('/')[-1]
            
            # Upload file
            with open(local_path, 'rb') as f:
                files = {'file': (filename, f, 'application/octet-stream')}
                data = {
                    'auth': self.auth_token,
                    'folderid': folder_id,
                    'filename': filename
                }
                
                response = requests.post(f"{self.api_base}/uploadfile", 
                                       data=data, files=files)
            
            if response.status_code != 200:
                raise UploadError(f"HTTP error: {response.status_code}")
            
            result = response.json()
            if result.get('result') != 0:
                error_msg = result.get('error', 'Unknown upload error')
                raise UploadError(f"pCloud upload failed: {error_msg}")
            
            file_id = result.get('metadata', [{}])[0].get('fileid')
            logger.info(f"Successfully uploaded {local_path} to pCloud")
            return str(file_id)
            
        except requests.RequestException as e:
            raise UploadError(f"Network error during upload: {str(e)}")
        except Exception as e:
            logger.error(f"pCloud upload error: {str(e)}")
            raise UploadError(f"Upload failed: {str(e)}")
    
    def download_file(self, remote_path: str, local_path: Path,
                     progress_callback: Optional[callable] = None) -> bool:
        """
        Download a file from pCloud.
        
        Args:
            remote_path: Remote file path (relative to Lumi-Sync folder)
            local_path: Local destination path
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if download successful
            
        Raises:
            DownloadError: If download fails
        """
        if not self.is_authenticated:
            raise DownloadError("Not authenticated with pCloud")
        
        try:
            # Find file by path
            file_info = self._find_file_by_path(remote_path)
            if not file_info:
                raise DownloadError(f"File not found: {remote_path}")
            
            file_id = file_info.get('fileid')
            
            # Get download link
            response = requests.get(f"{self.api_base}/getfilelink", params={
                'auth': self.auth_token,
                'fileid': file_id
            })
            
            if response.status_code != 200:
                raise DownloadError(f"HTTP error: {response.status_code}")
            
            result = response.json()
            if result.get('result') != 0:
                error_msg = result.get('error', 'Unknown error')
                raise DownloadError(f"Failed to get download link: {error_msg}")
            
            download_url = f"https://{result.get('hosts')[0]}{result.get('path')}"
            
            # Download file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Successfully downloaded {remote_path} from pCloud")
            return True
            
        except requests.RequestException as e:
            raise DownloadError(f"Network error during download: {str(e)}")
        except Exception as e:
            logger.error(f"pCloud download error: {str(e)}")
            raise DownloadError(f"Download failed: {str(e)}")
    
    def list_files(self, remote_path: str = "") -> List[Dict[str, Any]]:
        """
        List files in a remote directory.
        
        Args:
            remote_path: Remote directory path (relative to Lumi-Sync folder)
            
        Returns:
            List of file information dictionaries
        """
        if not self.is_authenticated:
            raise CloudProviderError("Not authenticated with pCloud")
        
        try:
            folder_id = self.lumisync_folder_id or 0
            
            if remote_path:
                folder_info = self._find_folder_by_path(remote_path)
                if folder_info:
                    folder_id = folder_info.get('folderid')
                else:
                    return []
            
            response = requests.get(f"{self.api_base}/listfolder", params={
                'auth': self.auth_token,
                'folderid': folder_id
            })
            
            if response.status_code != 200:
                raise CloudProviderError(f"HTTP error: {response.status_code}")
            
            result = response.json()
            if result.get('result') != 0:
                error_msg = result.get('error', 'Unknown error')
                raise CloudProviderError(f"Failed to list files: {error_msg}")
            
            files = []
            contents = result.get('metadata', {}).get('contents', [])
            
            for item in contents:
                if not item.get('isfolder'):
                    files.append({
                        'name': item.get('name'),
                        'size': item.get('size', 0),
                        'modified': item.get('modified'),
                        'id': item.get('fileid')
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"pCloud list files error: {str(e)}")
            raise CloudProviderError(f"Failed to list files: {str(e)}")
    
    def delete_file(self, remote_path: str) -> bool:
        """
        Delete a file from pCloud.
        
        Args:
            remote_path: Remote file path (relative to Lumi-Sync folder)
            
        Returns:
            True if deletion successful
        """
        if not self.is_authenticated:
            raise CloudProviderError("Not authenticated with pCloud")
        
        try:
            file_info = self._find_file_by_path(remote_path)
            if not file_info:
                logger.warning(f"File not found for deletion: {remote_path}")
                return True  # Consider it successful if file doesn't exist
            
            file_id = file_info.get('fileid')
            
            response = requests.get(f"{self.api_base}/deletefile", params={
                'auth': self.auth_token,
                'fileid': file_id
            })
            
            if response.status_code != 200:
                raise CloudProviderError(f"HTTP error: {response.status_code}")
            
            result = response.json()
            if result.get('result') != 0:
                error_msg = result.get('error', 'Unknown error')
                raise CloudProviderError(f"Failed to delete file: {error_msg}")
            
            logger.info(f"Successfully deleted {remote_path} from pCloud")
            return True
            
        except Exception as e:
            logger.error(f"pCloud delete error: {str(e)}")
            raise CloudProviderError(f"Failed to delete file: {str(e)}")
    
    def create_folder(self, folder_path: str) -> str:
        """Create a folder in pCloud.
        
        Args:
            folder_path: Folder path (relative to Lumi-Sync folder)
            
        Returns:
            Folder ID of created folder
        """
        if not self.is_authenticated:
            raise CloudProviderError("Not authenticated with pCloud")
        
        try:
            parent_id = self.lumisync_folder_id or 0
            folder_id = self._create_folder_path(folder_path, parent_id)
            return str(folder_id)
            
        except Exception as e:
            logger.error(f"pCloud create folder error: {str(e)}")
            raise CloudProviderError(f"Failed to create folder: {str(e)}")
    
    def find_folder(self, folder_path: str) -> Optional[str]:
        """Find a folder by path.
        
        Args:
            folder_path: Folder path (relative to Lumi-Sync folder)
            
        Returns:
            Folder ID if found, None otherwise
        """
        if not self.is_authenticated:
            raise CloudProviderError("Not authenticated with pCloud")
        
        try:
            folder_info = self._find_folder_by_path(folder_path)
            return str(folder_info.get('folderid')) if folder_info else None
            
        except Exception as e:
            logger.error(f"pCloud find folder error: {str(e)}")
            return None
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information.
        
        Returns:
            Dictionary with storage information
        """
        if not self.is_authenticated or not self.user_info:
            raise CloudProviderError("Not authenticated with pCloud")
        
        return {
            'used': self.user_info.get('usedquota', 0),
            'total': self.user_info.get('quota', 0),
            'available': self.user_info.get('quota', 0) - self.user_info.get('usedquota', 0)
        }
    
    def is_connected(self) -> bool:
        """Check if connected to pCloud.
        
        Returns:
            True if connected, False otherwise
        """
        return self.is_authenticated and self.auth_token is not None
    
    def _create_folder_path(self, folder_path: str, parent_id: int) -> int:
        """Create folder path recursively and return final folder ID"""
        if not folder_path:
            return parent_id
        
        parts = folder_path.split('/')
        current_id = parent_id
        
        for part in parts:
            if not part:
                continue
            
            # Check if folder exists
            response = requests.get(f"{self.api_base}/listfolder", params={
                'auth': self.auth_token,
                'folderid': current_id,
                'nofiles': 1
            })
            
            folder_exists = False
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 0:
                    folders = data.get('metadata', {}).get('contents', [])
                    for folder in folders:
                        if folder.get('name') == part and folder.get('isfolder'):
                            current_id = folder.get('folderid')
                            folder_exists = True
                            break
            
            if not folder_exists:
                # Create folder
                response = requests.get(f"{self.api_base}/createfolder", params={
                    'auth': self.auth_token,
                    'folderid': current_id,
                    'name': part
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('result') == 0:
                        current_id = data.get('metadata', {}).get('folderid')
        
        return current_id
    
    def _find_file_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Find file by path and return file info"""
        try:
            folder_id = self.lumisync_folder_id or 0
            
            if '/' in file_path:
                folder_path = '/'.join(file_path.split('/')[:-1])
                folder_info = self._find_folder_by_path(folder_path)
                if folder_info:
                    folder_id = folder_info.get('folderid')
                else:
                    return None
            
            filename = file_path.split('/')[-1]
            
            response = requests.get(f"{self.api_base}/listfolder", params={
                'auth': self.auth_token,
                'folderid': folder_id
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 0:
                    contents = data.get('metadata', {}).get('contents', [])
                    for item in contents:
                        if item.get('name') == filename and not item.get('isfolder'):
                            return item
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding file by path: {str(e)}")
            return None
    
    def _find_folder_by_path(self, folder_path: str) -> Optional[Dict[str, Any]]:
        """Find folder by path and return folder info"""
        if not folder_path:
            return {'folderid': self.lumisync_folder_id or 0}
        
        try:
            parts = folder_path.split('/')
            current_id = self.lumisync_folder_id or 0
            
            for part in parts:
                if not part:
                    continue
                
                response = requests.get(f"{self.api_base}/listfolder", params={
                    'auth': self.auth_token,
                    'folderid': current_id,
                    'nofiles': 1
                })
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                if data.get('result') != 0:
                    return None
                
                found = False
                folders = data.get('metadata', {}).get('contents', [])
                for folder in folders:
                    if folder.get('name') == part and folder.get('isfolder'):
                        current_id = folder.get('folderid')
                        found = True
                        break
                
                if not found:
                    return None
            
            return {'folderid': current_id}
            
        except Exception as e:
            logger.error(f"Error finding folder by path: {str(e)}")
            return None
    
    def disconnect(self):
        """Disconnect from pCloud"""
        self.auth_token = None
        self.user_info = None
        self.lumisync_folder_id = None
        self.is_authenticated = False
        logger.info("Disconnected from pCloud")
