#!/usr/bin/env python3
"""
Demo application showcasing the Lumi-Setup theme system
"""

import sys
import os
from pathlib import Path

# Add the lumisync package to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
        QScrollArea, QSplitter
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont
except ImportError as e:
    print(f"PyQt6 not installed: {e}")
    print("Install with: pip install PyQt6")
    sys.exit(1)

from lumisync.gui.themes import (
    get_theme_manager, LumiButton, LumiProgressBar, LumiCheckBox, 
    LumiLabel, LumiFrame, CategoryGroup, StatusPanel, LumiSplitter
)

class ThemeDemo(QMainWindow):
    """Demo window showcasing Lumi-Setup theme components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lumi-Setup Theme Demo - LumiSync")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply theme to application
        theme_manager = get_theme_manager()
        theme_manager.apply_theme_to_app(QApplication.instance())
        
        self._setup_ui()
        self._setup_demo_timer()
    
    def _setup_ui(self):
        """Setup the demo UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for two-panel layout (like Lumi-Setup)
        splitter = LumiSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Application selection (like Lumi-Setup)
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Progress and status (like Lumi-Setup)
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setSizes([360, 840])
        
        main_layout.addWidget(splitter)
        
        # Header bar
        self._create_header_bar()
    
    def _create_header_bar(self):
        """Create the header bar with action buttons."""
        header_frame = LumiFrame("header")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        # Title
        title_label = LumiLabel("Lumi-Setup v2.0 - Theme Demo", "title")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        self.start_button = LumiButton("Start Installation", "primary")
        self.pause_button = LumiButton("Pause", "secondary")
        self.stop_button = LumiButton("Stop", "danger")
        
        # Connect buttons to demo actions
        self.start_button.clicked.connect(self._start_demo)
        self.pause_button.clicked.connect(self._pause_demo)
        self.stop_button.clicked.connect(self._stop_demo)
        
        header_layout.addWidget(self.start_button)
        header_layout.addWidget(self.pause_button)
        header_layout.addWidget(self.stop_button)
        
        # Add header to main window
        self.setMenuWidget(header_frame)
    
    def _create_left_panel(self):
        """Create the left panel with application categories."""
        left_frame = LumiFrame("sidebar")
        left_frame.setFixedWidth(360)
        
        layout = QVBoxLayout(left_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Panel title
        title_frame = QWidget()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(16, 16, 16, 8)
        
        panel_title = LumiLabel("Select Applications to Install", "header")
        title_layout.addWidget(panel_title)
        
        # Quick selection buttons
        button_layout = QHBoxLayout()
        select_all_btn = LumiButton("Select All", "secondary")
        select_none_btn = LumiButton("Select None", "secondary")
        recommended_btn = LumiButton("Recommended", "success")
        
        select_all_btn.clicked.connect(self._select_all)
        select_none_btn.clicked.connect(self._select_none)
        recommended_btn.clicked.connect(self._select_recommended)
        
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(select_none_btn)
        button_layout.addWidget(recommended_btn)
        
        title_layout.addLayout(button_layout)
        layout.addWidget(title_frame)
        
        # Scrollable area for categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(8, 8, 8, 8)
        scroll_layout.setSpacing(8)
        
        # Create category groups (like Lumi-Setup)
        self.categories = {}
        
        # Desktop Applications
        desktop_apps = [
            "Firefox Web Browser", "Thunderbird Email Client", 
            "LibreOffice Office Suite", "GIMP Image Editor", 
            "VLC Media Player", "Visual Studio Code"
        ]
        desktop_group = CategoryGroup("Desktop Applications", desktop_apps)
        desktop_group.category_changed.connect(self._on_category_changed)
        self.categories["Desktop Applications"] = desktop_group
        scroll_layout.addWidget(desktop_group)
        
        # Development Tools
        dev_tools = [
            "Git Version Control", "Python 3", "Node.js", 
            "Docker", "RustDesk Remote Desktop"
        ]
        dev_group = CategoryGroup("Development Tools", dev_tools)
        dev_group.category_changed.connect(self._on_category_changed)
        self.categories["Development Tools"] = dev_group
        scroll_layout.addWidget(dev_group)
        
        # Entertainment
        entertainment = ["Steam Gaming Platform", "Discord Chat"]
        ent_group = CategoryGroup("Entertainment", entertainment)
        ent_group.category_changed.connect(self._on_category_changed)
        self.categories["Entertainment"] = ent_group
        scroll_layout.addWidget(ent_group)
        
        # System Tools
        system_tools = ["System Monitor", "File Manager", "Terminal"]
        sys_group = CategoryGroup("System Tools", system_tools)
        sys_group.category_changed.connect(self._on_category_changed)
        self.categories["System Tools"] = sys_group
        scroll_layout.addWidget(sys_group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Status at bottom
        status_label = LumiLabel("6 applications selected", "muted")
        status_label.setContentsMargins(16, 8, 16, 16)
        layout.addWidget(status_label)
        self.selection_status = status_label
        
        return left_frame
    
    def _create_right_panel(self):
        """Create the right panel with progress and status."""
        right_frame = LumiFrame("panel")
        layout = QVBoxLayout(right_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Status panel
        self.status_panel = StatusPanel()
        layout.addWidget(self.status_panel)
        
        return right_frame
    
    def _setup_demo_timer(self):
        """Setup timer for demo progress simulation."""
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self._update_demo_progress)
        self.demo_progress = 0
        self.demo_running = False
    
    def _start_demo(self):
        """Start the demo installation simulation."""
        if not self.demo_running:
            self.demo_running = True
            self.demo_progress = 0
            self.demo_timer.start(100)  # Update every 100ms
            
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            
            self.status_panel.update_progress(0, 100, "Starting installation...")
    
    def _pause_demo(self):
        """Pause the demo."""
        if self.demo_running:
            self.demo_timer.stop()
            self.demo_running = False
            self.start_button.setEnabled(True)
            self.start_button.setText("Resume")
            self.status_panel.update_progress(self.demo_progress, 100, "Installation paused")
    
    def _stop_demo(self):
        """Stop the demo."""
        self.demo_timer.stop()
        self.demo_running = False
        self.demo_progress = 0
        
        self.start_button.setEnabled(True)
        self.start_button.setText("Start Installation")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        self.status_panel.update_progress(0, 100, "Ready to start installation...")
        self.status_panel.update_current_app("", 0)
        self.status_panel.update_statistics(0, 0, 6, "00:00")
    
    def _update_demo_progress(self):
        """Update demo progress simulation."""
        if self.demo_running:
            self.demo_progress += 1
            
            # Simulate different phases
            if self.demo_progress <= 20:
                self.status_panel.update_current_app("Firefox Web Browser", self.demo_progress * 5)
                self.status_panel.update_progress(self.demo_progress, 100, "Installing Firefox Web Browser...")
            elif self.demo_progress <= 40:
                self.status_panel.update_current_app("Visual Studio Code", (self.demo_progress - 20) * 5)
                self.status_panel.update_progress(self.demo_progress, 100, "Installing Visual Studio Code...")
            elif self.demo_progress <= 60:
                self.status_panel.update_current_app("Git Version Control", (self.demo_progress - 40) * 5)
                self.status_panel.update_progress(self.demo_progress, 100, "Installing Git Version Control...")
            elif self.demo_progress <= 80:
                self.status_panel.update_current_app("Python 3", (self.demo_progress - 60) * 5)
                self.status_panel.update_progress(self.demo_progress, 100, "Installing Python 3...")
            elif self.demo_progress <= 100:
                self.status_panel.update_current_app("LibreOffice Office Suite", (self.demo_progress - 80) * 5)
                self.status_panel.update_progress(self.demo_progress, 100, "Installing LibreOffice Office Suite...")
            
            # Update statistics
            completed = max(0, (self.demo_progress - 1) // 20)
            remaining = max(0, 6 - completed - (1 if self.demo_progress % 20 != 0 else 0))
            elapsed_time = f"{self.demo_progress // 60:02d}:{self.demo_progress % 60:02d}"
            
            self.status_panel.update_statistics(completed, 0, remaining, elapsed_time)
            
            if self.demo_progress >= 100:
                self._stop_demo()
                self.status_panel.update_progress(100, 100, "Installation completed successfully!")
                self.status_panel.update_current_app("", 0)
                self.status_panel.update_statistics(6, 0, 0, elapsed_time)
    
    def _select_all(self):
        """Select all applications."""
        for category in self.categories.values():
            category.set_all_checked(True)
        self._update_selection_count()
    
    def _select_none(self):
        """Deselect all applications."""
        for category in self.categories.values():
            category.set_all_checked(False)
        self._update_selection_count()
    
    def _select_recommended(self):
        """Select recommended applications."""
        # Clear all first
        self._select_none()
        
        # Select recommended items
        recommended_items = {
            "Desktop Applications": ["Firefox Web Browser", "LibreOffice Office Suite", "VLC Media Player"],
            "Development Tools": ["Git Version Control", "Python 3"],
        }
        
        for category_name, items in recommended_items.items():
            if category_name in self.categories:
                category = self.categories[category_name]
                for item in items:
                    category.set_item_checked(item, True)
        
        self._update_selection_count()
    
    def _on_category_changed(self, item_name: str, checked: bool):
        """Handle category item change."""
        self._update_selection_count()
    
    def _update_selection_count(self):
        """Update the selection count display."""
        total_selected = 0
        for category in self.categories.values():
            total_selected += len(category.get_checked_items())
        
        self.selection_status.setText(f"{total_selected} applications selected")

def main():
    """Run the theme demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Lumi-Setup Theme Demo")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("LumiSync")
    
    # Create and show the demo window
    demo = ThemeDemo()
    demo.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
