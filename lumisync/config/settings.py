"""
LumiSync Configuration Settings
Central configuration management for the application
"""

import os
from pathlib import Path
from typing import Dict, List, Any

# Application Information
APP_NAME = "LumiSync"
APP_VERSION = "0.1.0"
APP_AUTHOR = "LumiSync Development Team"

# Directories
HOME_DIR = Path.home()
CONFIG_DIR = HOME_DIR / ".config" / "lumisync"
CACHE_DIR = HOME_DIR / ".cache" / "lumisync"
DATA_DIR = HOME_DIR / ".local" / "share" / "lumisync"
TEMP_DIR = Path("/tmp") / "lumisync"

# Ensure directories exist
for directory in [CONFIG_DIR, CACHE_DIR, DATA_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration Files
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
USER_CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = DATA_DIR / "lumisync.log"

# Cloud Storage Settings
CLOUD_FOLDER_NAME = "LumiSync"
BACKUP_FOLDER_STRUCTURE = {
    "metadata": "metadata.json",
    "system": "system",
    "applications": "applications",
    "backups": "backups"
}

# Google Drive API Settings (PoC)
GOOGLE_DRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.appdata'
]

# Supported Applications and their detection paths
APPLICATION_PATHS = {
    "firefox": {
        "snap": "~/snap/firefox/common/.mozilla/firefox/",
        "flatpak": "~/.var/app/org.mozilla.firefox/.mozilla/firefox/",
        "apt": "~/.mozilla/firefox/"
    },
    "thunderbird": {
        "snap": "~/snap/thunderbird/common/.thunderbird/",
        "flatpak": "~/.var/app/org.mozilla.Thunderbird/.thunderbird/",
        "apt": "~/.thunderbird/"
    }
}

# GNOME Settings to backup
GNOME_SETTINGS_KEYS = [
    # Desktop appearance
    "org.gnome.desktop.interface.gtk-theme",
    "org.gnome.desktop.interface.icon-theme",
    "org.gnome.desktop.interface.cursor-theme",
    "org.gnome.desktop.interface.font-name",
    "org.gnome.desktop.interface.document-font-name",
    "org.gnome.desktop.interface.monospace-font-name",
    
    # Background and screensaver
    "org.gnome.desktop.background.picture-uri",
    "org.gnome.desktop.background.picture-uri-dark",
    "org.gnome.desktop.background.primary-color",
    "org.gnome.desktop.background.secondary-color",
    
    # Dock/Panel settings (Ubuntu specific)
    "org.gnome.shell.extensions.dash-to-dock.dock-position",
    "org.gnome.shell.extensions.dash-to-dock.dock-fixed",
    "org.gnome.shell.extensions.dash-to-dock.dash-max-icon-size",
    "org.gnome.shell.extensions.dash-to-dock.show-apps-at-top",
    
    # Favorite applications
    "org.gnome.shell.favorite-apps",
    
    # Window management
    "org.gnome.desktop.wm.preferences.button-layout",
    "org.gnome.desktop.wm.preferences.focus-mode",
    "org.gnome.desktop.wm.preferences.theme",
    
    # Input settings
    "org.gnome.desktop.input-sources.sources",
    "org.gnome.desktop.input-sources.xkb-options",
]

# GUI Settings
GUI_SETTINGS = {
    "window": {
        "min_width": 600,
        "min_height": 500,
        "default_width": 800,
        "default_height": 600
    },
    "theme": {
        "primary_color": "#2196F3",
        "secondary_color": "#FFC107",
        "success_color": "#4CAF50",
        "warning_color": "#FF9800",
        "error_color": "#F44336",
        "background_color": "#FAFAFA",
        "text_color": "#212121"
    },
    "fonts": {
        "default": "Ubuntu, 10",
        "heading": "Ubuntu, 12, bold",
        "monospace": "Ubuntu Mono, 9"
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "simple": {
            "format": "%(levelname)s: %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOG_FILE),
            "formatter": "detailed",
            "level": "DEBUG"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "INFO"
        }
    },
    "loggers": {
        "lumisync": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

# Error Messages for User-Friendly Display
ERROR_MESSAGES = {
    "no_internet": {
        "title": "Keine Internetverbindung",
        "message": "LumiSync benötigt eine Internetverbindung für die Cloud-Synchronisierung.",
        "solutions": [
            "Internetverbindung prüfen",
            "Proxy-Einstellungen überprüfen",
            "Firewall-Einstellungen kontrollieren"
        ]
    },
    "auth_failed": {
        "title": "Cloud-Anmeldung fehlgeschlagen",
        "message": "Die Anmeldung bei Ihrem Cloud-Speicher war nicht erfolgreich.",
        "solutions": [
            "Erneut versuchen",
            "Browser-Cache leeren",
            "Anderes Konto verwenden"
        ]
    },
    "profile_not_found": {
        "title": "Anwendungsprofil nicht gefunden",
        "message": "Das Profil für {app} konnte nicht gefunden werden.",
        "solutions": [
            "Anwendung mindestens einmal starten",
            "Installationsmethode überprüfen",
            "Manuelle Pfad-Angabe"
        ]
    },
    "backup_failed": {
        "title": "Backup fehlgeschlagen",
        "message": "Das Erstellen des Backups ist fehlgeschlagen.",
        "solutions": [
            "Speicherplatz prüfen",
            "Berechtigungen überprüfen",
            "Erneut versuchen"
        ]
    },
    "restore_failed": {
        "title": "Wiederherstellung fehlgeschlagen",
        "message": "Die Wiederherstellung der Einstellungen ist fehlgeschlagen.",
        "solutions": [
            "Backup-Integrität prüfen",
            "Ziel-Verzeichnisse überprüfen",
            "Anwendungen schließen und erneut versuchen"
        ]
    }
}

# Success Messages
SUCCESS_MESSAGES = {
    "backup_complete": {
        "title": "Backup erfolgreich!",
        "message": "Ihre Einstellungen wurden erfolgreich in der Cloud gesichert."
    },
    "restore_complete": {
        "title": "Wiederherstellung erfolgreich!",
        "message": "Ihre Einstellungen wurden erfolgreich wiederhergestellt. Starten Sie die Anwendungen neu, um alle Änderungen zu sehen."
    },
    "auth_success": {
        "title": "Verbindung erfolgreich!",
        "message": "LumiSync ist jetzt mit Ihrem Cloud-Speicher verbunden."
    }
}

# File size limits (in MB)
FILE_SIZE_LIMITS = {
    "profile_max_size": 500,  # Maximum size for a single profile backup
    "total_backup_max_size": 1000,  # Maximum total backup size
    "warning_threshold": 100  # Warn user if backup exceeds this size
}

# Backup retention settings
BACKUP_RETENTION = {
    "max_backups": 10,  # Maximum number of backups to keep
    "auto_cleanup": True,  # Automatically remove old backups
    "keep_daily": 7,  # Keep daily backups for 7 days
    "keep_weekly": 4,  # Keep weekly backups for 4 weeks
    "keep_monthly": 12  # Keep monthly backups for 12 months
}
