"""
LumiSync v2.0 - Complete Redesigned Main GUI Window
Professional two-column layout with modern dark theme
Inspired by Lumi-Setup but optimized for synchronization tasks
"""

import sys
import json
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Set
import logging
from dataclasses import dataclass
from enum import Enum

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
        QPushButton, QLabel, QTextEdit, QProgressBar, QMessageBox,
        QStatusBar, QFrame, QTabWidget, QSplitter
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont, QIcon
except ImportError as e:
    raise ImportError(f"PyQt6 not installed: {e}. Run 'pip install PyQt6'")

from ..core.backup_manager import BackupManager
from ..core.restore_manager import RestoreManager
from ..core.cloud_providers.provider_factory import create_cloud_provider
from ..utils.logger import get_logger
from ..config.settings import GUI_SETTINGS
from .themes.lumi_setup_theme import LUMI_COLORS, FONTS, get_style
from .components.selection_pane import SelectionPaneWidget
from .components.tab_widgets import ProgressTabWidget, LogsTabWidget, SettingsTabWidget
from .components.provider_dialog import ProviderSelectionDialog

logger = get_logger(__name__)

class ConnectionStatus(Enum):
    """Cloud connection status states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class CloudConnectionWidget(QWidget):
    """Widget for managing cloud connection status and actions"""
    
    connection_requested = pyqtSignal(str)  # provider type
    disconnection_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = ConnectionStatus.DISCONNECTED
        self.connected_email = ""
        self.provider_type = ""
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Status section
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {LUMI_COLORS['bg_secondary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet(f"color: {LUMI_COLORS['accent_red']}; font-size: 16px;")
        
        self.status_label = QLabel("Status: Not Connected")
        self.status_label.setStyleSheet(f"color: {LUMI_COLORS['text_primary']}; font-weight: bold;")
        
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Connection button
        self.connect_btn = QPushButton("Connect to Cloud Storage")
        self.connect_btn.setMinimumHeight(40)
        self.connect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LUMI_COLORS['accent_cyan']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {LUMI_COLORS['accent_teal']};
            }}
            QPushButton:pressed {{
                background-color: {LUMI_COLORS['bg_tertiary']};
            }}
        """)
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        
        # Disconnect button (initially hidden)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setMinimumHeight(30)
        self.disconnect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LUMI_COLORS['bg_tertiary']};
                color: {LUMI_COLORS['text_secondary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 4px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {LUMI_COLORS['bg_hover']};
            }}
        """)
        self.disconnect_btn.clicked.connect(self.disconnection_requested.emit)
        self.disconnect_btn.hide()
        
        layout.addWidget(status_frame)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)
        
    def _on_connect_clicked(self):
        # Open provider selection dialog
        dialog = ProviderSelectionDialog(self)
        dialog.provider_connected.connect(self._on_provider_selected)
        dialog.exec()
        
    def _on_provider_selected(self, email: str, provider_type: str, provider_instance):
        """Handle provider selection from dialog"""
        self.connection_requested.emit(provider_type)
        
    def set_status(self, status: ConnectionStatus, email: str = "", provider: str = ""):
        self.status = status
        self.connected_email = email
        self.provider_type = provider
        
        if status == ConnectionStatus.DISCONNECTED:
            self.status_icon.setStyleSheet(f"color: {LUMI_COLORS['accent_red']}; font-size: 16px;")
            self.status_label.setText("Status: Not Connected")
            self.connect_btn.show()
            self.disconnect_btn.hide()
            
        elif status == ConnectionStatus.CONNECTING:
            self.status_icon.setStyleSheet(f"color: {LUMI_COLORS['accent_orange']}; font-size: 16px;")
            self.status_label.setText("Status: Connecting...")
            self.connect_btn.hide()
            self.disconnect_btn.hide()
            
        elif status == ConnectionStatus.CONNECTED:
            self.status_icon.setStyleSheet(f"color: {LUMI_COLORS['accent_green']}; font-size: 16px;")
            self.status_label.setText(f"Connected to: {email}")
            self.connect_btn.hide()
            self.disconnect_btn.show()
            
        elif status == ConnectionStatus.ERROR:
            self.status_icon.setStyleSheet(f"color: {LUMI_COLORS['accent_red']}; font-size: 16px;")
            self.status_label.setText("Status: Connection Error")
            self.connect_btn.show()
            self.disconnect_btn.hide()

class PrimaryActionsWidget(QWidget):
    """Widget for primary backup/restore actions"""
    
    backup_requested = pyqtSignal()
    restore_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.set_enabled(False)  # Initially disabled
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # Backup button
        self.backup_btn = QPushButton("🔄 Backup Settings")
        self.backup_btn.setMinimumHeight(50)
        self.backup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LUMI_COLORS['accent_green']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover:enabled {{
                background-color: {LUMI_COLORS['success']};
            }}
            QPushButton:disabled {{
                background-color: {LUMI_COLORS['bg_tertiary']};
                color: {LUMI_COLORS['text_muted']};
            }}
        """)
        self.backup_btn.clicked.connect(self.backup_requested.emit)
        
        # Restore button
        self.restore_btn = QPushButton("📥 Restore Settings")
        self.restore_btn.setMinimumHeight(50)
        self.restore_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LUMI_COLORS['bg_tertiary']};
                color: {LUMI_COLORS['text_primary']};
                border: 2px solid {LUMI_COLORS['border']};
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover:enabled {{
                background-color: {LUMI_COLORS['bg_hover']};
                border-color: {LUMI_COLORS['accent_cyan']};
            }}
            QPushButton:disabled {{
                background-color: {LUMI_COLORS['bg_tertiary']};
                color: {LUMI_COLORS['text_muted']};
                border-color: {LUMI_COLORS['border']};
            }}
        """)
        self.restore_btn.clicked.connect(self.restore_requested.emit)
        
        layout.addWidget(self.backup_btn, 2)  # Backup button gets more space
        layout.addWidget(self.restore_btn, 1)
        
    def set_enabled(self, enabled: bool):
        self.backup_btn.setEnabled(enabled)
        self.restore_btn.setEnabled(enabled)

class BackupThread(QThread):
    """Background thread for backup operations"""
    
    progress_updated = pyqtSignal(int, int, str)
    backup_completed = pyqtSignal(dict)
    backup_failed = pyqtSignal(str)
    
    def __init__(self, cloud_provider_type: str = 'google_drive', selected_categories: List[str] = None):
        super().__init__()
        self.cloud_provider_type = cloud_provider_type
        self.selected_categories = selected_categories or []
        self.is_paused = False
        self.should_stop = False
        
    def run(self):
        try:
            # Simulate backup process
            total_items = len(self.selected_categories) * 3  # Simulate multiple items per category
            
            for i, category in enumerate(self.selected_categories):
                if self.should_stop:
                    break
                    
                # Simulate processing items in category
                for j in range(3):
                    if self.should_stop:
                        break
                        
                    while self.is_paused:
                        self.msleep(100)
                        if self.should_stop:
                            break
                    
                    current_item = i * 3 + j + 1
                    message = f"Backing up {category} - item {j + 1}/3"
                    self.progress_updated.emit(current_item, total_items, message)
                    
                    # Simulate work
                    self.msleep(1000)
                    
            if not self.should_stop:
                self.backup_completed.emit({
                    'categories': self.selected_categories,
                    'total_items': total_items,
                    'timestamp': datetime.datetime.now()
                })
        except Exception as e:
            self.backup_failed.emit(str(e))
            
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False
        
    def stop(self):
        self.should_stop = True

class RestoreThread(QThread):
    """Background thread for restore operations"""
    
    progress_updated = pyqtSignal(int, int, str)
    restore_completed = pyqtSignal(dict)
    restore_failed = pyqtSignal(str)
    
    def __init__(self, cloud_provider_type: str = 'google_drive', selected_categories: List[str] = None):
        super().__init__()
        self.cloud_provider_type = cloud_provider_type
        self.selected_categories = selected_categories or []
        self.is_paused = False
        self.should_stop = False
        
    def run(self):
        try:
            # Simulate restore process
            total_items = len(self.selected_categories) * 3
            
            for i, category in enumerate(self.selected_categories):
                if self.should_stop:
                    break
                    
                for j in range(3):
                    if self.should_stop:
                        break
                        
                    while self.is_paused:
                        self.msleep(100)
                        if self.should_stop:
                            break
                    
                    current_item = i * 3 + j + 1
                    message = f"Restoring {category} - item {j + 1}/3"
                    self.progress_updated.emit(current_item, total_items, message)
                    
                    self.msleep(1000)
                    
            if not self.should_stop:
                self.restore_completed.emit({
                    'categories': self.selected_categories,
                    'total_items': total_items,
                    'timestamp': datetime.datetime.now()
                })
        except Exception as e:
            self.restore_failed.emit(str(e))
            
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False
        
    def stop(self):
        self.should_stop = True

class RedesignedMainWindow(QMainWindow):
    """Main application window with redesigned two-column layout"""
    
    def __init__(self):
        super().__init__()
        self.cloud_provider = None
        self.backup_thread = None
        self.restore_thread = None
        self.connection_status = ConnectionStatus.DISCONNECTED
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("LumiSync v2.0 - Linux Settings Synchronization")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Apply main window styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {LUMI_COLORS['bg_primary']};
                color: {LUMI_COLORS['text_primary']};
            }}
        """)
        
        # Central widget with splitter for two-column layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for resizable columns
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {LUMI_COLORS['border']};
                width: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {LUMI_COLORS['accent_cyan']};
            }}
        """)
        
        # Left column - Selection Pane (30% width)
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {LUMI_COLORS['bg_secondary']};
                border-right: 1px solid {LUMI_COLORS['border']};
            }}
        """)
        left_panel.setMinimumWidth(350)
        left_panel.setMaximumWidth(500)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.selection_pane = SelectionPaneWidget()
        left_layout.addWidget(self.selection_pane)
        
        # Right column - Action & Information Pane (70% width)
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {LUMI_COLORS['bg_primary']};
            }}
        """)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Top section: Cloud connection and primary actions (always visible)
        top_section = QFrame()
        top_section.setStyleSheet(f"""
            QFrame {{
                background-color: {LUMI_COLORS['bg_primary']};
                border-bottom: 1px solid {LUMI_COLORS['border']};
            }}
        """)
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 10, 0, 10)
        top_layout.setSpacing(10)
        
        # Cloud connection widget
        self.cloud_connection = CloudConnectionWidget()
        top_layout.addWidget(self.cloud_connection)
        
        # Primary actions widget
        self.primary_actions = PrimaryActionsWidget()
        top_layout.addWidget(self.primary_actions)
        
        # Bottom section: Tabbed layout
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {LUMI_COLORS['border']};
                background-color: {LUMI_COLORS['bg_primary']};
            }}
            QTabBar::tab {{
                background-color: {LUMI_COLORS['bg_secondary']};
                color: {LUMI_COLORS['text_primary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {LUMI_COLORS['bg_primary']};
                border-bottom: 2px solid {LUMI_COLORS['accent_cyan']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {LUMI_COLORS['bg_hover']};
            }}
        """)
        
        # Create tabs
        self.progress_tab = ProgressTabWidget()
        self.logs_tab = LogsTabWidget()
        self.settings_tab = SettingsTabWidget()
        
        self.tab_widget.addTab(self.progress_tab, "Progress")
        self.tab_widget.addTab(self.logs_tab, "Logs")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        right_layout.addWidget(top_section)
        right_layout.addWidget(self.tab_widget, 1)  # Tab widget takes remaining space
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 1050])  # Set initial sizes (30% / 70%)
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {LUMI_COLORS['bg_secondary']};
                color: {LUMI_COLORS['text_secondary']};
                border-top: 1px solid {LUMI_COLORS['border']};
            }}
        """)
        self.status_bar.showMessage("Ready - Select items to synchronize and connect to cloud storage")
        self.setStatusBar(self.status_bar)
        
    def _connect_signals(self):
        """Connect widget signals"""
        # Selection pane signals
        self.selection_pane.selection_changed.connect(self._on_selection_changed)
        
        # Cloud connection signals
        self.cloud_connection.connection_requested.connect(self._connect_to_cloud)
        self.cloud_connection.disconnection_requested.connect(self._disconnect_from_cloud)
        
        # Primary action signals
        self.primary_actions.backup_requested.connect(self._start_backup)
        self.primary_actions.restore_requested.connect(self._start_restore)
        
        # Progress tab signals
        self.progress_tab.pause_requested.connect(self._pause_operation)
        self.progress_tab.resume_requested.connect(self._resume_operation)
        self.progress_tab.stop_requested.connect(self._stop_operation)
        
    def _on_selection_changed(self):
        """Handle selection changes"""
        has_selection = self.selection_pane.has_selection()
        is_connected = self.connection_status == ConnectionStatus.CONNECTED
        
        # Enable/disable primary actions based on selection and connection
        self.primary_actions.set_enabled(has_selection and is_connected)
        
        if has_selection and is_connected:
            self.status_bar.showMessage("Ready to backup or restore selected items")
        elif has_selection:
            self.status_bar.showMessage("Connect to cloud storage to enable backup/restore")
        elif is_connected:
            self.status_bar.showMessage("Select items to synchronize")
        else:
            self.status_bar.showMessage("Select items and connect to cloud storage")
            
    def _connect_to_cloud(self, provider_type: str):
        """Connect to cloud storage"""
        try:
            self.cloud_connection.set_status(ConnectionStatus.CONNECTING)
            
            # Open provider selection dialog for real authentication
            dialog = ProviderSelectionDialog(self)
            dialog.provider_connected.connect(self._on_real_connection_success)
            dialog.exec()
                
        except Exception as e:
            logger.error(f"Cloud connection error: {str(e)}")
            self.cloud_connection.set_status(ConnectionStatus.ERROR)
            
    def _on_real_connection_success(self, email: str, provider_type: str, provider_instance):
        """Handle successful real-world connection"""
        self.cloud_provider = provider_instance
        self._on_connection_success(email, provider_type.replace('_', ' ').title())
        
    def _on_connection_success(self, email: str, provider: str):
        """Handle successful cloud connection"""
        self.connection_status = ConnectionStatus.CONNECTED
        self.cloud_connection.set_status(ConnectionStatus.CONNECTED, email, provider)
        self.logs_tab.add_log(f"Connected to {provider} as {email}", "INFO")
        self.logs_tab.add_log("Lumi-Sync folder created/verified in cloud storage", "INFO")
        self.status_bar.showMessage(f"Connected to {provider}")
        self._on_selection_changed()  # Update button states
        
    def _disconnect_from_cloud(self):
        """Disconnect from cloud storage"""
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.cloud_connection.set_status(ConnectionStatus.DISCONNECTED)
        self.logs_tab.add_log("Disconnected from cloud storage", "INFO")
        self._on_selection_changed()  # Update button states
        
    def _start_backup(self):
        """Start backup process"""
        selected_categories = self.selection_pane.get_selected_categories()
        if not selected_categories:
            QMessageBox.warning(self, "No Selection", "Please select items to backup.")
            return
            
        self.logs_tab.add_log(f"Starting backup of {len(selected_categories)} categories", "INFO")
        self.tab_widget.setCurrentIndex(0)  # Switch to Progress tab
        
        # Start backup thread
        self.backup_thread = BackupThread("google_drive", selected_categories)
        self.backup_thread.progress_updated.connect(self.progress_tab.update_progress)
        self.backup_thread.backup_completed.connect(self._on_backup_completed)
        self.backup_thread.backup_failed.connect(self._on_backup_failed)
        
        self.progress_tab.start_operation(len(selected_categories) * 3)
        self.backup_thread.start()
        
    def _start_restore(self):
        """Start restore process"""
        selected_categories = self.selection_pane.get_selected_categories()
        if not selected_categories:
            QMessageBox.warning(self, "No Selection", "Please select items to restore.")
            return
            
        self.logs_tab.add_log(f"Starting restore of {len(selected_categories)} categories", "INFO")
        self.tab_widget.setCurrentIndex(0)  # Switch to Progress tab
        
        # Start restore thread
        self.restore_thread = RestoreThread("google_drive", selected_categories)
        self.restore_thread.progress_updated.connect(self.progress_tab.update_progress)
        self.restore_thread.restore_completed.connect(self._on_restore_completed)
        self.restore_thread.restore_failed.connect(self._on_restore_failed)
        
        self.progress_tab.start_operation(len(selected_categories) * 3)
        self.restore_thread.start()
        
    def _pause_operation(self):
        """Pause current operation"""
        if self.backup_thread and self.backup_thread.isRunning():
            self.backup_thread.pause()
            self.logs_tab.add_log("Backup paused", "INFO")
        elif self.restore_thread and self.restore_thread.isRunning():
            self.restore_thread.pause()
            self.logs_tab.add_log("Restore paused", "INFO")
            
    def _resume_operation(self):
        """Resume current operation"""
        if self.backup_thread and self.backup_thread.isRunning():
            self.backup_thread.resume()
            self.logs_tab.add_log("Backup resumed", "INFO")
        elif self.restore_thread and self.restore_thread.isRunning():
            self.restore_thread.resume()
            self.logs_tab.add_log("Restore resumed", "INFO")
            
    def _stop_operation(self):
        """Stop current operation"""
        if self.backup_thread and self.backup_thread.isRunning():
            self.backup_thread.stop()
            self.logs_tab.add_log("Backup stopped", "WARNING")
        elif self.restore_thread and self.restore_thread.isRunning():
            self.restore_thread.stop()
            self.logs_tab.add_log("Restore stopped", "WARNING")
            
    def _on_backup_completed(self, backup_info: Dict[str, Any]):
        """Handle backup completion"""
        self.logs_tab.add_log("Backup completed successfully", "INFO")
        self.progress_tab.last_backup_label.setText(
            backup_info['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        )
        QMessageBox.information(self, "Backup Complete", "Settings backup completed successfully!")
        
    def _on_backup_failed(self, error: str):
        """Handle backup failure"""
        self.logs_tab.add_log(f"Backup failed: {error}", "ERROR")
        QMessageBox.critical(self, "Backup Failed", f"Backup failed: {error}")
        
    def _on_restore_completed(self, restore_info: Dict[str, Any]):
        """Handle restore completion"""
        self.logs_tab.add_log("Restore completed successfully", "INFO")
        QMessageBox.information(self, "Restore Complete", "Settings restore completed successfully!")
        
    def _on_restore_failed(self, error: str):
        """Handle restore failure"""
        self.logs_tab.add_log(f"Restore failed: {error}", "ERROR")
        QMessageBox.critical(self, "Restore Failed", f"Restore failed: {error}")

def create_application():
    """Create and configure the QApplication"""
    app = QApplication(sys.argv)
    app.setApplicationName("LumiSync")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("LumiSync")
    
    # Apply dark theme
    from .themes.lumi_setup_theme import apply_dark_palette
    apply_dark_palette(app)
    
    return app

def main():
    """Main entry point"""
    app = create_application()
    window = RedesignedMainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
