"""
File Utilities for Archive Operations
Handles compression, extraction, and file management for backups
"""

import tarfile
import zipfile
import shutil
import os
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
import logging
import hashlib

logger = logging.getLogger(__name__)


class FileUtilsError(Exception):
    """Base exception for file utilities operations"""
    pass


class ArchiveManager:
    """
    Manager for creating and extracting archives.
    
    Supports tar.gz, tar, and zip formats with progress callbacks
    and integrity verification.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_tar_archive(self, source_path: Path, archive_path: Path, 
                          compression: str = 'gz',
                          progress_callback: Optional[Callable] = None,
                          exclude_patterns: Optional[List[str]] = None) -> bool:
        """
        Create a tar archive from a source directory or file.
        
        Args:
            source_path: Path to source directory or file
            archive_path: Path where to create the archive
            compression: Compression type ('gz', 'bz2', 'xz', or None)
            progress_callback: Optional callback for progress updates
            exclude_patterns: List of patterns to exclude from archive
            
        Returns:
            True if archive created successfully, False otherwise
        """
        try:
            if not source_path.exists():
                raise FileUtilsError(f"Source path does not exist: {source_path}")
            
            # Ensure parent directory exists
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine tar mode
            if compression == 'gz':
                mode = 'w:gz'
            elif compression == 'bz2':
                mode = 'w:bz2'
            elif compression == 'xz':
                mode = 'w:xz'
            else:
                mode = 'w'
            
            self.logger.info(f"Creating archive: {archive_path}")
            
            with tarfile.open(archive_path, mode) as tar:
                if source_path.is_file():
                    # Add single file
                    tar.add(source_path, arcname=source_path.name)
                    if progress_callback:
                        progress_callback(1, 1)
                else:
                    # Add directory contents
                    files_to_add = self._get_files_to_archive(source_path, exclude_patterns)
                    total_files = len(files_to_add)
                    
                    for i, file_path in enumerate(files_to_add):
                        try:
                            # Calculate relative path for archive
                            arcname = file_path.relative_to(source_path)
                            tar.add(file_path, arcname=str(arcname))
                            
                            if progress_callback:
                                progress_callback(i + 1, total_files)
                                
                        except Exception as e:
                            self.logger.warning(f"Failed to add {file_path} to archive: {e}")
            
            # Verify archive was created
            if archive_path.exists() and archive_path.stat().st_size > 0:
                self.logger.info(f"Archive created successfully: {archive_path} ({self._format_size(archive_path.stat().st_size)})")
                return True
            else:
                raise FileUtilsError("Archive creation failed - file is empty or missing")
                
        except Exception as e:
            self.logger.error(f"Failed to create archive {archive_path}: {e}")
            # Clean up partial archive
            if archive_path.exists():
                try:
                    archive_path.unlink()
                except Exception:
                    pass
            return False
    
    def extract_tar_archive(self, archive_path: Path, extract_path: Path,
                           progress_callback: Optional[Callable] = None) -> bool:
        """
        Extract a tar archive to a destination directory.
        
        Args:
            archive_path: Path to the archive file
            extract_path: Path where to extract the archive
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if extraction successful, False otherwise
        """
        try:
            if not archive_path.exists():
                raise FileUtilsError(f"Archive does not exist: {archive_path}")
            
            # Ensure extraction directory exists
            extract_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Extracting archive: {archive_path} to {extract_path}")
            
            with tarfile.open(archive_path, 'r:*') as tar:
                members = tar.getmembers()
                total_members = len(members)
                
                for i, member in enumerate(members):
                    try:
                        # Security check - prevent path traversal
                        if self._is_safe_path(member.name):
                            tar.extract(member, extract_path)
                        else:
                            self.logger.warning(f"Skipping unsafe path: {member.name}")
                        
                        if progress_callback:
                            progress_callback(i + 1, total_members)
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to extract {member.name}: {e}")
            
            self.logger.info(f"Archive extracted successfully to {extract_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to extract archive {archive_path}: {e}")
            return False
    
    def _get_files_to_archive(self, source_path: Path, 
                             exclude_patterns: Optional[List[str]] = None) -> List[Path]:
        """Get list of files to include in archive."""
        files = []
        exclude_patterns = exclude_patterns or []
        
        # Add common exclusion patterns
        default_excludes = [
            '*.tmp', '*.temp', '*.log', '*.cache', '*.lock',
            '__pycache__', '.git', '.svn', '.DS_Store', 'Thumbs.db'
        ]
        exclude_patterns.extend(default_excludes)
        
        for root, dirs, filenames in os.walk(source_path):
            root_path = Path(root)
            
            # Filter directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]
            
            # Add files
            for filename in filenames:
                if not self._should_exclude(filename, exclude_patterns):
                    file_path = root_path / filename
                    if file_path.exists():
                        files.append(file_path)
        
        return files
    
    def _should_exclude(self, name: str, patterns: List[str]) -> bool:
        """Check if a file/directory should be excluded based on patterns."""
        import fnmatch
        
        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False
    
    def _is_safe_path(self, path: str) -> bool:
        """Check if a path is safe for extraction (prevents path traversal)."""
        # Normalize the path
        normalized = os.path.normpath(path)
        
        # Check for path traversal attempts
        if normalized.startswith('/') or '..' in normalized:
            return False
        
        return True
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def verify_archive_integrity(self, archive_path: Path) -> bool:
        """
        Verify the integrity of a tar archive.
        
        Args:
            archive_path: Path to the archive to verify
            
        Returns:
            True if archive is valid, False otherwise
        """
        try:
            with tarfile.open(archive_path, 'r:*') as tar:
                # Try to list all members - this will fail if archive is corrupted
                members = tar.getmembers()
                self.logger.debug(f"Archive {archive_path} contains {len(members)} members")
                return True
                
        except Exception as e:
            self.logger.error(f"Archive integrity check failed for {archive_path}: {e}")
            return False
    
    def get_archive_info(self, archive_path: Path) -> Dict[str, Any]:
        """
        Get information about an archive.
        
        Args:
            archive_path: Path to the archive
            
        Returns:
            Dictionary with archive information
        """
        info = {
            'path': str(archive_path),
            'exists': archive_path.exists(),
            'size_bytes': 0,
            'size_formatted': '0 B',
            'member_count': 0,
            'is_valid': False
        }
        
        if not archive_path.exists():
            return info
        
        try:
            # Get file size
            stat = archive_path.stat()
            info['size_bytes'] = stat.st_size
            info['size_formatted'] = self._format_size(stat.st_size)
            info['modified_time'] = stat.st_mtime
            
            # Get archive contents info
            with tarfile.open(archive_path, 'r:*') as tar:
                members = tar.getmembers()
                info['member_count'] = len(members)
                info['is_valid'] = True
                
        except Exception as e:
            self.logger.warning(f"Failed to get archive info for {archive_path}: {e}")
        
        return info


class FileManager:
    """
    General file management utilities.
    
    Handles file copying, moving, deletion, and other operations
    with proper error handling and logging.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def copy_directory(self, source: Path, destination: Path,
                      progress_callback: Optional[Callable] = None) -> bool:
        """
        Copy a directory tree with progress tracking.
        
        Args:
            source: Source directory path
            destination: Destination directory path
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if copy successful, False otherwise
        """
        try:
            if not source.exists():
                raise FileUtilsError(f"Source directory does not exist: {source}")
            
            if not source.is_dir():
                raise FileUtilsError(f"Source is not a directory: {source}")
            
            self.logger.info(f"Copying directory: {source} -> {destination}")
            
            # Count total files for progress tracking
            total_files = sum(1 for _ in source.rglob('*') if _.is_file())
            copied_files = 0
            
            # Create destination directory
            destination.mkdir(parents=True, exist_ok=True)
            
            for item in source.rglob('*'):
                relative_path = item.relative_to(source)
                dest_path = destination / relative_path
                
                if item.is_dir():
                    dest_path.mkdir(parents=True, exist_ok=True)
                elif item.is_file():
                    try:
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
                        copied_files += 1
                        
                        if progress_callback:
                            progress_callback(copied_files, total_files)
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to copy {item}: {e}")
            
            self.logger.info(f"Directory copy completed: {copied_files}/{total_files} files")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy directory {source}: {e}")
            return False
    
    def safe_delete(self, path: Path, backup_suffix: str = '.backup') -> bool:
        """
        Safely delete a file or directory by creating a backup first.
        
        Args:
            path: Path to delete
            backup_suffix: Suffix for backup file/directory
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            if not path.exists():
                self.logger.warning(f"Path does not exist: {path}")
                return True
            
            # Create backup
            backup_path = path.with_suffix(path.suffix + backup_suffix)
            
            if path.is_file():
                shutil.copy2(path, backup_path)
            else:
                shutil.copytree(path, backup_path)
            
            # Delete original
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
            
            self.logger.info(f"Safely deleted {path} (backup: {backup_path})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to safely delete {path}: {e}")
            return False
    
    def calculate_checksum(self, file_path: Path, algorithm: str = 'sha256') -> Optional[str]:
        """
        Calculate checksum of a file.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256', 'sha512')
            
        Returns:
            Hexadecimal checksum string or None if failed
        """
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return None
    
    def verify_checksum(self, file_path: Path, expected_checksum: str, 
                       algorithm: str = 'sha256') -> bool:
        """
        Verify file checksum.
        
        Args:
            file_path: Path to the file
            expected_checksum: Expected checksum value
            algorithm: Hash algorithm used
            
        Returns:
            True if checksum matches, False otherwise
        """
        actual_checksum = self.calculate_checksum(file_path, algorithm)
        
        if actual_checksum is None:
            return False
        
        return actual_checksum.lower() == expected_checksum.lower()
    
    def cleanup_temp_files(self, temp_dir: Path, max_age_hours: int = 24) -> int:
        """
        Clean up old temporary files.
        
        Args:
            temp_dir: Temporary directory to clean
            max_age_hours: Maximum age of files to keep (in hours)
            
        Returns:
            Number of files deleted
        """
        import time
        
        deleted_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            if not temp_dir.exists():
                return 0
            
            for item in temp_dir.rglob('*'):
                if item.is_file():
                    try:
                        file_age = current_time - item.stat().st_mtime
                        if file_age > max_age_seconds:
                            item.unlink()
                            deleted_count += 1
                            self.logger.debug(f"Deleted old temp file: {item}")
                    except Exception as e:
                        self.logger.warning(f"Failed to delete temp file {item}: {e}")
            
            self.logger.info(f"Cleaned up {deleted_count} old temporary files")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp files in {temp_dir}: {e}")
            return 0


# Convenience functions
def create_backup_archive(source_path: Path, archive_path: Path,
                         progress_callback: Optional[Callable] = None) -> bool:
    """
    Convenience function to create a backup archive.
    
    Args:
        source_path: Path to backup
        archive_path: Where to create the archive
        progress_callback: Optional progress callback
        
    Returns:
        True if successful, False otherwise
    """
    manager = ArchiveManager()
    return manager.create_tar_archive(source_path, archive_path, 'gz', progress_callback)


def extract_backup_archive(archive_path: Path, extract_path: Path,
                          progress_callback: Optional[Callable] = None) -> bool:
    """
    Convenience function to extract a backup archive.
    
    Args:
        archive_path: Path to the archive
        extract_path: Where to extract
        progress_callback: Optional progress callback
        
    Returns:
        True if successful, False otherwise
    """
    manager = ArchiveManager()
    return manager.extract_tar_archive(archive_path, extract_path, progress_callback)
