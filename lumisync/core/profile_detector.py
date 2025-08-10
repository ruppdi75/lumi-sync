"""
Intelligent Application Profile Detector
Detects application profiles regardless of installation method (APT, Snap, Flatpak)
"""

import os
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from ..config.settings import APPLICATION_PATHS

logger = logging.getLogger(__name__)


class ProfileInfo:
    """Container for application profile information."""
    
    def __init__(self, app_name: str, install_type: str, profile_path: Path, 
                 profile_name: str = "default", is_active: bool = True):
        self.app_name = app_name
        self.install_type = install_type  # 'apt', 'snap', 'flatpak'
        self.profile_path = profile_path
        self.profile_name = profile_name
        self.is_active = is_active
        self.size_mb = self._calculate_size()
    
    def _calculate_size(self) -> float:
        """Calculate the size of the profile directory in MB."""
        if not self.profile_path.exists():
            return 0.0
        
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(self.profile_path):
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    try:
                        total_size += filepath.stat().st_size
                    except (OSError, IOError):
                        continue  # Skip files we can't read
        except (OSError, IOError):
            return 0.0
        
        return round(total_size / (1024 * 1024), 2)  # Convert to MB
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'app_name': self.app_name,
            'install_type': self.install_type,
            'profile_path': str(self.profile_path),
            'profile_name': self.profile_name,
            'is_active': self.is_active,
            'size_mb': self.size_mb
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProfileInfo':
        """Create ProfileInfo from dictionary."""
        return cls(
            app_name=data['app_name'],
            install_type=data['install_type'],
            profile_path=Path(data['profile_path']),
            profile_name=data.get('profile_name', 'default'),
            is_active=data.get('is_active', True)
        )
    
    def __str__(self) -> str:
        return f"{self.app_name} ({self.install_type}): {self.profile_path} ({self.size_mb} MB)"


class ApplicationProfileDetector:
    """
    Intelligent detector for application profiles across different installation methods.
    
    This class can detect Firefox, Thunderbird, and other application profiles
    regardless of whether they were installed via APT, Snap, or Flatpak.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.home_dir = Path.home()
    
    def detect_all_profiles(self) -> Dict[str, List[ProfileInfo]]:
        """
        Detect all supported application profiles.
        
        Returns:
            Dictionary mapping app names to lists of detected profiles
        """
        all_profiles = {}
        
        for app_name in APPLICATION_PATHS.keys():
            profiles = self.detect_application_profiles(app_name)
            if profiles:
                all_profiles[app_name] = profiles
                self.logger.info(f"Detected {len(profiles)} profile(s) for {app_name}")
            else:
                self.logger.info(f"No profiles found for {app_name}")
        
        return all_profiles
    
    def detect_application_profiles(self, app_name: str) -> List[ProfileInfo]:
        """
        Detect profiles for a specific application.
        
        Args:
            app_name: Name of the application (e.g., 'firefox', 'thunderbird')
            
        Returns:
            List of detected ProfileInfo objects
        """
        if app_name not in APPLICATION_PATHS:
            self.logger.warning(f"Unknown application: {app_name}")
            return []
        
        profiles = []
        app_paths = APPLICATION_PATHS[app_name]
        
        # Check each installation type in order of preference
        for install_type in ['snap', 'flatpak', 'apt']:
            if install_type in app_paths:
                detected_profiles = self._detect_profiles_for_type(
                    app_name, install_type, app_paths[install_type]
                )
                profiles.extend(detected_profiles)
        
        # If we found profiles from multiple installation types, prefer the most recently used
        if len(profiles) > 1:
            profiles = self._filter_preferred_profiles(profiles)
        
        return profiles
    
    def _detect_profiles_for_type(self, app_name: str, install_type: str, 
                                 base_path: str) -> List[ProfileInfo]:
        """
        Detect profiles for a specific installation type.
        
        Args:
            app_name: Application name
            install_type: Installation type ('apt', 'snap', 'flatpak')
            base_path: Base path template for the installation type
            
        Returns:
            List of detected ProfileInfo objects
        """
        profiles = []
        
        # Expand the path template
        expanded_path = Path(os.path.expanduser(base_path))
        
        if not expanded_path.exists():
            self.logger.debug(f"Path does not exist: {expanded_path}")
            return profiles
        
        self.logger.debug(f"Checking {install_type} path: {expanded_path}")
        
        if app_name in ['firefox', 'thunderbird']:
            profiles = self._detect_mozilla_profiles(app_name, install_type, expanded_path)
        else:
            # For other applications, implement specific detection logic
            profiles = self._detect_generic_profiles(app_name, install_type, expanded_path)
        
        return profiles
    
    def _detect_mozilla_profiles(self, app_name: str, install_type: str, 
                                base_path: Path) -> List[ProfileInfo]:
        """
        Detect Mozilla application profiles (Firefox, Thunderbird).
        
        Mozilla applications use a profiles.ini file to manage multiple profiles.
        """
        profiles = []
        profiles_ini = base_path / "profiles.ini"
        
        if not profiles_ini.exists():
            self.logger.debug(f"No profiles.ini found at {profiles_ini}")
            return profiles
        
        try:
            config = configparser.ConfigParser()
            config.read(profiles_ini)
            
            # Parse profiles from profiles.ini
            for section_name in config.sections():
                if section_name.startswith('Profile'):
                    section = config[section_name]
                    
                    # Get profile information
                    profile_name = section.get('Name', 'Unknown')
                    is_relative = section.getboolean('IsRelative', True)
                    profile_path_str = section.get('Path', '')
                    is_default = section.getboolean('Default', False)
                    
                    if not profile_path_str:
                        continue
                    
                    # Construct full profile path
                    if is_relative:
                        profile_path = base_path / profile_path_str
                    else:
                        profile_path = Path(profile_path_str)
                    
                    if profile_path.exists():
                        profile_info = ProfileInfo(
                            app_name=app_name,
                            install_type=install_type,
                            profile_path=profile_path,
                            profile_name=profile_name,
                            is_active=is_default
                        )
                        profiles.append(profile_info)
                        self.logger.debug(f"Found {app_name} profile: {profile_info}")
            
            # If no profiles found in profiles.ini, look for default profile
            if not profiles:
                profiles = self._find_default_mozilla_profile(app_name, install_type, base_path)
        
        except Exception as e:
            self.logger.error(f"Error parsing profiles.ini for {app_name}: {e}")
            # Fallback to looking for default profile
            profiles = self._find_default_mozilla_profile(app_name, install_type, base_path)
        
        return profiles
    
    def _find_default_mozilla_profile(self, app_name: str, install_type: str, 
                                    base_path: Path) -> List[ProfileInfo]:
        """
        Find default Mozilla profile by looking for .default or .default-release directories.
        """
        profiles = []
        
        try:
            # Look for profile directories
            for item in base_path.iterdir():
                if item.is_dir():
                    dir_name = item.name
                    # Mozilla profiles typically end with .default or .default-release
                    if (dir_name.endswith('.default') or 
                        dir_name.endswith('.default-release') or
                        dir_name.endswith('.default-esr')):
                        
                        profile_info = ProfileInfo(
                            app_name=app_name,
                            install_type=install_type,
                            profile_path=item,
                            profile_name='default',
                            is_active=True
                        )
                        profiles.append(profile_info)
                        self.logger.debug(f"Found default {app_name} profile: {profile_info}")
        
        except Exception as e:
            self.logger.error(f"Error finding default {app_name} profile: {e}")
        
        return profiles
    
    def _detect_generic_profiles(self, app_name: str, install_type: str, 
                               base_path: Path) -> List[ProfileInfo]:
        """
        Generic profile detection for applications that don't use profiles.ini.
        """
        profiles = []
        
        if base_path.exists() and base_path.is_dir():
            profile_info = ProfileInfo(
                app_name=app_name,
                install_type=install_type,
                profile_path=base_path,
                profile_name='default',
                is_active=True
            )
            profiles.append(profile_info)
            self.logger.debug(f"Found {app_name} config: {profile_info}")
        
        return profiles
    
    def _filter_preferred_profiles(self, profiles: List[ProfileInfo]) -> List[ProfileInfo]:
        """
        Filter profiles to return the most preferred ones.
        
        Preference order: Snap > Flatpak > APT (most recent/isolated first)
        """
        if not profiles:
            return profiles
        
        # Group by application
        app_groups = {}
        for profile in profiles:
            app_name = profile.app_name
            if app_name not in app_groups:
                app_groups[app_name] = []
            app_groups[app_name].append(profile)
        
        preferred_profiles = []
        
        for app_name, app_profiles in app_groups.items():
            # Sort by preference: snap > flatpak > apt
            preference_order = {'snap': 0, 'flatpak': 1, 'apt': 2}
            app_profiles.sort(key=lambda p: preference_order.get(p.install_type, 3))
            
            # Take the most preferred profile
            preferred_profiles.append(app_profiles[0])
            
            self.logger.info(f"Selected {app_profiles[0].install_type} installation for {app_name}")
        
        return preferred_profiles
    
    def get_profile_by_app(self, app_name: str) -> Optional[ProfileInfo]:
        """
        Get the preferred profile for a specific application.
        
        Args:
            app_name: Name of the application
            
        Returns:
            ProfileInfo object if found, None otherwise
        """
        profiles = self.detect_application_profiles(app_name)
        return profiles[0] if profiles else None
    
    def validate_profile(self, profile: ProfileInfo) -> bool:
        """
        Validate that a profile is still valid and accessible.
        
        Args:
            profile: ProfileInfo object to validate
            
        Returns:
            True if profile is valid, False otherwise
        """
        try:
            if not profile.profile_path.exists():
                self.logger.warning(f"Profile path no longer exists: {profile.profile_path}")
                return False
            
            if not os.access(profile.profile_path, os.R_OK):
                self.logger.warning(f"Profile path not readable: {profile.profile_path}")
                return False
            
            # For Mozilla apps, check for key files
            if profile.app_name in ['firefox', 'thunderbird']:
                prefs_file = profile.profile_path / "prefs.js"
                if not prefs_file.exists():
                    self.logger.warning(f"Missing prefs.js in {profile.app_name} profile")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating profile {profile}: {e}")
            return False


# Convenience function
def detect_all_application_profiles() -> Dict[str, List[ProfileInfo]]:
    """
    Convenience function to detect all application profiles.
    
    Returns:
        Dictionary mapping app names to lists of detected profiles
    """
    detector = ApplicationProfileDetector()
    return detector.detect_all_profiles()
