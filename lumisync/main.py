"""
LumiSync Main Application Entry Point
Launches the GUI application for Linux settings synchronization
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lumisync.gui.main_window import MainWindow, create_application
from lumisync.utils.logger import setup_logging, get_logger
from lumisync.config.settings import LOG_FILE

def main():
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging(log_level='INFO', console_output=True)
        logger = get_logger(__name__)
        
        logger.info("Starting LumiSync application")
        logger.info(f"Log file: {LOG_FILE}")
        
        # Create Qt application
        app = create_application()
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logger.info("LumiSync GUI initialized successfully")
        
        # Run the application
        exit_code = app.exec()
        
        logger.info(f"LumiSync application exited with code: {exit_code}")
        return exit_code
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Failed to start LumiSync: {e}")
        if 'logger' in locals():
            logger.critical(f"Application startup failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
