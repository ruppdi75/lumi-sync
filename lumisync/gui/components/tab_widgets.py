"""
Tab Widgets for LumiSync v2.0 Action & Information Pane
Progress, Logs, and Settings tabs
"""

import datetime
from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QProgressBar, QGroupBox, QGridLayout, QTextEdit,
    QComboBox, QFileDialog, QCheckBox, QSpinBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from ..themes.lumi_setup_theme import LUMI_COLORS

class ProgressTabWidget(QWidget):
    """Progress tab showing backup/restore progress"""
    
    pause_requested = pyqtSignal()
    resume_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self._setup_ui()
        self.reset()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Overall progress section
        overall_group = QGroupBox("Overall Progress")
        overall_group.setStyleSheet(f"""
            QGroupBox {{
                color: {LUMI_COLORS['text_primary']};
                font-weight: bold;
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        overall_layout = QVBoxLayout(overall_group)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimumHeight(25)
        self.overall_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {LUMI_COLORS['border']};
                border-radius: 8px;
                background-color: {LUMI_COLORS['bg_secondary']};
                text-align: center;
                color: {LUMI_COLORS['text_primary']};
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {LUMI_COLORS['accent_cyan']}, stop:1 {LUMI_COLORS['accent_teal']});
                border-radius: 6px;
                margin: 1px;
            }}
        """)
        
        overall_layout.addWidget(self.overall_progress)
        
        # Current item section
        current_group = QGroupBox("Current Item")
        current_group.setStyleSheet(f"""
            QGroupBox {{
                color: {LUMI_COLORS['text_primary']};
                font-weight: bold;
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        current_layout = QVBoxLayout(current_group)
        
        self.current_item_label = QLabel("Ready to start...")
        self.current_item_label.setStyleSheet(f"""
            color: {LUMI_COLORS['text_primary']};
            font-size: 12px;
            padding: 5px;
        """)
        
        self.current_progress = QProgressBar()
        self.current_progress.setMinimumHeight(20)
        self.current_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 6px;
                background-color: {LUMI_COLORS['bg_secondary']};
                text-align: center;
                color: {LUMI_COLORS['text_primary']};
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {LUMI_COLORS['accent_green']};
                border-radius: 5px;
                margin: 1px;
            }}
        """)
        
        current_layout.addWidget(self.current_item_label)
        current_layout.addWidget(self.current_progress)
        
        # Statistics section
        stats_group = QGroupBox("Statistics")
        stats_group.setStyleSheet(f"""
            QGroupBox {{
                color: {LUMI_COLORS['text_primary']};
                font-weight: bold;
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        stats_layout = QGridLayout(stats_group)
        
        # Statistics labels
        value_style = f"color: {LUMI_COLORS['text_primary']}; font-weight: bold; font-size: 11px;"
        
        stats_layout.addWidget(QLabel("Completed:"), 0, 0)
        self.completed_label = QLabel("0 / 0 items")
        self.completed_label.setStyleSheet(value_style)
        stats_layout.addWidget(self.completed_label, 0, 1)
        
        stats_layout.addWidget(QLabel("Time Elapsed:"), 1, 0)
        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet(value_style)
        stats_layout.addWidget(self.time_label, 1, 1)
        
        stats_layout.addWidget(QLabel("Last Backup:"), 2, 0)
        self.last_backup_label = QLabel("Never")
        self.last_backup_label.setStyleSheet(value_style)
        stats_layout.addWidget(self.last_backup_label, 2, 1)
        
        # Control buttons
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 10, 0, 0)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.resume_btn = QPushButton("▶ Resume")
        self.stop_btn = QPushButton("⏹ Stop")
        
        for btn in [self.pause_btn, self.resume_btn, self.stop_btn]:
            btn.setMinimumHeight(35)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {LUMI_COLORS['bg_tertiary']};
                    color: {LUMI_COLORS['text_primary']};
                    border: 1px solid {LUMI_COLORS['border']};
                    border-radius: 4px;
                    font-size: 11px;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    background-color: {LUMI_COLORS['bg_hover']};
                }}
                QPushButton:disabled {{
                    color: {LUMI_COLORS['text_muted']};
                    background-color: {LUMI_COLORS['bg_secondary']};
                }}
            """)
            
        self.pause_btn.clicked.connect(self.pause_requested.emit)
        self.resume_btn.clicked.connect(self.resume_requested.emit)
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        self.resume_btn.hide()  # Initially hidden
        
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.resume_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addStretch()
        
        layout.addWidget(overall_group)
        layout.addWidget(current_group)
        layout.addWidget(stats_group)
        layout.addWidget(controls_frame)
        layout.addStretch()
        
    def reset(self):
        """Reset progress to initial state"""
        self.overall_progress.setValue(0)
        self.current_progress.setValue(0)
        self.current_item_label.setText("Ready to start...")
        self.completed_label.setText("0 / 0 items")
        self.time_label.setText("00:00")
        self.timer.stop()
        self._hide_controls()
        
    def start_operation(self, total_items: int):
        """Start a new operation"""
        self.overall_progress.setMaximum(total_items)
        self.overall_progress.setValue(0)
        self.completed_label.setText(f"0 / {total_items} items")
        self.start_time = datetime.datetime.now()
        self.timer.start(1000)  # Update every second
        self._show_controls()
        
    def update_progress(self, current: int, total: int, message: str):
        """Update progress information"""
        self.overall_progress.setValue(current)
        self.current_item_label.setText(message)
        self.completed_label.setText(f"{current} / {total} items")
        
    def _update_time(self):
        """Update elapsed time display"""
        if self.start_time:
            elapsed = datetime.datetime.now() - self.start_time
            minutes, seconds = divmod(int(elapsed.total_seconds()), 60)
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        
    def _show_controls(self):
        """Show operation control buttons"""
        self.pause_btn.show()
        self.stop_btn.show()
        
    def _hide_controls(self):
        """Hide operation control buttons"""
        self.pause_btn.hide()
        self.resume_btn.hide()
        self.stop_btn.hide()

class LogsTabWidget(QWidget):
    """Logs tab with filtering and export capabilities"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_entries = []
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Filter controls
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet(f"color: {LUMI_COLORS['text_primary']};")
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Info", "Warning", "Error"])
        self.filter_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {LUMI_COLORS['bg_secondary']};
                color: {LUMI_COLORS['text_primary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
        """)
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        
        self.export_btn = QPushButton("Export Logs")
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LUMI_COLORS['bg_tertiary']};
                color: {LUMI_COLORS['text_primary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 4px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: {LUMI_COLORS['bg_hover']};
            }}
        """)
        self.export_btn.clicked.connect(self._export_logs)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(self.export_btn)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {LUMI_COLORS['bg_secondary']};
                color: {LUMI_COLORS['text_primary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                padding: 10px;
            }}
        """)
        
        layout.addWidget(filter_frame)
        layout.addWidget(self.log_display)
        
    def add_log(self, message: str, level: str = "INFO", timestamp: datetime.datetime = None):
        """Add a log entry"""
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message
        }
        self.log_entries.append(entry)
        self._update_display()
        
    def _update_display(self):
        """Update the log display based on current filter"""
        filter_level = self.filter_combo.currentText()
        
        display_text = ""
        for entry in self.log_entries:
            if filter_level == "All" or entry['level'] == filter_level.upper():
                timestamp_str = entry['timestamp'].strftime("%H:%M:%S")
                level_color = self._get_level_color(entry['level'])
                display_text += f"<span style='color: {LUMI_COLORS['text_secondary']}'>[{timestamp_str}]</span> "
                display_text += f"<span style='color: {level_color}'>{entry['level']}</span>: "
                display_text += f"<span style='color: {LUMI_COLORS['text_primary']}'>{entry['message']}</span><br>"
                
        self.log_display.setHtml(display_text)
        # Scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def _get_level_color(self, level: str) -> str:
        """Get color for log level"""
        colors = {
            'INFO': LUMI_COLORS['info'],
            'WARNING': LUMI_COLORS['warning'],
            'ERROR': LUMI_COLORS['error'],
            'DEBUG': LUMI_COLORS['text_secondary']
        }
        return colors.get(level, LUMI_COLORS['text_primary'])
        
    def _apply_filter(self):
        """Apply the selected filter"""
        self._update_display()
        
    def _export_logs(self):
        """Export logs to a file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "lumisync_logs.txt", "Text Files (*.txt)"
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    for entry in self.log_entries:
                        timestamp_str = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp_str}] {entry['level']}: {entry['message']}\n")
                self.add_log(f"Logs exported to {filename}", "INFO")
            except Exception as e:
                self.add_log(f"Failed to export logs: {str(e)}", "ERROR")

class SettingsTabWidget(QWidget):
    """Settings tab for cloud providers and application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Cloud Providers section
        providers_group = QGroupBox("Cloud Providers")
        providers_group.setStyleSheet(f"""
            QGroupBox {{
                color: {LUMI_COLORS['text_primary']};
                font-weight: bold;
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        providers_layout = QVBoxLayout(providers_group)
        
        # Provider selection
        provider_frame = QFrame()
        provider_layout = QGridLayout(provider_frame)
        
        provider_layout.addWidget(QLabel("Default Provider:"), 0, 0)
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Google Drive", "OneDrive", "Dropbox"])
        self.provider_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {LUMI_COLORS['bg_secondary']};
                color: {LUMI_COLORS['text_primary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        provider_layout.addWidget(self.provider_combo, 0, 1)
        
        providers_layout.addWidget(provider_frame)
        
        # Application Settings section
        app_group = QGroupBox("Application Settings")
        app_group.setStyleSheet(f"""
            QGroupBox {{
                color: {LUMI_COLORS['text_primary']};
                font-weight: bold;
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        app_layout = QVBoxLayout(app_group)
        
        # Startup checkbox
        self.startup_cb = QCheckBox("Launch on system startup")
        self.startup_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {LUMI_COLORS['text_primary']};
                font-size: 12px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {LUMI_COLORS['border']};
                border-radius: 3px;
                background-color: {LUMI_COLORS['bg_secondary']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {LUMI_COLORS['accent_cyan']};
                border-color: {LUMI_COLORS['accent_cyan']};
            }}
        """)
        
        # Auto-backup settings
        backup_frame = QFrame()
        backup_layout = QGridLayout(backup_frame)
        
        self.auto_backup_cb = QCheckBox("Enable automatic backups")
        self.auto_backup_cb.setStyleSheet(self.startup_cb.styleSheet())
        backup_layout.addWidget(self.auto_backup_cb, 0, 0, 1, 2)
        
        backup_layout.addWidget(QLabel("Backup interval (hours):"), 1, 0)
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(1, 168)  # 1 hour to 1 week
        self.backup_interval.setValue(24)
        self.backup_interval.setStyleSheet(f"""
            QSpinBox {{
                background-color: {LUMI_COLORS['bg_secondary']};
                color: {LUMI_COLORS['text_primary']};
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        backup_layout.addWidget(self.backup_interval, 1, 1)
        
        app_layout.addWidget(self.startup_cb)
        app_layout.addWidget(backup_frame)
        
        layout.addWidget(providers_group)
        layout.addWidget(app_group)
        layout.addStretch()
