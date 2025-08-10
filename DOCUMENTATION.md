# LumiSync - Comprehensive Documentation

## 🌟 Overview

LumiSync is a revolutionary Linux desktop settings synchronization tool that allows users to backup and restore their complete desktop environment across multiple devices using their own cloud storage. Built with Python and PyQt6, it provides a modern, user-friendly interface for managing Linux desktop configurations.

## 🏗️ Architecture

### Core Components

#### 1. Cloud Provider Abstraction (`core/cloud_providers/`)
- **Base Provider**: Abstract interface for all cloud storage providers
- **Google Drive Provider**: Full implementation for Google Drive integration
- **Provider Factory**: Creates and manages provider instances
- **Future Support**: OneDrive, Box, pCloud (architecture ready)

#### 2. Profile Detection System (`core/profile_detector.py`)
- **Intelligent Detection**: Automatically finds application profiles regardless of installation method
- **Multi-Format Support**: APT, Snap, Flatpak installations
- **Mozilla Applications**: Special handling for Firefox and Thunderbird profiles
- **Validation**: Ensures profile integrity before backup

#### 3. System Integration (`utils/system_utils.py`)
- **GNOME Settings Manager**: Handles dconf/gsettings operations
- **Desktop Environment Detection**: Validates GNOME compatibility
- **Settings Backup/Restore**: Complete desktop appearance synchronization
- **Custom Keybindings**: Preserves user-defined keyboard shortcuts

#### 4. File Management (`utils/file_utils.py`)
- **Archive Manager**: Creates and extracts tar.gz archives with compression
- **File Operations**: Safe copying, moving, and deletion with backups
- **Integrity Verification**: Checksum validation for all operations
- **Progress Tracking**: Real-time progress updates for long operations

#### 5. Backup & Restore Orchestration
- **Backup Manager**: Coordinates complete backup process
- **Restore Manager**: Handles intelligent restoration with conflict resolution
- **Metadata Management**: Tracks backup contents and compatibility
- **Error Handling**: Comprehensive error recovery and user feedback

#### 6. Modern GUI (`gui/main_window.py`)
- **PyQt6 Interface**: Modern, responsive user interface
- **Background Operations**: Non-blocking backup/restore with progress tracking
- **Status Management**: Real-time connection and operation status
- **User Feedback**: Comprehensive logging and error reporting

## 🔧 Technical Specifications

### Supported Applications
- **Firefox**: All installation methods (APT, Snap, Flatpak)
- **Thunderbird**: All installation methods with profile detection
- **GNOME Desktop**: Complete settings synchronization
- **Future**: VS Code, Terminal configurations, custom applications

### Cloud Storage Support
- **Google Drive**: Full implementation with OAuth 2.0
- **Planned**: Microsoft OneDrive, Box.com, pCloud
- **Architecture**: Provider-agnostic design for easy extension

### File Formats & Compression
- **Archives**: tar.gz compression for optimal size/speed balance
- **Metadata**: JSON format for human-readable backup information
- **Settings**: Native dconf/gsettings format preservation

### Security Features
- **OAuth 2.0**: Secure cloud authentication without storing passwords
- **Local Encryption**: Sensitive tokens encrypted with user-specific keys
- **Minimal Permissions**: Only necessary cloud storage access
- **Data Privacy**: No telemetry, all data remains in user's cloud

## 📋 Installation Requirements

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, Fedora 34+, openSUSE 15.3+)
- **Desktop Environment**: GNOME (primary), KDE/XFCE (limited support)
- **Python**: 3.8 or higher
- **Memory**: 512 MB RAM minimum, 1 GB recommended
- **Storage**: 100 MB for application, varies by backup size

### Dependencies
```bash
# System packages
sudo apt install python3 python3-pip python3-venv python3-dev python3-dbus python3-gi

# Python packages (installed automatically)
PyQt6>=6.4.0
google-api-python-client>=2.70.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=0.8.0
python-dbus>=1.2.18
psutil>=5.9.0
```

## 🚀 Installation & Setup

### Quick Installation
```bash
git clone https://github.com/lumisync/lumisync.git
cd lumisync
chmod +x install.sh
./install.sh
```

### Manual Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_lumisync.py

# Launch application
python -m lumisync.main
```

### First-Time Setup
1. **Launch LumiSync**: `./lumisync` or from applications menu
2. **Connect to Cloud**: Click "Mit Google Drive verbinden"
3. **Authorize Access**: Complete OAuth flow in browser
4. **Create Backup**: Click "Einstellungen sichern"
5. **Verify Upload**: Check your Google Drive for LumiSync folder

## 💼 Usage Guide

### Creating Your First Backup
1. **System Check**: LumiSync automatically detects your configuration
2. **Profile Detection**: Finds Firefox, Thunderbird, and other app profiles
3. **Settings Collection**: Gathers GNOME desktop settings
4. **Cloud Upload**: Securely uploads to your Google Drive
5. **Verification**: Confirms backup integrity

### Restoring on Another System
1. **Install LumiSync**: Use the same installation process
2. **Connect to Cloud**: Authenticate with the same Google account
3. **Download Backup**: LumiSync finds your existing backup
4. **System Preparation**: Creates backup of current settings
5. **Restoration**: Applies your synchronized settings
6. **Restart Applications**: Firefox/Thunderbird for complete restoration

### Advanced Features
- **Selective Restoration**: Choose which components to restore
- **Backup History**: Multiple backup versions with timestamps
- **Conflict Resolution**: Intelligent handling of setting conflicts
- **Progress Monitoring**: Real-time status and detailed logging

## 🛠️ Development

### Project Structure
```
lumisync/
├── core/                   # Core business logic
│   ├── cloud_providers/    # Cloud storage abstraction
│   ├── backup_manager.py   # Backup orchestration
│   ├── restore_manager.py  # Restore orchestration
│   └── profile_detector.py # Application profile detection
├── gui/                    # PyQt6 user interface
│   └── main_window.py      # Main application window
├── utils/                  # Utility modules
│   ├── system_utils.py     # GNOME/system integration
│   ├── file_utils.py       # File operations
│   └── logger.py           # Logging system
├── config/                 # Configuration
│   └── settings.py         # Application settings
└── main.py                 # Application entry point
```

### Adding New Cloud Providers
1. **Inherit from CloudProvider**: Implement abstract methods
2. **Register Provider**: Add to provider factory
3. **Test Implementation**: Verify all operations work
4. **Update GUI**: Add provider selection option

### Extending Application Support
1. **Define Detection Logic**: Add to `APPLICATION_PATHS`
2. **Implement Detection**: Extend `profile_detector.py`
3. **Test Backup/Restore**: Verify complete workflow
4. **Update Documentation**: Add to supported applications list

## 🔍 Troubleshooting

### Common Issues

#### Authentication Problems
- **Clear Credentials**: Delete `~/.config/lumisync/credentials.json`
- **Browser Issues**: Try different browser or incognito mode
- **Firewall**: Ensure port 8080 is accessible for OAuth callback

#### Profile Detection Failures
- **Application Not Found**: Ensure application is installed and run at least once
- **Permission Issues**: Check read access to profile directories
- **Multiple Installations**: LumiSync prefers Snap > Flatpak > APT

#### Backup/Restore Errors
- **Network Issues**: Check internet connection and Google Drive access
- **Storage Space**: Verify sufficient space in Google Drive
- **File Permissions**: Ensure write access to target directories

### Debug Mode
```bash
# Enable detailed logging
export LUMISYNC_DEBUG=1
python -m lumisync.main
```

### Log Files
- **Application Log**: `~/.local/share/lumisync/lumisync.log`
- **Debug Output**: Console when run from terminal
- **System Integration**: Check system journal for dbus errors

## 🔐 Security & Privacy

### Data Protection
- **Local Processing**: All operations performed locally
- **Encrypted Storage**: Sensitive tokens encrypted at rest
- **No Telemetry**: No data collection or analytics
- **User Control**: Complete ownership of backup data

### Cloud Security
- **OAuth 2.0**: Industry-standard authentication
- **Scoped Access**: Minimal required permissions
- **Revocable**: Access can be revoked anytime in Google account settings
- **Encrypted Transit**: All data encrypted during transfer

### Best Practices
- **Regular Backups**: Create backups before major system changes
- **Verify Restores**: Test restoration on non-production systems
- **Monitor Access**: Review cloud storage access regularly
- **Update Software**: Keep LumiSync updated for security patches

## 🚧 Roadmap

### Version 0.2.0 (Beta)
- **Multi-Cloud Support**: OneDrive, Box, pCloud integration
- **Selective Backup**: Choose specific applications/settings
- **Automated Scheduling**: Periodic backup creation
- **Enhanced GUI**: Advanced options and preferences

### Version 1.0.0 (Stable)
- **KDE Support**: Plasma desktop environment integration
- **Plugin Architecture**: Third-party extensions
- **Encryption**: End-to-end backup encryption
- **Team Features**: Shared configurations for organizations

### Long-term Vision
- **Cross-Platform**: Windows and macOS support
- **Mobile Companion**: Android/iOS apps for backup management
- **AI Integration**: Intelligent setting recommendations
- **Enterprise Features**: Centralized management and compliance

## 📞 Support & Community

### Getting Help
- **Documentation**: This comprehensive guide
- **GitHub Issues**: Report bugs and request features
- **Community Forum**: User discussions and tips
- **Email Support**: Direct developer contact

### Contributing
- **Code Contributions**: Pull requests welcome
- **Translations**: Help localize LumiSync
- **Testing**: Try on different distributions
- **Documentation**: Improve guides and tutorials

### License
LumiSync is released under the MIT License, ensuring freedom to use, modify, and distribute.

---

**LumiSync - Synchronize your Linux desktop settings with ease! 🌟**
