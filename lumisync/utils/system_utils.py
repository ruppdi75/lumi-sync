"""
System Utilities for GNOME/dconf Operations
Handles desktop settings backup and restoration
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

from ..config.settings import GNOME_SETTINGS_KEYS

logger = logging.getLogger(__name__)


class SystemUtilsError(Exception):
    """Base exception for system utilities operations"""
    pass


class GnomeSettingsManager:
    """
    Manager for GNOME desktop settings using gsettings and dconf.
    
    Handles backup and restoration of desktop appearance, themes,
    wallpapers, dock settings, and other GNOME configuration.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate that we're running in a GNOME environment."""
        try:
            # Check if gsettings is available
            result = subprocess.run(['which', 'gsettings'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise SystemUtilsError("gsettings command not found. GNOME environment required.")
            
            # Check if we can access the GNOME settings
            result = subprocess.run(['gsettings', 'list-schemas'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise SystemUtilsError("Cannot access GNOME settings. Check DISPLAY variable.")
            
            self.logger.info("GNOME environment validated successfully")
            
        except FileNotFoundError:
            raise SystemUtilsError("gsettings command not found. Please install GNOME.")
        except Exception as e:
            raise SystemUtilsError(f"Failed to validate GNOME environment: {e}")
    
    def backup_settings(self) -> Dict[str, Any]:
        """
        Backup GNOME settings to a dictionary.
        
        Returns:
            Dictionary containing all backed up settings
        """
        settings_backup = {
            'version': '1.0',
            'desktop_environment': 'GNOME',
            'settings': {},
            'custom_keybindings': [],
            'extensions': {}
        }
        
        self.logger.info("Starting GNOME settings backup")
        
        # Backup individual settings keys
        for key in GNOME_SETTINGS_KEYS:
            try:
                value = self._get_setting(key)
                if value is not None:
                    settings_backup['settings'][key] = value
                    self.logger.debug(f"Backed up setting: {key} = {value}")
            except Exception as e:
                self.logger.warning(f"Failed to backup setting {key}: {e}")
        
        # Backup custom keybindings
        try:
            keybindings = self._backup_custom_keybindings()
            settings_backup['custom_keybindings'] = keybindings
            self.logger.info(f"Backed up {len(keybindings)} custom keybindings")
        except Exception as e:
            self.logger.warning(f"Failed to backup custom keybindings: {e}")
        
        # Backup enabled extensions
        try:
            extensions = self._backup_extensions()
            settings_backup['extensions'] = extensions
            self.logger.info(f"Backed up {len(extensions)} extension settings")
        except Exception as e:
            self.logger.warning(f"Failed to backup extensions: {e}")
        
        self.logger.info("GNOME settings backup completed")
        return settings_backup
    
    def restore_settings(self, settings_backup: Dict[str, Any]) -> bool:
        """
        Restore GNOME settings from a backup dictionary.
        
        Args:
            settings_backup: Dictionary containing settings to restore
            
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            self.logger.info("Starting GNOME settings restoration")
            
            # Validate backup format
            if not self._validate_backup_format(settings_backup):
                raise SystemUtilsError("Invalid backup format")
            
            success_count = 0
            total_count = 0
            
            # Restore individual settings
            settings = settings_backup.get('settings', {})
            for key, value in settings.items():
                total_count += 1
                try:
                    if self._set_setting(key, value):
                        success_count += 1
                        self.logger.debug(f"Restored setting: {key} = {value}")
                    else:
                        self.logger.warning(f"Failed to restore setting: {key}")
                except Exception as e:
                    self.logger.warning(f"Error restoring setting {key}: {e}")
            
            # Restore custom keybindings
            keybindings = settings_backup.get('custom_keybindings', [])
            if keybindings:
                try:
                    self._restore_custom_keybindings(keybindings)
                    self.logger.info(f"Restored {len(keybindings)} custom keybindings")
                except Exception as e:
                    self.logger.warning(f"Failed to restore custom keybindings: {e}")
            
            # Restore extensions (informational only for now)
            extensions = settings_backup.get('extensions', {})
            if extensions:
                self.logger.info(f"Note: {len(extensions)} extensions were in the backup. "
                               "Extension installation not yet implemented.")
            
            self.logger.info(f"Settings restoration completed: {success_count}/{total_count} successful")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Settings restoration failed: {e}")
            return False
    
    def _get_setting(self, key: str) -> Optional[Any]:
        """Get a single GNOME setting value."""
        try:
            # Split schema and key
            parts = key.rsplit('.', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid setting key format: {key}")
            
            schema, setting_key = parts
            
            result = subprocess.run(
                ['gsettings', 'get', schema, setting_key],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                value = result.stdout.strip()
                # Parse the value based on its type
                return self._parse_gsettings_value(value)
            else:
                self.logger.warning(f"Failed to get setting {key}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout getting setting: {key}")
            return None
        except Exception as e:
            self.logger.warning(f"Error getting setting {key}: {e}")
            return None
    
    def _set_setting(self, key: str, value: Any) -> bool:
        """Set a single GNOME setting value."""
        try:
            # Split schema and key
            parts = key.rsplit('.', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid setting key format: {key}")
            
            schema, setting_key = parts
            
            # Format value for gsettings
            formatted_value = self._format_gsettings_value(value)
            
            result = subprocess.run(
                ['gsettings', 'set', schema, setting_key, formatted_value],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return True
            else:
                self.logger.warning(f"Failed to set setting {key}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout setting: {key}")
            return False
        except Exception as e:
            self.logger.warning(f"Error setting {key}: {e}")
            return False
    
    def _parse_gsettings_value(self, value: str) -> Any:
        """Parse a gsettings value string to appropriate Python type."""
        value = value.strip()
        
        # Handle different value types
        if value == 'true':
            return True
        elif value == 'false':
            return False
        elif value.startswith("'") and value.endswith("'"):
            # String value
            return value[1:-1]
        elif value.startswith('[') and value.endswith(']'):
            # Array value
            try:
                # Remove brackets and split by comma
                inner = value[1:-1].strip()
                if not inner:
                    return []
                
                items = []
                for item in inner.split(','):
                    item = item.strip()
                    if item.startswith("'") and item.endswith("'"):
                        items.append(item[1:-1])
                    else:
                        items.append(item)
                return items
            except Exception:
                return value
        else:
            # Try to parse as number
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                return value
    
    def _format_gsettings_value(self, value: Any) -> str:
        """Format a Python value for gsettings."""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, list):
            # Format array
            formatted_items = []
            for item in value:
                if isinstance(item, str):
                    formatted_items.append(f"'{item}'")
                else:
                    formatted_items.append(str(item))
            return f"[{', '.join(formatted_items)}]"
        else:
            return str(value)
    
    def _backup_custom_keybindings(self) -> List[Dict[str, str]]:
        """Backup custom keybindings."""
        keybindings = []
        
        try:
            # Get list of custom keybindings
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.settings-daemon.plugins.media-keys', 'custom-keybindings'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Parse the keybinding paths
                paths_str = result.stdout.strip()
                if paths_str and paths_str != '@as []':
                    # Extract paths from the array format
                    paths = self._parse_gsettings_value(paths_str)
                    
                    for path in paths:
                        if isinstance(path, str) and path.startswith('/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/'):
                            # Get keybinding details
                            schema = f"org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{path}"
                            
                            name = self._get_setting(f"{schema}.name")
                            command = self._get_setting(f"{schema}.command")
                            binding = self._get_setting(f"{schema}.binding")
                            
                            if name and command and binding:
                                keybindings.append({
                                    'name': name,
                                    'command': command,
                                    'binding': binding,
                                    'path': path
                                })
        
        except Exception as e:
            self.logger.warning(f"Error backing up custom keybindings: {e}")
        
        return keybindings
    
    def _restore_custom_keybindings(self, keybindings: List[Dict[str, str]]):
        """Restore custom keybindings."""
        if not keybindings:
            return
        
        try:
            # Create new paths for keybindings
            paths = []
            for i, keybinding in enumerate(keybindings):
                path = f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{i}/"
                paths.append(path)
                
                # Set keybinding details
                schema = f"org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{path}"
                self._set_setting(f"{schema}.name", keybinding['name'])
                self._set_setting(f"{schema}.command", keybinding['command'])
                self._set_setting(f"{schema}.binding", keybinding['binding'])
            
            # Set the paths array
            self._set_setting('org.gnome.settings-daemon.plugins.media-keys.custom-keybindings', paths)
            
        except Exception as e:
            self.logger.warning(f"Error restoring custom keybindings: {e}")
    
    def _backup_extensions(self) -> Dict[str, Any]:
        """Backup GNOME Shell extensions settings."""
        extensions = {}
        
        try:
            # Get enabled extensions
            enabled_extensions = self._get_setting('org.gnome.shell.enabled-extensions')
            if enabled_extensions:
                extensions['enabled'] = enabled_extensions
            
            # Get disabled extensions
            disabled_extensions = self._get_setting('org.gnome.shell.disabled-extensions')
            if disabled_extensions:
                extensions['disabled'] = disabled_extensions
            
        except Exception as e:
            self.logger.warning(f"Error backing up extensions: {e}")
        
        return extensions
    
    def _validate_backup_format(self, backup: Dict[str, Any]) -> bool:
        """Validate the format of a settings backup."""
        required_keys = ['version', 'settings']
        
        for key in required_keys:
            if key not in backup:
                self.logger.error(f"Missing required key in backup: {key}")
                return False
        
        if not isinstance(backup['settings'], dict):
            self.logger.error("Settings must be a dictionary")
            return False
        
        return True
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information for backup metadata."""
        info = {}
        
        try:
            # Get hostname
            result = subprocess.run(['hostname'], capture_output=True, text=True)
            if result.returncode == 0:
                info['hostname'] = result.stdout.strip()
        except Exception:
            info['hostname'] = 'unknown'
        
        try:
            # Get OS information
            if Path('/etc/os-release').exists():
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            info['os'] = line.split('=', 1)[1].strip().strip('"')
                            break
        except Exception:
            info['os'] = 'Linux'
        
        try:
            # Get GNOME version
            result = subprocess.run(['gnome-shell', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                info['desktop'] = result.stdout.strip()
        except Exception:
            info['desktop'] = 'GNOME'
        
        return info


# Convenience functions
def backup_gnome_settings() -> Dict[str, Any]:
    """
    Convenience function to backup GNOME settings.
    
    Returns:
        Dictionary containing backed up settings
    """
    manager = GnomeSettingsManager()
    return manager.backup_settings()


def restore_gnome_settings(settings_backup: Dict[str, Any]) -> bool:
    """
    Convenience function to restore GNOME settings.
    
    Args:
        settings_backup: Dictionary containing settings to restore
        
    Returns:
        True if restoration successful, False otherwise
    """
    manager = GnomeSettingsManager()
    return manager.restore_settings(settings_backup)
