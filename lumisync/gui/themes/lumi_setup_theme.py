"""
Lumi-Setup Style Theme for LumiSync
Modern dark theme with cyan accents matching the Lumi-Setup v2.0 design
"""

from typing import Dict, Any
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

# Color palette based on Lumi-Setup analysis
LUMI_COLORS = {
    # Primary backgrounds
    'bg_primary': '#2b2b2b',        # Main dark background
    'bg_secondary': '#3a3a3a',      # Secondary panels
    'bg_tertiary': '#4a4a4a',       # Elevated elements
    'bg_hover': '#505050',          # Hover states
    
    # Accent colors
    'accent_cyan': '#4a9eff',       # Primary cyan accent
    'accent_teal': '#00d4aa',       # Teal variant
    'accent_green': '#00ff88',      # Success/positive actions
    'accent_red': '#ff4757',        # Error/negative actions
    'accent_orange': '#ffa726',     # Warning/attention
    
    # Text colors
    'text_primary': '#ffffff',      # Primary text
    'text_secondary': '#b0b0b0',    # Secondary text
    'text_muted': '#808080',        # Muted/disabled text
    'text_accent': '#4a9eff',       # Accent text
    
    # Border and separator colors
    'border': '#555555',            # Standard borders
    'border_light': '#666666',      # Light borders
    'separator': '#444444',         # Separators and dividers
    
    # Status colors
    'success': '#00ff88',
    'warning': '#ffa726',
    'error': '#ff4757',
    'info': '#4a9eff',
    
    # Special elements
    'selection': '#4a9eff33',       # Selection background (with alpha)
    'checkbox_checked': '#4a9eff',  # Checked checkbox
    'progress_bg': '#3a3a3a',       # Progress bar background
    'progress_fill': '#4a9eff',     # Progress bar fill
}

# Typography settings
FONTS = {
    'primary': {
        'family': 'Segoe UI',
        'size': 10,
        'weight': QFont.Weight.Normal
    },
    'header': {
        'family': 'Segoe UI',
        'size': 12,
        'weight': QFont.Weight.Medium
    },
    'title': {
        'family': 'Segoe UI',
        'size': 14,
        'weight': QFont.Weight.Bold
    },
    'button': {
        'family': 'Segoe UI',
        'size': 10,
        'weight': QFont.Weight.Medium
    },
    'monospace': {
        'family': 'Consolas',
        'size': 9,
        'weight': QFont.Weight.Normal
    }
}

# Component-specific styles
STYLES = {
    'main_window': f"""
        QMainWindow {{
            background-color: {LUMI_COLORS['bg_primary']};
            color: {LUMI_COLORS['text_primary']};
        }}
    """,
    
    'sidebar': f"""
        QWidget {{
            background-color: {LUMI_COLORS['bg_secondary']};
            border-right: 1px solid {LUMI_COLORS['border']};
        }}
    """,
    
    'header': f"""
        QWidget {{
            background-color: {LUMI_COLORS['bg_tertiary']};
            border-bottom: 1px solid {LUMI_COLORS['border']};
            min-height: 60px;
        }}
    """,
    
    'primary_button': f"""
        QPushButton {{
            background-color: {LUMI_COLORS['accent_cyan']};
            color: {LUMI_COLORS['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: #5aa3ff;
        }}
        QPushButton:pressed {{
            background-color: #3a8eff;
        }}
        QPushButton:disabled {{
            background-color: {LUMI_COLORS['bg_tertiary']};
            color: {LUMI_COLORS['text_muted']};
        }}
    """,
    
    'secondary_button': f"""
        QPushButton {{
            background-color: {LUMI_COLORS['bg_tertiary']};
            color: {LUMI_COLORS['text_primary']};
            border: 1px solid {LUMI_COLORS['border']};
            border-radius: 6px;
            padding: 8px 16px;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {LUMI_COLORS['bg_hover']};
            border-color: {LUMI_COLORS['accent_cyan']};
        }}
        QPushButton:pressed {{
            background-color: {LUMI_COLORS['bg_secondary']};
        }}
        QPushButton:disabled {{
            background-color: {LUMI_COLORS['bg_secondary']};
            color: {LUMI_COLORS['text_muted']};
            border-color: {LUMI_COLORS['separator']};
        }}
    """,
    
    'success_button': f"""
        QPushButton {{
            background-color: {LUMI_COLORS['accent_green']};
            color: {LUMI_COLORS['bg_primary']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: #00e699;
        }}
        QPushButton:pressed {{
            background-color: #00cc77;
        }}
    """,
    
    'danger_button': f"""
        QPushButton {{
            background-color: {LUMI_COLORS['accent_red']};
            color: {LUMI_COLORS['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: #ff5768;
        }}
        QPushButton:pressed {{
            background-color: #ff3746;
        }}
    """,
    
    'progress_bar': f"""
        QProgressBar {{
            border: 2px solid {LUMI_COLORS['border']};
            border-radius: 8px;
            background-color: {LUMI_COLORS['progress_bg']};
            text-align: center;
            color: {LUMI_COLORS['text_primary']};
            font-weight: bold;
            font-size: 11px;
            min-height: 20px;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {LUMI_COLORS['accent_cyan']}, stop:1 {LUMI_COLORS['accent_teal']});
            border-radius: 6px;
            margin: 1px;
        }}
    """,
    
    'checkbox': f"""
        QCheckBox {{
            color: {LUMI_COLORS['text_primary']};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {LUMI_COLORS['border']};
            border-radius: 3px;
            background-color: {LUMI_COLORS['bg_secondary']};
        }}
        QCheckBox::indicator:hover {{
            border-color: {LUMI_COLORS['accent_cyan']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {LUMI_COLORS['checkbox_checked']};
            border-color: {LUMI_COLORS['checkbox_checked']};
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }}
    """,
    
    'text_edit': f"""
        QTextEdit {{
            background-color: {LUMI_COLORS['bg_secondary']};
            color: {LUMI_COLORS['text_primary']};
            border: 1px solid {LUMI_COLORS['border']};
            border-radius: 4px;
            padding: 8px;
            selection-background-color: {LUMI_COLORS['selection']};
        }}
        QTextEdit:focus {{
            border-color: {LUMI_COLORS['accent_cyan']};
        }}
    """,
    
    'tab_widget': f"""
        QTabWidget::pane {{
            border: 1px solid {LUMI_COLORS['border']};
            background-color: {LUMI_COLORS['bg_secondary']};
        }}
        QTabBar::tab {{
            background-color: {LUMI_COLORS['bg_tertiary']};
            color: {LUMI_COLORS['text_secondary']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: {LUMI_COLORS['accent_cyan']};
            color: {LUMI_COLORS['text_primary']};
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {LUMI_COLORS['bg_hover']};
            color: {LUMI_COLORS['text_primary']};
        }}
    """,
    
    'tree_widget': f"""
        QTreeWidget {{
            background-color: {LUMI_COLORS['bg_secondary']};
            color: {LUMI_COLORS['text_primary']};
            border: none;
            selection-background-color: {LUMI_COLORS['selection']};
            outline: none;
        }}
        QTreeWidget::item {{
            padding: 4px;
            border: none;
        }}
        QTreeWidget::item:hover {{
            background-color: {LUMI_COLORS['bg_hover']};
        }}
        QTreeWidget::item:selected {{
            background-color: {LUMI_COLORS['selection']};
        }}
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgOCA4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNMiAxTDYgNEwyIDciIHN0cm9rZT0iIzRhOWVmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }}
        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgOCA4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNMSAyTDQgNkw3IDIiIHN0cm9rZT0iIzRhOWVmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }}
    """,
    
    'status_bar': f"""
        QStatusBar {{
            background-color: {LUMI_COLORS['bg_tertiary']};
            color: {LUMI_COLORS['text_secondary']};
            border-top: 1px solid {LUMI_COLORS['border']};
        }}
    """,
    
    'group_box': f"""
        QGroupBox {{
            color: {LUMI_COLORS['text_primary']};
            border: 1px solid {LUMI_COLORS['border']};
            border-radius: 4px;
            margin-top: 8px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;
            background-color: {LUMI_COLORS['bg_primary']};
        }}
    """
}

def create_font(font_config: Dict[str, Any]) -> QFont:
    """Create a QFont from configuration."""
    font = QFont(font_config['family'], font_config['size'])
    font.setWeight(font_config['weight'])
    return font

def apply_dark_palette(app) -> None:
    """Apply dark color palette to the application."""
    palette = QPalette()
    
    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(LUMI_COLORS['bg_primary']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(LUMI_COLORS['text_primary']))
    
    # Base colors (for input widgets)
    palette.setColor(QPalette.ColorRole.Base, QColor(LUMI_COLORS['bg_secondary']))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(LUMI_COLORS['bg_tertiary']))
    
    # Text colors
    palette.setColor(QPalette.ColorRole.Text, QColor(LUMI_COLORS['text_primary']))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(LUMI_COLORS['text_primary']))
    
    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(LUMI_COLORS['bg_tertiary']))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(LUMI_COLORS['text_primary']))
    
    # Highlight colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(LUMI_COLORS['accent_cyan']))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(LUMI_COLORS['text_primary']))
    
    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(LUMI_COLORS['text_muted']))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(LUMI_COLORS['text_muted']))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(LUMI_COLORS['text_muted']))
    
    app.setPalette(palette)

def get_style(component: str) -> str:
    """Get stylesheet for a specific component."""
    return STYLES.get(component, "")

def get_color(color_name: str) -> str:
    """Get color value by name."""
    return LUMI_COLORS.get(color_name, "#ffffff")

def get_font_config(font_name: str) -> Dict[str, Any]:
    """Get font configuration by name."""
    return FONTS.get(font_name, FONTS['primary'])
