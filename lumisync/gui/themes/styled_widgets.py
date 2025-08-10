"""
Styled Widgets for Lumi-Setup Theme
Pre-configured widgets with Lumi-Setup styling applied
"""

from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QPushButton, QProgressBar, QCheckBox, QLabel, QFrame,
    QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QTreeWidget,
    QTreeWidgetItem, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient

from .theme_manager import get_theme_manager
from .lumi_setup_theme import LUMI_COLORS, create_font, FONTS

class LumiButton(QPushButton):
    """Styled button matching Lumi-Setup design."""
    
    def __init__(self, text: str, button_type: str = "primary", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_style()
    
    def _setup_style(self):
        """Setup button styling."""
        theme_manager = get_theme_manager()
        theme_manager.style_button(self, self.button_type)
        
        # Set minimum size for consistency
        self.setMinimumHeight(36)
        self.setMinimumWidth(100)

class LumiProgressBar(QProgressBar):
    """Styled progress bar with gradient fill."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """Setup progress bar styling."""
        theme_manager = get_theme_manager()
        theme_manager.style_progress_bar(self)
        self.setMinimumHeight(24)

class LumiCheckBox(QCheckBox):
    """Styled checkbox with custom indicator."""
    
    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._setup_style()
    
    def _setup_style(self):
        """Setup checkbox styling."""
        theme_manager = get_theme_manager()
        theme_manager.style_checkbox(self)

class LumiLabel(QLabel):
    """Styled label with theme-appropriate colors."""
    
    def __init__(self, text: str = "", label_type: str = "primary", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.label_type = label_type
        self._setup_style()
    
    def _setup_style(self):
        """Setup label styling based on type."""
        color_map = {
            "primary": LUMI_COLORS['text_primary'],
            "secondary": LUMI_COLORS['text_secondary'],
            "muted": LUMI_COLORS['text_muted'],
            "accent": LUMI_COLORS['text_accent'],
            "success": LUMI_COLORS['success'],
            "warning": LUMI_COLORS['warning'],
            "error": LUMI_COLORS['error']
        }
        
        font_map = {
            "primary": "primary",
            "header": "header",
            "title": "title"
        }
        
        color = color_map.get(self.label_type, LUMI_COLORS['text_primary'])
        self.setStyleSheet(f"color: {color};")
        
        # Set appropriate font
        if self.label_type in ["header", "title"]:
            font = create_font(FONTS[self.label_type])
            self.setFont(font)

class LumiFrame(QFrame):
    """Styled frame for grouping elements."""
    
    def __init__(self, frame_type: str = "panel", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.frame_type = frame_type
        self._setup_style()
    
    def _setup_style(self):
        """Setup frame styling."""
        if self.frame_type == "panel":
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {LUMI_COLORS['bg_secondary']};
                    border: 1px solid {LUMI_COLORS['border']};
                    border-radius: 6px;
                }}
            """)
        elif self.frame_type == "sidebar":
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {LUMI_COLORS['bg_secondary']};
                    border-right: 1px solid {LUMI_COLORS['border']};
                }}
            """)
        elif self.frame_type == "header":
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {LUMI_COLORS['bg_tertiary']};
                    border-bottom: 1px solid {LUMI_COLORS['border']};
                    min-height: 60px;
                }}
            """)

class LumiTextEdit(QTextEdit):
    """Styled text edit for logs and output."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """Setup text edit styling."""
        theme_manager = get_theme_manager()
        theme_manager.style_text_edit(self)

class LumiTreeWidget(QTreeWidget):
    """Styled tree widget for hierarchical data."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """Setup tree widget styling."""
        theme_manager = get_theme_manager()
        theme_manager.style_tree_widget(self)

class CategoryGroup(QWidget):
    """Widget representing a category group with checkboxes."""
    
    category_changed = pyqtSignal(str, bool)  # category_name, checked
    
    def __init__(self, title: str, items: List[str], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.title = title
        self.items = items
        self.checkboxes = {}
        self.is_expanded = True
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the category group UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Category header
        header_frame = LumiFrame("panel")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        # Expand/collapse indicator (simple text for now)
        self.expand_indicator = LumiLabel("▼" if self.is_expanded else "▶", "accent")
        self.expand_indicator.setFixedWidth(20)
        
        # Category title
        title_label = LumiLabel(self.title, "header")
        title_label.setStyleSheet(f"font-weight: bold; color: {LUMI_COLORS['text_primary']};")
        
        # Item count
        count_label = LumiLabel(f"({len(self.items)} items)", "muted")
        
        header_layout.addWidget(self.expand_indicator)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(count_label)
        
        # Make header clickable
        header_frame.mousePressEvent = self._toggle_expand
        
        layout.addWidget(header_frame)
        
        # Items container
        self.items_container = QWidget()
        items_layout = QVBoxLayout(self.items_container)
        items_layout.setContentsMargins(20, 4, 4, 4)
        items_layout.setSpacing(4)
        
        # Create checkboxes for items
        for item in self.items:
            checkbox = LumiCheckBox(item)
            checkbox.stateChanged.connect(lambda state, name=item: self._on_item_changed(name, state))
            self.checkboxes[item] = checkbox
            items_layout.addWidget(checkbox)
        
        layout.addWidget(self.items_container)
        
        # Set initial visibility
        self.items_container.setVisible(self.is_expanded)
    
    def _toggle_expand(self, event):
        """Toggle the expanded state of the category."""
        self.is_expanded = not self.is_expanded
        self.expand_indicator.setText("▼" if self.is_expanded else "▶")
        self.items_container.setVisible(self.is_expanded)
    
    def _on_item_changed(self, item_name: str, state: int):
        """Handle item checkbox state change."""
        is_checked = state == Qt.CheckState.Checked.value
        self.category_changed.emit(item_name, is_checked)
    
    def set_item_checked(self, item_name: str, checked: bool):
        """Set the checked state of an item."""
        if item_name in self.checkboxes:
            self.checkboxes[item_name].setChecked(checked)
    
    def get_checked_items(self) -> List[str]:
        """Get list of checked items."""
        return [name for name, checkbox in self.checkboxes.items() if checkbox.isChecked()]
    
    def set_all_checked(self, checked: bool):
        """Set all items to checked or unchecked."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(checked)

class StatusPanel(QWidget):
    """Status panel showing current operation and statistics."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the status panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Overall progress section
        progress_group = QGroupBox("Overall Progress")
        theme_manager = get_theme_manager()
        theme_manager.style_group_box(progress_group)
        
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(8)
        
        # Status message
        self.status_label = LumiLabel("Ready to start installation...", "primary")
        progress_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = LumiProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_group)
        
        # Current application section
        current_group = QGroupBox("Current Application")
        theme_manager.style_group_box(current_group)
        
        current_layout = QVBoxLayout(current_group)
        self.current_app_label = LumiLabel("No application currently being processed", "accent")
        self.current_app_label.setStyleSheet(f"color: {LUMI_COLORS['accent_cyan']};")
        current_layout.addWidget(self.current_app_label)
        
        # Current progress
        self.current_progress = LumiProgressBar()
        self.current_progress.setValue(0)
        current_layout.addWidget(self.current_progress)
        
        layout.addWidget(current_group)
        
        # Statistics section
        stats_group = QGroupBox("Statistics")
        theme_manager.style_group_box(stats_group)
        
        stats_layout = QHBoxLayout(stats_group)
        
        self.completed_label = LumiLabel("Completed: 0", "success")
        self.failed_label = LumiLabel("Failed: 0", "error")
        self.remaining_label = LumiLabel("Remaining: 0", "secondary")
        self.time_label = LumiLabel("Time: 00:00", "muted")
        
        stats_layout.addWidget(self.completed_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.remaining_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.time_label)
        
        layout.addWidget(stats_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update the overall progress."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
        
        if message:
            self.status_label.setText(message)
    
    def update_current_app(self, app_name: str, progress: int = 0):
        """Update the current application being processed."""
        if app_name:
            self.current_app_label.setText(f"Installing: {app_name}")
            self.current_progress.setValue(progress)
        else:
            self.current_app_label.setText("No application currently being processed")
            self.current_progress.setValue(0)
    
    def update_statistics(self, completed: int, failed: int, remaining: int, elapsed_time: str = "00:00"):
        """Update the statistics display."""
        self.completed_label.setText(f"Completed: {completed}")
        self.failed_label.setText(f"Failed: {failed}")
        self.remaining_label.setText(f"Remaining: {remaining}")
        self.time_label.setText(f"Time: {elapsed_time}")

class LumiSplitter(QSplitter):
    """Styled splitter for dividing panels."""
    
    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)
        self._setup_style()
    
    def _setup_style(self):
        """Setup splitter styling."""
        self.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {LUMI_COLORS['border']};
            }}
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            QSplitter::handle:vertical {{
                height: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {LUMI_COLORS['accent_cyan']};
            }}
        """)
        
        # Set handle width
        self.setHandleWidth(2)
