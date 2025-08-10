"""
Modern Main GUI Window for LumiSync
Professional dark theme interface with tabbed layout and advanced features
"""

import sys
import json
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
from dataclasses import dataclass

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
        QPushButton, QLabel, QTextEdit, QProgressBar, QMessageBox,
        QStatusBar, QFrame, QTabWidget, QTreeWidget, QTreeWidgetItem,
        QCheckBox, QComboBox, QSpinBox, QGroupBox, QGridLayout,
        QSplitter, QScrollArea, QTableWidget, QTableWidgetItem,
        QHeaderView, QLineEdit, QFileDialog, QSlider, QButtonGroup,
        QRadioButton, QToolButton, QMenu, QAction, QSystemTrayIcon
    )
    from PyQt6.QtCore import (
        Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
        QEasingCurve, QRect, QSize, QPoint, QSettings
    )
    from PyQt6.QtGui import (
        QFont, QIcon, QPalette, QColor, QPixmap, QPainter,
        QLinearGradient, QBrush, QFontMetrics
    )
except ImportError as e:
    raise ImportError(f"PyQt6 not installed: {e}. Run 'pip install PyQt6'")

from ..core.backup_manager import BackupManager
from ..core.restore_manager import RestoreManager
from ..core.cloud_providers.provider_factory import create_cloud_provider
from ..utils.logger import get_logger
from ..config.settings import GUI_SETTINGS

logger = get_logger(__name__)

# Modern color scheme
COLORS = {
    'bg_primary': '#1e1e2e',      # Dark background
    'bg_secondary': '#313244',     # Secondary background
    'bg_tertiary': '#45475a',      # Tertiary background
    'accent_blue': '#89b4fa',      # Blue accent
    'accent_green': '#a6e3a1',     # Green accent
    'accent_orange': '#fab387',    # Orange accent
    'accent_red': '#f38ba8',       # Red accent
    'text_primary': '#cdd6f4',     # Primary text
    'text_secondary': '#bac2de',   # Secondary text
    'text_muted': '#6c7086',       # Muted text
    'border': '#585b70',           # Border color
    'success': '#a6e3a1',          # Success color
    'warning': '#f9e2af',          # Warning color
    'error': '#f38ba8',            # Error color
}

@dataclass
class InstallationStats:
    """Statistics for installation process."""
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    
    @property
    def success_rate(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100
    
    @property
    def duration(self) -> Optional[datetime.timedelta]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class ModernProgressBar(QProgressBar):
    """Custom progress bar with modern styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['bg_secondary']};
                text-align: center;
                color: {COLORS['text_primary']};
                font-weight: bold;
                font-size: 11px;
                min-height: 20px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['accent_blue']}, stop:1 {COLORS['accent_green']});
                border-radius: 6px;
                margin: 1px;
            }}
        """)


class ModernButton(QPushButton):
    """Custom button with modern styling and animations."""
    
    def __init__(self, text: str, button_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self._setup_style()
    
    def _setup_style(self):
        """Setup button styling based on type."""
        styles = {
            'primary': f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {COLORS['accent_blue']}, stop:1 #74c0fc);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #74c0fc, stop:1 {COLORS['accent_blue']});
                }}
                QPushButton:pressed {{
                    background: {COLORS['accent_blue']};
                }}
                QPushButton:disabled {{
                    background: {COLORS['bg_tertiary']};
                    color: {COLORS['text_muted']};
                }}
            """,
            'success': f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {COLORS['accent_green']}, stop:1 #94d82d);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #94d82d, stop:1 {COLORS['accent_green']});
                }}
            """,
            'warning': f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {COLORS['accent_orange']}, stop:1 #fd7e14);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #fd7e14, stop:1 {COLORS['accent_orange']});
                }}
            """,
            'danger': f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {COLORS['accent_red']}, stop:1 #e03131);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e03131, stop:1 {COLORS['accent_red']});
                }}
            """,
            'secondary': f"""
                QPushButton {{
                    background: {COLORS['bg_secondary']};
                    color: {COLORS['text_primary']};
                    border: 2px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: {COLORS['bg_tertiary']};
                    border-color: {COLORS['accent_blue']};
                }}
            """
        }
        
        self.setStyleSheet(styles.get(self.button_type, styles['primary']))


class LogWidget(QTextEdit):
    """Advanced logging widget with filtering and export capabilities."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        self.current_filter = 'ALL'
        self.log_entries = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the logging widget UI."""
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 9))
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                selection-background-color: {COLORS['accent_blue']};
            }}
        """)
    
    def add_log(self, message: str, level: str = "INFO", timestamp: Optional[datetime.datetime] = None):
        """Add a log entry with timestamp and level."""
        if timestamp is None:
            timestamp = datetime.datetime.now()
        
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message
        }
        
        self.log_entries.append(log_entry)
        self._update_display()
    
    def _update_display(self):
        """Update the display based on current filter."""
        self.clear()
        
        for entry in self.log_entries:
            if self.current_filter == 'ALL' or entry['level'] == self.current_filter:
                self._append_formatted_entry(entry)
    
    def _append_formatted_entry(self, entry: Dict[str, Any]):
        """Append a formatted log entry to the display."""
        timestamp_str = entry['timestamp'].strftime("%H:%M:%S")
        level = entry['level']
        message = entry['message']
        
        # Color coding for different log levels
        colors = {
            'DEBUG': COLORS['text_muted'],
            'INFO': COLORS['accent_blue'],
            'WARNING': COLORS['accent_orange'],
            'ERROR': COLORS['accent_red']
        }
        
        color = colors.get(level, COLORS['text_primary'])
        
        formatted_entry = f"""
        <div style="margin: 2px 0; padding: 4px; border-left: 3px solid {color};">
            <span style="color: {COLORS['text_muted']};">[{timestamp_str}]</span>
            <span style="color: {color}; font-weight: bold;">[{level}]</span>
            <span style="color: {COLORS['text_primary']};">{message}</span>
        </div>
        """
        
        self.insertHtml(formatted_entry)
        self.moveCursor(self.textCursor().End)
    
    def set_filter(self, level: str):
        """Set the log level filter."""
        self.current_filter = level.upper()
        self._update_display()
    
    def export_logs(self, filepath: str):
        """Export logs to a file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("LumiSync Log Export\n")
                f.write("=" * 50 + "\n\n")
                
                for entry in self.log_entries:
                    timestamp_str = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{timestamp_str}] [{entry['level']}] {entry['message']}\n")
            
            return True
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            return False


class BackupThread(QThread):
    """Enhanced background thread for backup operations."""
    
    progress_updated = pyqtSignal(int, int, str)
    backup_completed = pyqtSignal(dict)
    backup_failed = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self, cloud_provider_type: str = 'google_drive', selected_categories: List[str] = None):
        super().__init__()
        self.cloud_provider_type = cloud_provider_type
        self.selected_categories = selected_categories or []
        self.is_paused = False
        self.should_stop = False
    
    def run(self):
        try:
            self.status_changed.emit("Initializing backup...")
            backup_manager = BackupManager(self.cloud_provider_type)
            
            backup_info = backup_manager.create_backup(
                progress_callback=self._progress_callback,
                categories=self.selected_categories
            )
            
            if not self.should_stop:
                self.backup_completed.emit(backup_info)
        except Exception as e:
            self.backup_failed.emit(str(e))
    
    def _progress_callback(self, current: int, total: int, message: str):
        """Handle progress updates with pause/stop support."""
        while self.is_paused and not self.should_stop:
            self.msleep(100)
        
        if self.should_stop:
            return False
        
        self.progress_updated.emit(current, total, message)
        return True
    
    def pause(self):
        """Pause the backup process."""
        self.is_paused = True
        self.status_changed.emit("Backup paused")
    
    def resume(self):
        """Resume the backup process."""
        self.is_paused = False
        self.status_changed.emit("Backup resumed")
    
    def stop(self):
        """Stop the backup process."""
        self.should_stop = True
        self.status_changed.emit("Backup stopped")


class RestoreThread(QThread):
    """Enhanced background thread for restore operations."""
    
    progress_updated = pyqtSignal(int, int, str)
    restore_completed = pyqtSignal(dict)
    restore_failed = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self, cloud_provider_type: str = 'google_drive', selected_categories: List[str] = None):
        super().__init__()
        self.cloud_provider_type = cloud_provider_type
        self.selected_categories = selected_categories or []
        self.is_paused = False
        self.should_stop = False
    
    def run(self):
        try:
            self.status_changed.emit("Initializing restore...")
            restore_manager = RestoreManager(self.cloud_provider_type)
            
            restore_info = restore_manager.restore_backup(
                progress_callback=self._progress_callback,
                categories=self.selected_categories
            )
            
            if not self.should_stop:
                self.restore_completed.emit(restore_info)
        except Exception as e:
            self.restore_failed.emit(str(e))
    
    def _progress_callback(self, current: int, total: int, message: str):
        """Handle progress updates with pause/stop support."""
        while self.is_paused and not self.should_stop:
            self.msleep(100)
        
        if self.should_stop:
            return False
        
        self.progress_updated.emit(current, total, message)
        return True
    
    def pause(self):
        """Pause the restore process."""
        self.is_paused = True
        self.status_changed.emit("Restore paused")
    
    def resume(self):
        """Resume the restore process."""
        self.is_paused = False
        self.status_changed.emit("Restore resumed")
    
    def stop(self):
        """Stop the restore process."""
        self.should_stop = True
        self.status_changed.emit("Restore stopped")


def create_application():
    """Create the QApplication with modern styling."""
    app = QApplication(sys.argv)
    app.setApplicationName("LumiSync")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("LumiSync")
    
    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("assets/icon.png"))
    except:
        pass
    
    return app
