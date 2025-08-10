"""
LumiSync v2.0 - Redesigned Main GUI Window
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
        QStatusBar, QFrame, QTabWidget, QTreeWidget, QTreeWidgetItem,
        QCheckBox, QComboBox, QSpinBox, QGroupBox, QGridLayout,
        QSplitter, QScrollArea, QTableWidget, QTableWidgetItem,
        QHeaderView, QLineEdit, QFileDialog, QSlider, QButtonGroup,
        QRadioButton, QToolButton, QMenu, QAction, QSystemTrayIcon,
        QListWidget, QListWidgetItem, QStackedWidget
    )
    from PyQt6.QtCore import (
        Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
        QEasingCurve, QRect, QSize, QPoint, QSettings, QUrl
    )
    from PyQt6.QtGui import (
        QFont, QIcon, QPalette, QColor, QPixmap, QPainter,
        QLinearGradient, QBrush, QFontMetrics, QDesktopServices
    )
except ImportError as e:
    raise ImportError(f"PyQt6 not installed: {e}. Run 'pip install PyQt6'")

from ..core.backup_manager import BackupManager
from ..core.restore_manager import RestoreManager
from ..core.cloud_providers.provider_factory import create_cloud_provider
from ..utils.logger import get_logger
from ..config.settings import GUI_SETTINGS
from .themes.lumi_setup_theme import LUMI_COLORS, FONTS, get_style

logger = get_logger(__name__)

class ConnectionStatus(Enum):
    """Cloud connection status states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class SyncCategory:
    """Represents a synchronization category"""
    id: str
    name: str
    description: str
    items: List[str]
    recommended: bool = False
    enabled: bool = True

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
        # For now, default to Google Drive
        self.connection_requested.emit("google_drive")
        
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
