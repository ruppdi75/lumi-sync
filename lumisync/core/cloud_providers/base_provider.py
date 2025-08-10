"""
Base Cloud Provider Abstract Class
Defines the interface that all cloud storage providers must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CloudProviderError(Exception):
    """Base exception for cloud provider operations"""
    pass


class AuthenticationError(CloudProviderError):
    """Raised when authentication fails"""
    pass


class UploadError(CloudProviderError):
    """Raised when file upload fails"""
    pass


class DownloadError(CloudProviderError):
    """Raised when file download fails"""
    pass


class CloudProvider(ABC):
    """
    Abstract base class for all cloud storage providers.
    
    This class defines the standard interface that all cloud providers
    (Google Drive, OneDrive, Box, pCloud) must implement to work with LumiSync.
    """
    
    def __init__(self, provider_name: str):
        """
        Initialize the cloud provider.
        
        Args:
            provider_name: Human-readable name of the provider (e.g., "Google Drive")
        """
        self.provider_name = provider_name
        self.is_authenticated = False
        self._credentials = None
        self.logger = logging.getLogger(f"lumisync.cloud.{provider_name.lower().replace(' ', '_')}")
    
    @abstractmethod
    def authenticate(self, credentials_path: Optional[Path] = None, **kwargs) -> bool:
        """
        Authenticate with the cloud provider.
        
        Args:
            credentials_path: Path to credentials file (if applicable)
            **kwargs: Provider-specific authentication parameters
            
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if currently connected to the cloud provider.
        
        Returns:
            True if connected and authenticated, False otherwise
        """
        pass
    
    @abstractmethod
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Returns:
            Dictionary containing user information (name, email, storage info, etc.)
        """
        pass
    
    @abstractmethod
    def create_folder(self, folder_path: str, parent_id: Optional[str] = None) -> str:
        """
        Create a folder in the cloud storage.
        
        Args:
            folder_path: Path/name of the folder to create
            parent_id: ID of parent folder (None for root)
            
        Returns:
            ID of the created folder
            
        Raises:
            CloudProviderError: If folder creation fails
        """
        pass
    
    @abstractmethod
    def upload_file(self, local_path: Path, remote_path: str, 
                   parent_id: Optional[str] = None, 
                   progress_callback: Optional[callable] = None) -> str:
        """
        Upload a file to the cloud storage.
        
        Args:
            local_path: Path to the local file to upload
            remote_path: Destination path/name in cloud storage
            parent_id: ID of parent folder (None for root)
            progress_callback: Optional callback for upload progress (bytes_uploaded, total_bytes)
            
        Returns:
            ID of the uploaded file
            
        Raises:
            UploadError: If upload fails
        """
        pass
    
    @abstractmethod
    def download_file(self, file_id: str, local_path: Path,
                     progress_callback: Optional[callable] = None) -> bool:
        """
        Download a file from the cloud storage.
        
        Args:
            file_id: ID of the file to download
            local_path: Local path where to save the file
            progress_callback: Optional callback for download progress (bytes_downloaded, total_bytes)
            
        Returns:
            True if download successful, False otherwise
            
        Raises:
            DownloadError: If download fails
        """
        pass
    
    @abstractmethod
    def list_files(self, folder_id: Optional[str] = None, 
                  folder_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in a folder.
        
        Args:
            folder_id: ID of the folder to list (takes precedence over folder_path)
            folder_path: Path of the folder to list
            
        Returns:
            List of file/folder information dictionaries
            Each dict should contain: id, name, type, size, modified_time
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from the cloud storage.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        pass
    
    @abstractmethod
    def find_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Find a folder by name.
        
        Args:
            folder_name: Name of the folder to find
            parent_id: ID of parent folder to search in (None for root)
            
        Returns:
            ID of the folder if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_storage_info(self) -> Dict[str, int]:
        """
        Get storage quota information.
        
        Returns:
            Dictionary with 'used', 'total', and 'available' storage in bytes
        """
        pass
    
    def get_lumisync_folder_id(self) -> Optional[str]:
        """
        Get or create the LumiSync folder and return its ID.
        
        Returns:
            ID of the LumiSync folder
        """
        folder_id = self.find_folder("LumiSync")
        if not folder_id:
            self.logger.info("Creating LumiSync folder in cloud storage")
            folder_id = self.create_folder("LumiSync")
        return folder_id
    
    def upload_backup_structure(self, backup_data: Dict[str, Path], 
                              progress_callback: Optional[callable] = None) -> Dict[str, str]:
        """
        Upload a complete backup structure to the cloud.
        
        Args:
            backup_data: Dictionary mapping remote paths to local file paths
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping remote paths to file IDs
        """
        lumisync_folder_id = self.get_lumisync_folder_id()
        uploaded_files = {}
        
        total_files = len(backup_data)
        for i, (remote_path, local_path) in enumerate(backup_data.items()):
            self.logger.info(f"Uploading {remote_path} ({i+1}/{total_files})")
            
            try:
                file_id = self.upload_file(
                    local_path=local_path,
                    remote_path=remote_path,
                    parent_id=lumisync_folder_id,
                    progress_callback=progress_callback
                )
                uploaded_files[remote_path] = file_id
                
            except Exception as e:
                self.logger.error(f"Failed to upload {remote_path}: {e}")
                raise UploadError(f"Failed to upload {remote_path}: {e}")
        
        return uploaded_files
    
    def download_backup_structure(self, file_mapping: Dict[str, str], 
                                 download_dir: Path,
                                 progress_callback: Optional[callable] = None) -> Dict[str, Path]:
        """
        Download a complete backup structure from the cloud.
        
        Args:
            file_mapping: Dictionary mapping remote paths to file IDs
            download_dir: Local directory to download files to
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping remote paths to local file paths
        """
        download_dir.mkdir(parents=True, exist_ok=True)
        downloaded_files = {}
        
        total_files = len(file_mapping)
        for i, (remote_path, file_id) in enumerate(file_mapping.items()):
            local_path = download_dir / remote_path
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Downloading {remote_path} ({i+1}/{total_files})")
            
            try:
                success = self.download_file(
                    file_id=file_id,
                    local_path=local_path,
                    progress_callback=progress_callback
                )
                
                if success:
                    downloaded_files[remote_path] = local_path
                else:
                    raise DownloadError(f"Download of {remote_path} failed")
                    
            except Exception as e:
                self.logger.error(f"Failed to download {remote_path}: {e}")
                raise DownloadError(f"Failed to download {remote_path}: {e}")
        
        return downloaded_files
    
    def __str__(self) -> str:
        """String representation of the provider"""
        return f"{self.provider_name} ({'Connected' if self.is_connected() else 'Disconnected'})"
    
    def __repr__(self) -> str:
        """Developer representation of the provider"""
        return f"CloudProvider(name='{self.provider_name}', authenticated={self.is_authenticated})"
