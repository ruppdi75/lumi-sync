"""
Backup Manager - Orchestrates the backup process
Coordinates profile detection, system settings backup, and cloud upload
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import logging

from .profile_detector import ApplicationProfileDetector, ProfileInfo
from .cloud_providers.provider_factory import create_cloud_provider
from ..utils.system_utils import GnomeSettingsManager
from ..utils.file_utils import ArchiveManager, FileManager
from ..config.settings import TEMP_DIR, BACKUP_FOLDER_STRUCTURE

logger = logging.getLogger(__name__)


class BackupError(Exception):
    """Exception raised during backup operations"""
    pass


class BackupManager:
    """
    Manages the complete backup process for LumiSync.
    
    Coordinates profile detection, system settings backup, file archiving,
    and cloud upload to create a complete backup of user settings.
    """
    
    def __init__(self, cloud_provider_type: str = 'google_drive'):
        self.logger = logging.getLogger(__name__)
        self.cloud_provider = create_cloud_provider(cloud_provider_type)
        self.profile_detector = ApplicationProfileDetector()
        self.gnome_manager = GnomeSettingsManager()
        self.archive_manager = ArchiveManager()
        self.file_manager = FileManager()
        
        # Create working directories
        self.temp_backup_dir = TEMP_DIR / f"backup_{int(time.time())}"
        self.temp_backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"BackupManager initialized with {cloud_provider_type}")
    
    def create_backup(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Create a complete backup of user settings and profiles.
        
        Args:
            progress_callback: Optional callback for progress updates (step, total_steps, message)
            
        Returns:
            Dictionary with backup information and results
        """
        backup_info = {
            'timestamp': datetime.now().isoformat(),
            'status': 'started',
            'files_created': [],
            'cloud_files': {},
            'errors': [],
            'metadata': {}
        }
        
        total_steps = 7  # Adjust based on actual steps
        current_step = 0
        
        def update_progress(message: str):
            nonlocal current_step
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, message)
            self.logger.info(f"Backup step {current_step}/{total_steps}: {message}")
        
        try:
            update_progress("Initializing backup process")
            
            # Step 1: Authenticate with cloud provider
            update_progress("Authenticating with cloud storage")
            if not self.cloud_provider.is_connected():
                if not self.cloud_provider.authenticate():
                    raise BackupError("Failed to authenticate with cloud provider")
            
            # Step 2: Detect application profiles
            update_progress("Detecting application profiles")
            detected_profiles = self.profile_detector.detect_all_profiles()
            backup_info['metadata']['detected_profiles'] = {
                app: [profile.to_dict() for profile in profiles]
                for app, profiles in detected_profiles.items()
            }
            
            # Step 3: Backup GNOME settings
            update_progress("Backing up desktop settings")
            gnome_settings = self.gnome_manager.backup_settings()
            system_settings_file = self.temp_backup_dir / "system_settings.json"
            
            with open(system_settings_file, 'w') as f:
                json.dump(gnome_settings, f, indent=2)
            backup_info['files_created'].append(str(system_settings_file))
            
            # Step 4: Create application profile archives
            update_progress("Creating application profile archives")
            profile_archives = {}
            
            for app_name, profiles in detected_profiles.items():
                if profiles:  # Take the first (preferred) profile
                    profile = profiles[0]
                    if self.profile_detector.validate_profile(profile):
                        archive_path = self.temp_backup_dir / f"{app_name}_profile.tar.gz"
                        
                        if self.archive_manager.create_tar_archive(
                            source_path=profile.profile_path,
                            archive_path=archive_path,
                            compression='gz'
                        ):
                            profile_archives[app_name] = {
                                'archive_path': str(archive_path),
                                'profile_info': profile.to_dict()
                            }
                            backup_info['files_created'].append(str(archive_path))
                            self.logger.info(f"Created archive for {app_name}: {archive_path}")
                        else:
                            error_msg = f"Failed to create archive for {app_name}"
                            backup_info['errors'].append(error_msg)
                            self.logger.error(error_msg)
            
            # Step 5: Create backup metadata
            update_progress("Creating backup metadata")
            metadata = self._create_backup_metadata(detected_profiles, gnome_settings)
            metadata_file = self.temp_backup_dir / "metadata.json"
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            backup_info['files_created'].append(str(metadata_file))
            backup_info['metadata'].update(metadata)
            
            # Step 6: Create installed packages list
            update_progress("Creating installed packages list")
            packages_file = self.temp_backup_dir / "installed_packages.txt"
            if self._create_packages_list(packages_file):
                backup_info['files_created'].append(str(packages_file))
            
            # Step 7: Upload to cloud storage
            update_progress("Uploading to cloud storage")
            cloud_files = self._upload_backup_to_cloud()
            backup_info['cloud_files'] = cloud_files
            
            backup_info['status'] = 'completed'
            self.logger.info("Backup completed successfully")
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['errors'].append(str(e))
            self.logger.error(f"Backup failed: {e}")
            raise BackupError(f"Backup process failed: {e}")
        
        finally:
            # Cleanup temporary files
            self._cleanup_temp_files()
        
        return backup_info
    
    def _create_backup_metadata(self, detected_profiles: Dict[str, List[ProfileInfo]], 
                               gnome_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive backup metadata."""
        metadata = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'lumisync_version': '0.1.0',
            'device_info': self.gnome_manager.get_system_info(),
            'backup_contents': {
                'gnome_settings': {
                    'included': True,
                    'settings_count': len(gnome_settings.get('settings', {})),
                    'keybindings_count': len(gnome_settings.get('custom_keybindings', [])),
                    'extensions_count': len(gnome_settings.get('extensions', {}))
                },
                'application_profiles': {}
            },
            'cloud_provider': self.cloud_provider.provider_name,
            'total_size_mb': 0
        }
        
        # Add profile information
        for app_name, profiles in detected_profiles.items():
            if profiles:
                profile = profiles[0]
                metadata['backup_contents']['application_profiles'][app_name] = {
                    'included': True,
                    'install_type': profile.install_type,
                    'profile_name': profile.profile_name,
                    'size_mb': profile.size_mb,
                    'profile_path': str(profile.profile_path)
                }
                metadata['total_size_mb'] += profile.size_mb
        
        return metadata
    
    def _create_packages_list(self, packages_file: Path) -> bool:
        """Create a list of installed packages."""
        try:
            import subprocess
            
            # Get manually installed packages
            result = subprocess.run(
                ['apt-mark', 'showmanual'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                with open(packages_file, 'w') as f:
                    f.write("# LumiSync - Installed Packages List\n")
                    f.write(f"# Generated on {datetime.now().isoformat()}\n")
                    f.write("# This list contains manually installed packages\n\n")
                    f.write(result.stdout)
                
                self.logger.info(f"Created packages list: {packages_file}")
                return True
            else:
                self.logger.warning(f"Failed to get packages list: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating packages list: {e}")
            return False
    
    def _upload_backup_to_cloud(self) -> Dict[str, str]:
        """Upload backup files to cloud storage."""
        cloud_files = {}
        
        try:
            # Get or create LumiSync folder
            lumisync_folder_id = self.cloud_provider.get_lumisync_folder_id()
            
            # Upload all files in temp backup directory
            for file_path in self.temp_backup_dir.iterdir():
                if file_path.is_file():
                    self.logger.info(f"Uploading {file_path.name}")
                    
                    file_id = self.cloud_provider.upload_file(
                        local_path=file_path,
                        remote_path=file_path.name,
                        parent_id=lumisync_folder_id
                    )
                    
                    if file_id:
                        cloud_files[file_path.name] = file_id
                        self.logger.info(f"Uploaded {file_path.name} with ID: {file_id}")
                    else:
                        raise BackupError(f"Failed to upload {file_path.name}")
            
            return cloud_files
            
        except Exception as e:
            self.logger.error(f"Cloud upload failed: {e}")
            raise BackupError(f"Failed to upload backup to cloud: {e}")
    
    def _cleanup_temp_files(self):
        """Clean up temporary backup files."""
        try:
            if self.temp_backup_dir.exists():
                import shutil
                shutil.rmtree(self.temp_backup_dir)
                self.logger.debug(f"Cleaned up temporary directory: {self.temp_backup_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp files: {e}")
    
    def list_cloud_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups in cloud storage.
        
        Returns:
            List of backup information dictionaries
        """
        try:
            if not self.cloud_provider.is_connected():
                if not self.cloud_provider.authenticate():
                    raise BackupError("Failed to authenticate with cloud provider")
            
            # Find LumiSync folder
            lumisync_folder_id = self.cloud_provider.find_folder("LumiSync")
            if not lumisync_folder_id:
                return []
            
            # List files in LumiSync folder
            files = self.cloud_provider.list_files(folder_id=lumisync_folder_id)
            
            # Look for metadata files to identify backups
            backups = []
            for file in files:
                if file['name'] == 'metadata.json':
                    # Download and parse metadata
                    temp_metadata_file = TEMP_DIR / f"temp_metadata_{int(time.time())}.json"
                    
                    if self.cloud_provider.download_file(file['id'], temp_metadata_file):
                        try:
                            with open(temp_metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            backup_info = {
                                'created_at': metadata.get('created_at'),
                                'device_info': metadata.get('device_info', {}),
                                'total_size_mb': metadata.get('total_size_mb', 0),
                                'applications': list(metadata.get('backup_contents', {}).get('application_profiles', {}).keys()),
                                'cloud_file_id': file['id']
                            }
                            backups.append(backup_info)
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to parse metadata: {e}")
                        finally:
                            # Cleanup temp file
                            if temp_metadata_file.exists():
                                temp_metadata_file.unlink()
            
            return backups
            
        except Exception as e:
            self.logger.error(f"Failed to list cloud backups: {e}")
            return []
    
    def get_backup_size_estimate(self) -> Dict[str, float]:
        """
        Estimate the size of a potential backup.
        
        Returns:
            Dictionary with size estimates in MB
        """
        size_estimate = {
            'gnome_settings': 0.1,  # Settings are typically very small
            'application_profiles': {},
            'total_estimated_mb': 0.1
        }
        
        try:
            # Detect profiles and estimate their sizes
            detected_profiles = self.profile_detector.detect_all_profiles()
            
            for app_name, profiles in detected_profiles.items():
                if profiles:
                    profile = profiles[0]
                    size_mb = profile.size_mb
                    size_estimate['application_profiles'][app_name] = size_mb
                    size_estimate['total_estimated_mb'] += size_mb
            
        except Exception as e:
            self.logger.warning(f"Failed to estimate backup size: {e}")
        
        return size_estimate


# Convenience function
def create_backup(cloud_provider_type: str = 'google_drive', 
                 progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Convenience function to create a backup.
    
    Args:
        cloud_provider_type: Type of cloud provider to use
        progress_callback: Optional progress callback
        
    Returns:
        Backup information dictionary
    """
    manager = BackupManager(cloud_provider_type)
    return manager.create_backup(progress_callback)
