"""
Restore Manager - Orchestrates the restore process
Downloads backup from cloud and restores settings and profiles
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
from ..config.settings import TEMP_DIR

logger = logging.getLogger(__name__)


class RestoreError(Exception):
    """Exception raised during restore operations"""
    pass


class RestoreManager:
    """
    Manages the complete restore process for LumiSync.
    
    Downloads backup from cloud storage and restores GNOME settings,
    application profiles, and other user configurations.
    """
    
    def __init__(self, cloud_provider_type: str = 'google_drive'):
        self.logger = logging.getLogger(__name__)
        self.cloud_provider = create_cloud_provider(cloud_provider_type)
        self.profile_detector = ApplicationProfileDetector()
        self.gnome_manager = GnomeSettingsManager()
        self.archive_manager = ArchiveManager()
        self.file_manager = FileManager()
        
        # Create working directories
        self.temp_restore_dir = TEMP_DIR / f"restore_{int(time.time())}"
        self.temp_restore_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"RestoreManager initialized with {cloud_provider_type}")
    
    def restore_backup(self, backup_id: Optional[str] = None,
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Restore settings and profiles from a cloud backup.
        
        Args:
            backup_id: Specific backup ID to restore (None for latest)
            progress_callback: Optional callback for progress updates (step, total_steps, message)
            
        Returns:
            Dictionary with restore information and results
        """
        restore_info = {
            'timestamp': datetime.now().isoformat(),
            'status': 'started',
            'downloaded_files': [],
            'restored_settings': {},
            'restored_profiles': {},
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        total_steps = 8  # Adjust based on actual steps
        current_step = 0
        
        def update_progress(message: str):
            nonlocal current_step
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, message)
            self.logger.info(f"Restore step {current_step}/{total_steps}: {message}")
        
        try:
            update_progress("Initializing restore process")
            
            # Step 1: Authenticate with cloud provider
            update_progress("Authenticating with cloud storage")
            if not self.cloud_provider.is_connected():
                if not self.cloud_provider.authenticate():
                    raise RestoreError("Failed to authenticate with cloud provider")
            
            # Step 2: Download backup files
            update_progress("Downloading backup files from cloud")
            downloaded_files = self._download_backup_files(backup_id)
            restore_info['downloaded_files'] = downloaded_files
            
            if not downloaded_files:
                raise RestoreError("No backup files found to restore")
            
            # Step 3: Load and validate metadata
            update_progress("Loading backup metadata")
            metadata = self._load_backup_metadata()
            restore_info['metadata'] = metadata
            
            # Step 4: Detect current system profiles
            update_progress("Detecting current system configuration")
            current_profiles = self.profile_detector.detect_all_profiles()
            
            # Step 5: Create backup of current settings
            update_progress("Creating backup of current settings")
            self._backup_current_settings()
            
            # Step 6: Restore GNOME settings
            update_progress("Restoring desktop settings")
            gnome_restore_result = self._restore_gnome_settings()
            restore_info['restored_settings'] = gnome_restore_result
            
            # Step 7: Restore application profiles
            update_progress("Restoring application profiles")
            profile_restore_results = self._restore_application_profiles(current_profiles)
            restore_info['restored_profiles'] = profile_restore_results
            
            # Step 8: Finalize and cleanup
            update_progress("Finalizing restore process")
            self._finalize_restore()
            
            restore_info['status'] = 'completed'
            self.logger.info("Restore completed successfully")
            
        except Exception as e:
            restore_info['status'] = 'failed'
            restore_info['errors'].append(str(e))
            self.logger.error(f"Restore failed: {e}")
            raise RestoreError(f"Restore process failed: {e}")
        
        finally:
            # Cleanup temporary files
            self._cleanup_temp_files()
        
        return restore_info
    
    def _download_backup_files(self, backup_id: Optional[str] = None) -> List[str]:
        """Download backup files from cloud storage."""
        downloaded_files = []
        
        try:
            # Find LumiSync folder
            lumisync_folder_id = self.cloud_provider.find_folder("LumiSync")
            if not lumisync_folder_id:
                raise RestoreError("LumiSync folder not found in cloud storage")
            
            # List files in LumiSync folder
            cloud_files = self.cloud_provider.list_files(folder_id=lumisync_folder_id)
            
            if not cloud_files:
                raise RestoreError("No backup files found in cloud storage")
            
            # Download all backup files
            for file_info in cloud_files:
                file_name = file_info['name']
                file_id = file_info['id']
                local_path = self.temp_restore_dir / file_name
                
                self.logger.info(f"Downloading {file_name}")
                
                if self.cloud_provider.download_file(file_id, local_path):
                    downloaded_files.append(file_name)
                    self.logger.info(f"Downloaded {file_name}")
                else:
                    self.logger.warning(f"Failed to download {file_name}")
            
            return downloaded_files
            
        except Exception as e:
            self.logger.error(f"Failed to download backup files: {e}")
            raise RestoreError(f"Download failed: {e}")
    
    def _load_backup_metadata(self) -> Dict[str, Any]:
        """Load and validate backup metadata."""
        metadata_file = self.temp_restore_dir / "metadata.json"
        
        if not metadata_file.exists():
            raise RestoreError("Backup metadata not found")
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Validate metadata format
            required_fields = ['version', 'created_at', 'device_info', 'backup_contents']
            for field in required_fields:
                if field not in metadata:
                    raise RestoreError(f"Invalid metadata: missing {field}")
            
            self.logger.info(f"Loaded backup metadata from {metadata['created_at']}")
            return metadata
            
        except json.JSONDecodeError as e:
            raise RestoreError(f"Invalid metadata format: {e}")
        except Exception as e:
            raise RestoreError(f"Failed to load metadata: {e}")
    
    def _backup_current_settings(self):
        """Create a backup of current settings before restore."""
        try:
            backup_dir = self.temp_restore_dir / "current_backup"
            backup_dir.mkdir(exist_ok=True)
            
            # Backup current GNOME settings
            current_settings = self.gnome_manager.backup_settings()
            settings_backup_file = backup_dir / "current_gnome_settings.json"
            
            with open(settings_backup_file, 'w') as f:
                json.dump(current_settings, f, indent=2)
            
            self.logger.info("Created backup of current settings")
            
        except Exception as e:
            self.logger.warning(f"Failed to backup current settings: {e}")
    
    def _restore_gnome_settings(self) -> Dict[str, Any]:
        """Restore GNOME desktop settings."""
        restore_result = {
            'attempted': False,
            'successful': False,
            'settings_count': 0,
            'errors': []
        }
        
        try:
            settings_file = self.temp_restore_dir / "system_settings.json"
            
            if not settings_file.exists():
                restore_result['errors'].append("System settings file not found")
                return restore_result
            
            with open(settings_file, 'r') as f:
                settings_backup = json.load(f)
            
            restore_result['attempted'] = True
            restore_result['settings_count'] = len(settings_backup.get('settings', {}))
            
            # Restore settings
            success = self.gnome_manager.restore_settings(settings_backup)
            restore_result['successful'] = success
            
            if success:
                self.logger.info("GNOME settings restored successfully")
            else:
                restore_result['errors'].append("Failed to restore GNOME settings")
            
        except Exception as e:
            error_msg = f"Error restoring GNOME settings: {e}"
            restore_result['errors'].append(error_msg)
            self.logger.error(error_msg)
        
        return restore_result
    
    def _restore_application_profiles(self, current_profiles: Dict[str, List[ProfileInfo]]) -> Dict[str, Any]:
        """Restore application profiles from backup archives."""
        restore_results = {}
        
        # List of applications to restore
        apps_to_restore = ['firefox', 'thunderbird']
        
        for app_name in apps_to_restore:
            restore_result = {
                'attempted': False,
                'successful': False,
                'archive_found': False,
                'target_path': None,
                'backup_created': False,
                'errors': []
            }
            
            try:
                # Check if archive exists
                archive_file = self.temp_restore_dir / f"{app_name}_profile.tar.gz"
                
                if not archive_file.exists():
                    restore_result['errors'].append(f"Archive not found: {archive_file.name}")
                    restore_results[app_name] = restore_result
                    continue
                
                restore_result['archive_found'] = True
                restore_result['attempted'] = True
                
                # Detect current installation and target path
                target_profile = self._find_restore_target(app_name, current_profiles)
                
                if not target_profile:
                    # Try to detect where the app should be installed
                    target_path = self._determine_install_path(app_name)
                    if not target_path:
                        restore_result['errors'].append(f"Cannot determine installation path for {app_name}")
                        restore_results[app_name] = restore_result
                        continue
                else:
                    target_path = target_profile.profile_path
                
                restore_result['target_path'] = str(target_path)
                
                # Create backup of existing profile if it exists
                if target_path.exists():
                    backup_path = target_path.with_suffix('.lumisync_backup')
                    if self.file_manager.copy_directory(target_path, backup_path):
                        restore_result['backup_created'] = True
                        self.logger.info(f"Created backup of existing {app_name} profile")
                
                # Extract archive to target location
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                if self.archive_manager.extract_tar_archive(archive_file, target_path):
                    restore_result['successful'] = True
                    self.logger.info(f"Restored {app_name} profile to {target_path}")
                else:
                    restore_result['errors'].append(f"Failed to extract {app_name} archive")
                
            except Exception as e:
                error_msg = f"Error restoring {app_name} profile: {e}"
                restore_result['errors'].append(error_msg)
                self.logger.error(error_msg)
            
            restore_results[app_name] = restore_result
        
        return restore_results
    
    def _find_restore_target(self, app_name: str, current_profiles: Dict[str, List[ProfileInfo]]) -> Optional[ProfileInfo]:
        """Find the target profile for restoration."""
        if app_name in current_profiles and current_profiles[app_name]:
            return current_profiles[app_name][0]  # Use the preferred profile
        return None
    
    def _determine_install_path(self, app_name: str) -> Optional[Path]:
        """Determine where to install an application profile if not currently installed."""
        from ..config.settings import APPLICATION_PATHS
        
        if app_name not in APPLICATION_PATHS:
            return None
        
        # Try to determine the most likely installation path
        app_paths = APPLICATION_PATHS[app_name]
        
        # Check in order of preference: apt, flatpak, snap
        for install_type in ['apt', 'flatpak', 'snap']:
            if install_type in app_paths:
                path_template = app_paths[install_type]
                expanded_path = Path(path_template.replace('~', str(Path.home())))
                
                # For Mozilla apps, we need to create a default profile directory
                if app_name in ['firefox', 'thunderbird']:
                    profile_dir = expanded_path / f"lumisync.default"
                    return profile_dir
                else:
                    return expanded_path
        
        return None
    
    def _finalize_restore(self):
        """Finalize the restore process."""
        try:
            # Show packages list if available
            packages_file = self.temp_restore_dir / "installed_packages.txt"
            if packages_file.exists():
                self.logger.info("Package list available for manual installation")
                # In a GUI, this would be displayed to the user
            
            # Log completion message
            self.logger.info("Restore process completed. Please restart applications to see changes.")
            
        except Exception as e:
            self.logger.warning(f"Error in finalization: {e}")
    
    def _cleanup_temp_files(self):
        """Clean up temporary restore files."""
        try:
            if self.temp_restore_dir.exists():
                import shutil
                shutil.rmtree(self.temp_restore_dir)
                self.logger.debug(f"Cleaned up temporary directory: {self.temp_restore_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp files: {e}")
    
    def list_available_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups in cloud storage.
        
        Returns:
            List of backup information dictionaries
        """
        try:
            if not self.cloud_provider.is_connected():
                if not self.cloud_provider.authenticate():
                    raise RestoreError("Failed to authenticate with cloud provider")
            
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
                                'id': file['id'],
                                'created_at': metadata.get('created_at'),
                                'device_info': metadata.get('device_info', {}),
                                'total_size_mb': metadata.get('total_size_mb', 0),
                                'applications': list(metadata.get('backup_contents', {}).get('application_profiles', {}).keys()),
                                'lumisync_version': metadata.get('lumisync_version', 'unknown')
                            }
                            backups.append(backup_info)
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to parse metadata: {e}")
                        finally:
                            # Cleanup temp file
                            if temp_metadata_file.exists():
                                temp_metadata_file.unlink()
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return backups
            
        except Exception as e:
            self.logger.error(f"Failed to list available backups: {e}")
            return []
    
    def validate_backup_compatibility(self, backup_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if a backup is compatible with the current system.
        
        Args:
            backup_metadata: Metadata from the backup
            
        Returns:
            Dictionary with compatibility information
        """
        compatibility = {
            'compatible': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        try:
            # Check LumiSync version compatibility
            backup_version = backup_metadata.get('lumisync_version', 'unknown')
            if backup_version != '0.1.0':
                compatibility['warnings'].append(f"Backup created with different LumiSync version: {backup_version}")
            
            # Check desktop environment
            backup_device = backup_metadata.get('device_info', {})
            backup_desktop = backup_device.get('desktop', '')
            
            current_device = self.gnome_manager.get_system_info()
            current_desktop = current_device.get('desktop', '')
            
            if 'GNOME' not in backup_desktop and 'GNOME' in current_desktop:
                compatibility['warnings'].append("Backup was not created on a GNOME system")
            
            # Check application compatibility
            backup_apps = backup_metadata.get('backup_contents', {}).get('application_profiles', {})
            current_profiles = self.profile_detector.detect_all_profiles()
            
            for app_name in backup_apps.keys():
                if app_name not in current_profiles:
                    compatibility['recommendations'].append(f"Install {app_name} before restoring for best results")
            
        except Exception as e:
            compatibility['errors'].append(f"Error validating compatibility: {e}")
            compatibility['compatible'] = False
        
        return compatibility


# Convenience function
def restore_backup(cloud_provider_type: str = 'google_drive',
                  backup_id: Optional[str] = None,
                  progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Convenience function to restore a backup.
    
    Args:
        cloud_provider_type: Type of cloud provider to use
        backup_id: Specific backup ID to restore (None for latest)
        progress_callback: Optional progress callback
        
    Returns:
        Restore information dictionary
    """
    manager = RestoreManager(cloud_provider_type)
    return manager.restore_backup(backup_id, progress_callback)
