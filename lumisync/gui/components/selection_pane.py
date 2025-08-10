"""
Selection Pane Component for LumiSync v2.0
Left column widget for selecting synchronization items
"""

from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..themes.lumi_setup_theme import LUMI_COLORS
from dataclasses import dataclass

@dataclass
class SyncCategory:
    """Represents a synchronization category"""
    id: str
    name: str
    description: str
    items: List[str]
    recommended: bool = False
    enabled: bool = True

class SelectionPaneWidget(QWidget):
    """Left pane for selecting items to synchronize"""
    
    selection_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.categories = self._get_sync_categories()
        self.category_checkboxes = {}
        self.item_checkboxes = {}
        self._setup_ui()
        
    def _get_sync_categories(self) -> List[SyncCategory]:
        """Define the synchronization categories"""
        return [
            SyncCategory(
                id="desktop_settings",
                name="Desktop Settings",
                description="GNOME/dconf settings, themes, wallpaper, dock favorites",
                items=["Themes", "Wallpaper", "Dock Favorites", "Window Manager", "Keyboard Shortcuts"],
                recommended=True
            ),
            SyncCategory(
                id="firefox",
                name="Firefox Web Browser",
                description="Bookmarks, history, extensions, preferences",
                items=["Bookmarks", "History", "Extensions", "Preferences", "Saved Passwords"],
                recommended=True
            ),
            SyncCategory(
                id="thunderbird",
                name="Thunderbird Email Client",
                description="Email accounts, contacts, calendar",
                items=["Email Accounts", "Contacts", "Calendar", "Filters", "Extensions"],
                recommended=False
            ),
            SyncCategory(
                id="vscode",
                name="Visual Studio Code",
                description="Settings, extensions, keybindings, snippets",
                items=["Settings", "Extensions", "Keybindings", "Snippets", "Workspace"],
                recommended=True
            ),
            SyncCategory(
                id="development_tools",
                name="Development Tools",
                description="Git config, SSH keys, terminal settings",
                items=["Git Configuration", "SSH Keys", "Terminal Settings", "Shell Configuration"],
                recommended=False
            ),
            SyncCategory(
                id="system_tools",
                name="System Tools",
                description="Package lists, system preferences",
                items=["Installed Packages", "System Preferences", "Service Configuration"],
                recommended=False
            )
        ]
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header_label = QLabel("Select Items to Synchronize")
        header_label.setStyleSheet(f"""
            color: {LUMI_COLORS['text_primary']};
            font-size: 16px;
            font-weight: bold;
            padding: 10px 0;
        """)
        
        # Control buttons
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)
        
        self.select_all_btn = QPushButton("Select All")
        self.select_none_btn = QPushButton("Select None")
        self.recommended_btn = QPushButton("Recommended")
        
        for btn in [self.select_all_btn, self.select_none_btn, self.recommended_btn]:
            btn.setMinimumHeight(30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {LUMI_COLORS['bg_tertiary']};
                    color: {LUMI_COLORS['text_primary']};
                    border: 1px solid {LUMI_COLORS['border']};
                    border-radius: 4px;
                    font-size: 10px;
                    padding: 5px 10px;
                }}
                QPushButton:hover {{
                    background-color: {LUMI_COLORS['bg_hover']};
                }}
            """)
            
        # Special styling for Recommended button
        self.recommended_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LUMI_COLORS['accent_green']};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {LUMI_COLORS['success']};
            }}
        """)
        
        self.select_all_btn.clicked.connect(self._select_all)
        self.select_none_btn.clicked.connect(self._select_none)
        self.recommended_btn.clicked.connect(self._select_recommended)
        
        controls_layout.addWidget(self.select_all_btn)
        controls_layout.addWidget(self.select_none_btn)
        controls_layout.addWidget(self.recommended_btn)
        
        # Scrollable area for categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {LUMI_COLORS['border']};
                border-radius: 6px;
                background-color: {LUMI_COLORS['bg_secondary']};
            }}
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(5)
        
        # Create category groups
        for category in self.categories:
            group_frame = self._create_category_group(category)
            scroll_layout.addWidget(group_frame)
            
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        
        layout.addWidget(header_label)
        layout.addWidget(controls_frame)
        layout.addWidget(scroll_area)
        
    def _create_category_group(self, category: SyncCategory) -> QWidget:
        """Create a widget for a category group"""
        group_frame = QFrame()
        group_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {LUMI_COLORS['bg_primary']};
                border: 1px solid {LUMI_COLORS['border_light']};
                border-radius: 6px;
                margin: 2px;
            }}
        """)
        
        layout = QVBoxLayout(group_frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        
        # Category header with checkbox
        header_layout = QHBoxLayout()
        
        category_cb = QCheckBox(category.name)
        category_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {LUMI_COLORS['text_primary']};
                font-weight: bold;
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
        category_cb.stateChanged.connect(lambda state, cat=category: self._on_category_changed(cat, state))
        self.category_checkboxes[category.id] = category_cb
        
        # Description
        desc_label = QLabel(category.description)
        desc_label.setStyleSheet(f"""
            color: {LUMI_COLORS['text_secondary']};
            font-size: 10px;
            margin-left: 20px;
        """)
        desc_label.setWordWrap(True)
        
        header_layout.addWidget(category_cb)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(desc_label)
        
        # Individual items
        self.item_checkboxes[category.id] = []
        for item in category.items:
            item_cb = QCheckBox(item)
            item_cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {LUMI_COLORS['text_secondary']};
                    font-size: 11px;
                    margin-left: 20px;
                }}
                QCheckBox::indicator {{
                    width: 14px;
                    height: 14px;
                    border: 1px solid {LUMI_COLORS['border']};
                    border-radius: 2px;
                    background-color: {LUMI_COLORS['bg_tertiary']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {LUMI_COLORS['accent_cyan']};
                    border-color: {LUMI_COLORS['accent_cyan']};
                }}
            """)
            item_cb.stateChanged.connect(self._on_item_changed)
            self.item_checkboxes[category.id].append(item_cb)
            layout.addWidget(item_cb)
            
        return group_frame
        
    def _on_category_changed(self, category: SyncCategory, state: int):
        """Handle category checkbox state change"""
        checked = state == Qt.CheckState.Checked.value
        for item_cb in self.item_checkboxes[category.id]:
            item_cb.setChecked(checked)
        self.selection_changed.emit()
        
    def _on_item_changed(self):
        """Handle individual item checkbox change"""
        # Update category checkboxes based on item states
        for category in self.categories:
            item_checkboxes = self.item_checkboxes[category.id]
            checked_count = sum(1 for cb in item_checkboxes if cb.isChecked())
            
            category_cb = self.category_checkboxes[category.id]
            if checked_count == 0:
                category_cb.setCheckState(Qt.CheckState.Unchecked)
            elif checked_count == len(item_checkboxes):
                category_cb.setCheckState(Qt.CheckState.Checked)
            else:
                category_cb.setCheckState(Qt.CheckState.PartiallyChecked)
                
        self.selection_changed.emit()
        
    def _select_all(self):
        """Select all categories and items"""
        for category in self.categories:
            self.category_checkboxes[category.id].setChecked(True)
            # Also select all individual items
            for item_cb in self.item_checkboxes[category.id]:
                item_cb.setChecked(True)
        self.selection_changed.emit()
            
    def _select_none(self):
        """Deselect all categories and items"""
        for category in self.categories:
            self.category_checkboxes[category.id].setChecked(False)
            # Also deselect all individual items
            for item_cb in self.item_checkboxes[category.id]:
                item_cb.setChecked(False)
        self.selection_changed.emit()
            
    def _select_recommended(self):
        """Select recommended categories"""
        for category in self.categories:
            is_recommended = category.recommended
            self.category_checkboxes[category.id].setChecked(is_recommended)
            # Also update individual items
            for item_cb in self.item_checkboxes[category.id]:
                item_cb.setChecked(is_recommended)
        self.selection_changed.emit()
            
    def get_selected_categories(self) -> List[str]:
        """Get list of selected category IDs"""
        selected = []
        for category in self.categories:
            if self.category_checkboxes[category.id].isChecked():
                selected.append(category.id)
        return selected
        
    def has_selection(self) -> bool:
        """Check if any items are selected"""
        for category in self.categories:
            if any(cb.isChecked() for cb in self.item_checkboxes[category.id]):
                return True
        return False
