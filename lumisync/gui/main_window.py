"""
Main GUI Window for LumiSync
Modern PyQt6 interface for Linux settings synchronization
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import logging

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
        QPushButton, QLabel, QTextEdit, QProgressBar, QMessageBox,
        QStatusBar, QFrame
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont
except ImportError as e:
    raise ImportError(f"PyQt6 not installed: {e}. Run 'pip install PyQt6'")

from ..core.backup_manager import BackupManager
from ..core.restore_manager import RestoreManager
from ..core.cloud_providers.provider_factory import create_cloud_provider
from ..utils.logger import get_logger
from ..config.settings import GUI_SETTINGS

# Import modern components
try:
    from .modern_main_window import (
        COLORS, InstallationStats, ModernProgressBar, ModernButton, 
        LogWidget, BackupThread, RestoreThread
    )
    MODERN_UI_AVAILABLE = True
except ImportError:
    MODERN_UI_AVAILABLE = False

logger = get_logger(__name__)


class BackupThread(QThread):
    """Background thread for backup operations."""
    
    progress_updated = pyqtSignal(int, int, str)
    backup_completed = pyqtSignal(dict)
    backup_failed = pyqtSignal(str)
    
    def __init__(self, cloud_provider_type: str = 'google_drive'):
        super().__init__()
        self.cloud_provider_type = cloud_provider_type
    
    def run(self):
        try:
            backup_manager = BackupManager(self.cloud_provider_type)
            backup_info = backup_manager.create_backup(
                lambda c, t, m: self.progress_updated.emit(c, t, m)
            )
            self.backup_completed.emit(backup_info)
        except Exception as e:
            self.backup_failed.emit(str(e))


class RestoreThread(QThread):
    """Background thread for restore operations."""
    
    progress_updated = pyqtSignal(int, int, str)
    restore_completed = pyqtSignal(dict)
    restore_failed = pyqtSignal(str)
    
    def __init__(self, cloud_provider_type: str = 'google_drive'):
        super().__init__()
        self.cloud_provider_type = cloud_provider_type
    
    def run(self):
        try:
            restore_manager = RestoreManager(self.cloud_provider_type)
            restore_info = restore_manager.restore_backup(
                None, lambda c, t, m: self.progress_updated.emit(c, t, m)
            )
            self.restore_completed.emit(restore_info)
        except Exception as e:
            self.restore_failed.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for LumiSync."""
    
    def __init__(self):
        super().__init__()
        self.cloud_provider = None
        self.backup_thread = None
        self.restore_thread = None
        self.init_ui()
        QTimer.singleShot(1000, self.check_cloud_connection)
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("LumiSync - Linux Settings Synchronization")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Status
        self.status_label = QLabel("☁️ Status: Nicht verbunden")
        self.status_label.setFont(QFont("Ubuntu", 12))
        main_layout.addWidget(self.status_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(separator)
        
        # Buttons
        self.connect_button = QPushButton("🔗 Mit Google Drive verbinden")
        self.connect_button.setMinimumHeight(50)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; color: white; border: none;
                border-radius: 8px; padding: 12px; font-size: 11pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:disabled { background-color: #BDBDBD; }
        """)
        main_layout.addWidget(self.connect_button)
        
        self.backup_button = QPushButton("📤 Einstellungen sichern")
        self.backup_button.setMinimumHeight(50)
        self.backup_button.setEnabled(False)
        self.backup_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; border: none;
                border-radius: 8px; padding: 12px; font-size: 11pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #388E3C; }
            QPushButton:disabled { background-color: #BDBDBD; }
        """)
        main_layout.addWidget(self.backup_button)
        
        self.restore_button = QPushButton("📥 Einstellungen wiederherstellen")
        self.restore_button.setMinimumHeight(50)
        self.restore_button.setEnabled(False)
        self.restore_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; color: white; border: none;
                border-radius: 8px; padding: 12px; font-size: 11pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #F57C00; }
            QPushButton:disabled { background-color: #BDBDBD; }
        """)
        main_layout.addWidget(self.restore_button)
        
        # Activity log
        log_label = QLabel("📋 Aktivitätslog:")
        log_label.setFont(QFont("Ubuntu", 10, QFont.Weight.Bold))
        main_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; border: 1px solid #dee2e6;
                border-radius: 4px; padding: 8px;
            }
        """)
        main_layout.addWidget(self.log_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        help_button = QPushButton("ℹ️ Hilfe")
        help_button.clicked.connect(self.show_help)
        exit_button = QPushButton("❌ Beenden")
        exit_button.clicked.connect(self.close)
        
        bottom_layout.addWidget(help_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(exit_button)
        main_layout.addLayout(bottom_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connect signals
        self.connect_button.clicked.connect(self.connect_to_cloud)
        self.backup_button.clicked.connect(self.start_backup)
        self.restore_button.clicked.connect(self.start_restore)
        
        self.add_log_message("Willkommen bei LumiSync! 🌟")
    
    def add_log_message(self, message: str, level: str = "info"):
        """Add message to activity log."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if level == "error":
            icon = "❌"
        elif level == "success":
            icon = "✅"
        else:
            icon = "ℹ️"
        
        self.log_text.append(f"[{timestamp}] {icon} {message}")
    
    def check_cloud_connection(self):
        """Check existing cloud connection."""
        try:
            self.cloud_provider = create_cloud_provider('google_drive')
            if self.cloud_provider.is_connected():
                user_info = self.cloud_provider.get_user_info()
                self.status_label.setText(f"☁️ Status: Verbunden mit {self.cloud_provider.provider_name}")
                self.backup_button.setEnabled(True)
                self.restore_button.setEnabled(True)
                self.connect_button.setText("✅ Verbunden")
                self.add_log_message("Bestehende Cloud-Verbindung erkannt", "success")
        except Exception:
            pass
    
    def connect_to_cloud(self):
        """Connect to cloud storage."""
        try:
            self.add_log_message("Verbinde mit Google Drive...")
            self.connect_button.setEnabled(False)
            
            self.cloud_provider = create_cloud_provider('google_drive')
            
            if self.cloud_provider.authenticate():
                user_info = self.cloud_provider.get_user_info()
                self.status_label.setText(f"☁️ Status: Verbunden mit {self.cloud_provider.provider_name}")
                self.add_log_message("Erfolgreich verbunden! ✅", "success")
                
                self.backup_button.setEnabled(True)
                self.restore_button.setEnabled(True)
                self.connect_button.setText("✅ Verbunden")
            else:
                raise Exception("Authentifizierung fehlgeschlagen")
                
        except Exception as e:
            self.add_log_message(f"Verbindung fehlgeschlagen: {e}", "error")
            self.connect_button.setEnabled(True)
            QMessageBox.critical(self, "Fehler", f"Verbindung fehlgeschlagen:\n{e}")
    
    def start_backup(self):
        """Start backup process."""
        reply = QMessageBox.question(self, "Backup erstellen",
                                   "Backup der Einstellungen erstellen?")
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.backup_button.setEnabled(False)
        self.restore_button.setEnabled(False)
        
        self.backup_thread = BackupThread('google_drive')
        self.backup_thread.progress_updated.connect(self.on_progress)
        self.backup_thread.backup_completed.connect(self.on_backup_completed)
        self.backup_thread.backup_failed.connect(self.on_backup_failed)
        self.backup_thread.start()
        
        self.add_log_message("Backup gestartet...")
    
    def start_restore(self):
        """Start restore process."""
        reply = QMessageBox.question(self, "Wiederherstellen",
                                   "Einstellungen wiederherstellen?\n\nWarnung: Überschreibt aktuelle Einstellungen!")
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.backup_button.setEnabled(False)
        self.restore_button.setEnabled(False)
        
        self.restore_thread = RestoreThread('google_drive')
        self.restore_thread.progress_updated.connect(self.on_progress)
        self.restore_thread.restore_completed.connect(self.on_restore_completed)
        self.restore_thread.restore_failed.connect(self.on_restore_failed)
        self.restore_thread.start()
        
        self.add_log_message("Wiederherstellung gestartet...")
    
    def on_progress(self, current: int, total: int, message: str):
        """Handle progress updates."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{message} ({current}/{total})")
    
    def on_backup_completed(self, backup_info: Dict[str, Any]):
        """Handle backup completion."""
        self.progress_bar.setVisible(False)
        self.add_log_message("Backup erfolgreich! 🎉", "success")
        QMessageBox.information(self, "Erfolg", "Backup erfolgreich erstellt!")
        self.backup_button.setEnabled(True)
        self.restore_button.setEnabled(True)
    
    def on_backup_failed(self, error: str):
        """Handle backup failure."""
        self.progress_bar.setVisible(False)
        self.add_log_message(f"Backup fehlgeschlagen: {error}", "error")
        QMessageBox.critical(self, "Fehler", f"Backup fehlgeschlagen:\n{error}")
        self.backup_button.setEnabled(True)
        self.restore_button.setEnabled(True)
    
    def on_restore_completed(self, restore_info: Dict[str, Any]):
        """Handle restore completion."""
        self.progress_bar.setVisible(False)
        self.add_log_message("Wiederherstellung erfolgreich! 🎉", "success")
        QMessageBox.information(self, "Erfolg", 
                              "Wiederherstellung erfolgreich!\n\nStarten Sie Anwendungen neu.")
        self.backup_button.setEnabled(True)
        self.restore_button.setEnabled(True)
    
    def on_restore_failed(self, error: str):
        """Handle restore failure."""
        self.progress_bar.setVisible(False)
        self.add_log_message(f"Wiederherstellung fehlgeschlagen: {error}", "error")
        QMessageBox.critical(self, "Fehler", f"Wiederherstellung fehlgeschlagen:\n{error}")
        self.backup_button.setEnabled(True)
        self.restore_button.setEnabled(True)
    
    def show_help(self):
        """Show help dialog."""
        QMessageBox.information(self, "Hilfe",
                              "LumiSync - Linux Settings Synchronization\n\n"
                              "1. Mit Google Drive verbinden\n"
                              "2. Einstellungen sichern\n"
                              "3. Auf anderem System wiederherstellen\n\n"
                              "Gesichert werden:\n"
                              "• Desktop-Einstellungen\n"
                              "• Firefox-Profil\n"
                              "• Thunderbird-Profil")


def create_application() -> QApplication:
    """Create the QApplication."""
    app = QApplication(sys.argv)
    app.setApplicationName("LumiSync")
    app.setApplicationVersion("0.1.0")
    return app
