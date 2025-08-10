"""
Cloud Provider Selection and Authentication Dialog
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFormLayout, QFrame, QMessageBox,
    QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from ..themes.lumi_setup_theme import LUMI_COLORS
from ...core.cloud_providers.provider_factory import CloudProviderFactory


class AuthenticationThread(QThread):
    """Background thread for cloud provider authentication"""
    
    auth_success = pyqtSignal(str, str, object)  # email, provider_type, provider_instance
    auth_failed = pyqtSignal(str)  # error message
    
    def __init__(self, provider_type: str, credentials: Dict[str, Any]):
        super().__init__()
        self.provider_type = provider_type
        self.credentials = credentials
        
    def run(self):
        try:
            provider = CloudProviderFactory.create_provider(self.provider_type)
            
            if provider.authenticate(**self.credentials):
                user_info = provider.get_user_info()
                email = user_info.get('email', 'Unknown')
                self.auth_success.emit(email, self.provider_type, provider)
            else:
                self.auth_failed.emit("Authentication failed")
                
        except Exception as e:
            self.auth_failed.emit(str(e))


class ProviderSelectionDialog(QDialog):
    """Dialog for selecting and authenticating with cloud providers"""
    
    provider_connected = pyqtSignal(str, str, object)  # email, provider_type, provider_instance
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_thread = None
        self.setWindowTitle("Connect to Cloud Storage")
        self.setFixedSize(500, 400)
        self.setModal(True)
        self._setup_ui()
        self._setup_styles()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Connect to Cloud Storage")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Provider selection
        provider_frame = QFrame()
        provider_layout = QFormLayout(provider_frame)
        
        self.provider_combo = QComboBox()
        available_providers = CloudProviderFactory.get_available_providers()
        for key, name in available_providers.items():
            self.provider_combo.addItem(name, key)
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        
        provider_layout.addRow("Cloud Provider:", self.provider_combo)
        layout.addWidget(provider_frame)
        
        # Authentication form
        self.auth_frame = QFrame()
        self.auth_layout = QFormLayout(self.auth_frame)
        layout.addWidget(self.auth_frame)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        self.connect_btn.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.connect_btn)
        
        layout.addLayout(button_layout)
        
        # Initialize with first provider
        self._on_provider_changed()
        
    def _setup_styles(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {LUMI_COLORS['bg_primary']};
                color: {LUMI_COLORS['text_primary']};
            }}
            QLabel {{
                color: {LUMI_COLORS['text_primary']};
            }}
            QComboBox {{
                background-color: {LUMI_COLORS['bg_secondary']};
                color: {LUMI_COLORS['text_primary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                min-height: 20px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {LUMI_COLORS['text_secondary']};
            }}
            QLineEdit {{
                background-color: {LUMI_COLORS['bg_secondary']};
                color: {LUMI_COLORS['text_primary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border-color: {LUMI_COLORS['accent_cyan']};
            }}
            QPushButton {{
                background-color: {LUMI_COLORS['bg_tertiary']};
                color: {LUMI_COLORS['text_primary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {LUMI_COLORS['bg_hover']};
            }}
            QPushButton[default="true"] {{
                background-color: {LUMI_COLORS['accent_cyan']};
                color: white;
                border: none;
            }}
            QPushButton[default="true"]:hover {{
                background-color: {LUMI_COLORS['accent_teal']};
            }}
            QFrame {{
                background-color: {LUMI_COLORS['bg_secondary']};
                border: 1px solid {LUMI_COLORS['border_light']};
                border-radius: 8px;
                padding: 15px;
            }}
            QProgressBar {{
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {LUMI_COLORS['accent_cyan']};
                border-radius: 3px;
            }}
        """)
        
    def _on_provider_changed(self):
        """Update authentication form based on selected provider"""
        # Clear existing form
        while self.auth_layout.count():
            child = self.auth_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        provider_key = self.provider_combo.currentData()
        
        if provider_key == 'google_drive':
            self._setup_google_drive_form()
        elif provider_key == 'pcloud':
            self._setup_pcloud_form()
            
    def _setup_google_drive_form(self):
        """Setup form for Google Drive authentication"""
        info_label = QLabel(
            "Google Drive uses OAuth 2.0 authentication.\n"
            "Click Connect to open the authentication flow in your browser."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {LUMI_COLORS['text_secondary']}; font-size: 11px;")
        self.auth_layout.addRow(info_label)
        
    def _setup_pcloud_form(self):
        """Setup form for pCloud authentication"""
        info_label = QLabel("Enter your pCloud credentials:")
        info_label.setStyleSheet(f"color: {LUMI_COLORS['text_secondary']}; font-size: 11px;")
        self.auth_layout.addRow(info_label)
        
        self.pcloud_username = QLineEdit()
        self.pcloud_username.setPlaceholderText("Enter your pCloud email/username")
        self.auth_layout.addRow("Username:", self.pcloud_username)
        
        self.pcloud_password = QLineEdit()
        self.pcloud_password.setPlaceholderText("Enter your pCloud password")
        self.pcloud_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.auth_layout.addRow("Password:", self.pcloud_password)
        
    def _on_connect_clicked(self):
        """Handle connect button click"""
        provider_key = self.provider_combo.currentData()
        
        if provider_key == 'google_drive':
            self._connect_google_drive()
        elif provider_key == 'pcloud':
            self._connect_pcloud()
            
    def _connect_google_drive(self):
        """Connect to Google Drive"""
        self._start_authentication('google_drive', {})
        
    def _connect_pcloud(self):
        """Connect to pCloud"""
        username = getattr(self, 'pcloud_username', None)
        password = getattr(self, 'pcloud_password', None)
        
        if not username or not password:
            QMessageBox.warning(self, "Missing Credentials", 
                              "Please enter both username and password for pCloud.")
            return
            
        if not username.text().strip() or not password.text().strip():
            QMessageBox.warning(self, "Missing Credentials", 
                              "Please enter both username and password for pCloud.")
            return
            
        credentials = {
            'username': username.text().strip(),
            'password': password.text().strip()
        }
        
        self._start_authentication('pcloud', credentials)
        
    def _start_authentication(self, provider_type: str, credentials: Dict[str, Any]):
        """Start authentication process"""
        self.connect_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText("Connecting...")
        self.status_label.setStyleSheet(f"color: {LUMI_COLORS['text_secondary']};")
        
        self.auth_thread = AuthenticationThread(provider_type, credentials)
        self.auth_thread.auth_success.connect(self._on_auth_success)
        self.auth_thread.auth_failed.connect(self._on_auth_failed)
        self.auth_thread.start()
        
    def _on_auth_success(self, email: str, provider_type: str, provider_instance):
        """Handle successful authentication"""
        self.progress_bar.hide()
        self.status_label.setText(f"Successfully connected to {email}")
        self.status_label.setStyleSheet(f"color: {LUMI_COLORS['accent_green']};")
        
        # Emit signal and close dialog
        self.provider_connected.emit(email, provider_type, provider_instance)
        self.accept()
        
    def _on_auth_failed(self, error: str):
        """Handle authentication failure"""
        self.connect_btn.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText(f"Connection failed: {error}")
        self.status_label.setStyleSheet(f"color: {LUMI_COLORS['accent_red']};")
        
        QMessageBox.critical(self, "Connection Failed", 
                           f"Failed to connect to cloud storage:\n\n{error}")
