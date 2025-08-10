"""
Theme Manager for LumiSync
Manages theme application and component styling
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QProgressBar, QCheckBox, QTextEdit, QTabWidget, QTreeWidget, QStatusBar, QGroupBox
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont

from .lumi_setup_theme import (
    LUMI_COLORS, FONTS, STYLES, 
    create_font, apply_dark_palette, get_style, get_color, get_font_config
)

class ThemeManager(QObject):
    """Manages theme application and updates for the application."""
    
    theme_changed = pyqtSignal(str)  # Emitted when theme changes
    
    def __init__(self):
        super().__init__()
        self.current_theme = "lumi_setup"
        self.custom_styles = {}
    
    def apply_theme_to_app(self, app: QApplication) -> None:
        """Apply the complete theme to the application."""
        # Apply dark palette
        apply_dark_palette(app)
        
        # Set application-wide stylesheet
        app.setStyleSheet(self._get_global_stylesheet())
        
        # Set default font
        default_font = create_font(FONTS['primary'])
        app.setFont(default_font)
    
    def style_widget(self, widget: QWidget, style_name: str) -> None:
        """Apply a specific style to a widget."""
        if style_name in STYLES:
            widget.setStyleSheet(STYLES[style_name])
    
    def style_button(self, button: QPushButton, button_type: str = "primary") -> None:
        """Style a button with the specified type."""
        style_map = {
            "primary": "primary_button",
            "secondary": "secondary_button", 
            "success": "success_button",
            "danger": "danger_button"
        }
        
        style_name = style_map.get(button_type, "primary_button")
        button.setStyleSheet(get_style(style_name))
        
        # Set font
        font = create_font(FONTS['button'])
        button.setFont(font)
    
    def style_progress_bar(self, progress_bar: QProgressBar) -> None:
        """Style a progress bar."""
        progress_bar.setStyleSheet(get_style("progress_bar"))
    
    def style_checkbox(self, checkbox: QCheckBox) -> None:
        """Style a checkbox."""
        checkbox.setStyleSheet(get_style("checkbox"))
        font = create_font(FONTS['primary'])
        checkbox.setFont(font)
    
    def style_text_edit(self, text_edit: QTextEdit) -> None:
        """Style a text edit widget."""
        text_edit.setStyleSheet(get_style("text_edit"))
        font = create_font(FONTS['monospace'])
        text_edit.setFont(font)
    
    def style_tab_widget(self, tab_widget: QTabWidget) -> None:
        """Style a tab widget."""
        tab_widget.setStyleSheet(get_style("tab_widget"))
    
    def style_tree_widget(self, tree_widget: QTreeWidget) -> None:
        """Style a tree widget."""
        tree_widget.setStyleSheet(get_style("tree_widget"))
    
    def style_status_bar(self, status_bar: QStatusBar) -> None:
        """Style a status bar."""
        status_bar.setStyleSheet(get_style("status_bar"))
    
    def style_group_box(self, group_box: QGroupBox) -> None:
        """Style a group box."""
        group_box.setStyleSheet(get_style("group_box"))
        font = create_font(FONTS['header'])
        group_box.setFont(font)
    
    def create_styled_button(self, text: str, button_type: str = "primary", parent: Optional[QWidget] = None) -> QPushButton:
        """Create a pre-styled button."""
        button = QPushButton(text, parent)
        self.style_button(button, button_type)
        return button
    
    def create_styled_progress_bar(self, parent: Optional[QWidget] = None) -> QProgressBar:
        """Create a pre-styled progress bar."""
        progress_bar = QProgressBar(parent)
        self.style_progress_bar(progress_bar)
        return progress_bar
    
    def create_styled_checkbox(self, text: str, parent: Optional[QWidget] = None) -> QCheckBox:
        """Create a pre-styled checkbox."""
        checkbox = QCheckBox(text, parent)
        self.style_checkbox(checkbox)
        return checkbox
    
    def get_color(self, color_name: str) -> str:
        """Get a color from the current theme."""
        return get_color(color_name)
    
    def get_font(self, font_name: str) -> QFont:
        """Get a font from the current theme."""
        config = get_font_config(font_name)
        return create_font(config)
    
    def add_custom_style(self, name: str, stylesheet: str) -> None:
        """Add a custom style that can be applied to widgets."""
        self.custom_styles[name] = stylesheet
    
    def apply_custom_style(self, widget: QWidget, style_name: str) -> None:
        """Apply a custom style to a widget."""
        if style_name in self.custom_styles:
            widget.setStyleSheet(self.custom_styles[style_name])
    
    def _get_global_stylesheet(self) -> str:
        """Get the global application stylesheet."""
        return f"""
        /* Global application styles */
        QWidget {{
            background-color: {get_color('bg_primary')};
            color: {get_color('text_primary')};
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {get_color('bg_tertiary')};
            color: {get_color('text_primary')};
            border: 1px solid {get_color('border')};
            border-radius: 4px;
            padding: 4px;
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {get_color('bg_secondary')};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {get_color('bg_tertiary')};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {get_color('bg_hover')};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {get_color('bg_secondary')};
            height: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {get_color('bg_tertiary')};
            border-radius: 6px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {get_color('bg_hover')};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* Menu styling */
        QMenu {{
            background-color: {get_color('bg_secondary')};
            color: {get_color('text_primary')};
            border: 1px solid {get_color('border')};
            border-radius: 4px;
        }}
        QMenu::item {{
            padding: 8px 16px;
        }}
        QMenu::item:selected {{
            background-color: {get_color('accent_cyan')};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {get_color('separator')};
            margin: 4px 0px;
        }}
        
        /* Splitter styling */
        QSplitter::handle {{
            background-color: {get_color('border')};
        }}
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        QSplitter::handle:hover {{
            background-color: {get_color('accent_cyan')};
        }}
        """

# Global theme manager instance
theme_manager = ThemeManager()

def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    return theme_manager
