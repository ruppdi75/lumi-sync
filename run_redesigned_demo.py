#!/usr/bin/env python3
"""
LumiSync v2.0 Redesigned GUI Demo
Showcases the new professional two-column layout
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from lumisync.gui.redesigned_main_window_complete import main
    
    if __name__ == "__main__":
        print("🚀 Starting LumiSync v2.0 Redesigned GUI Demo...")
        print("✨ Features:")
        print("   • Professional two-column layout")
        print("   • Modern dark theme inspired by Lumi-Setup")
        print("   • Categorized selection pane with smart controls")
        print("   • Cloud connection status with visual feedback")
        print("   • Tabbed information pane (Progress, Logs, Settings)")
        print("   • Real-time progress tracking and operation controls")
        print("   • Professional status feedback and user guidance")
        print()
        
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ Error importing redesigned GUI: {e}")
    print("💡 Make sure PyQt6 is installed: pip install PyQt6")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error running demo: {e}")
    sys.exit(1)
