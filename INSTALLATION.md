# Installation Guide

## System Requirements

### Supported Operating Systems
- **Ubuntu** 20.04+ (Primary support)
- **Fedora** 35+ 
- **openSUSE** Leap 15.4+
- **Arch Linux** (Latest)
- **Debian** 11+
- **Pop!_OS** 22.04+
- **Linux Mint** 20+

### Python Requirements
- **Python** 3.8 or higher
- **pip** package manager

### Desktop Environment Support
- **GNOME** (Full support)
- **KDE Plasma** (Planned)
- **XFCE** (Planned)
- **Other DEs** (Basic support)

## Installation Methods

### Method 1: From Source (Recommended for PoC)

1. **Clone the repository**
   ```bash
   git clone https://github.com/ruppdi75/lumi-sync.git
   cd lumi-sync
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Ubuntu/Debian
   # or
   source venv/bin/activate.fish  # On Fish shell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python -m lumisync.main
   ```

### Method 2: Using the Install Script

1. **Download and run the install script**
   ```bash
   wget https://raw.githubusercontent.com/ruppdi75/lumi-sync/main/install.sh
   chmod +x install.sh
   ./install.sh
   ```

2. **Launch from desktop or terminal**
   ```bash
   lumisync
   ```

### Method 3: AppImage (Coming Soon)

1. **Download the AppImage**
   ```bash
   wget https://github.com/ruppdi75/lumi-sync/releases/latest/download/LumiSync.AppImage
   chmod +x LumiSync.AppImage
   ```

2. **Run the AppImage**
   ```bash
   ./LumiSync.AppImage
   ```

## Cloud Storage Setup

### Google Drive (Default for PoC)
1. The application includes pre-configured API credentials for testing
2. Click "Connect" and authorize access
3. Your data is stored in a dedicated LumiSync folder

### Other Providers (Production)
For production use, you'll need to set up your own API credentials:

#### Google Drive
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Add credentials to `lumisync/config/google_credentials.json`

#### OneDrive
1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new application
3. Configure API permissions
4. Add credentials to configuration

#### Box
1. Go to [Box Developer Console](https://developer.box.com/)
2. Create a new app
3. Configure OAuth 2.0
4. Add credentials to configuration

#### pCloud
1. Go to [pCloud API Console](https://docs.pcloud.com/)
2. Register your application
3. Get API credentials
4. Add to configuration

## Troubleshooting

### Common Issues

#### PyQt6 Installation Issues
```bash
# On Ubuntu/Debian
sudo apt-get install python3-pyqt6

# On Fedora
sudo dnf install python3-PyQt6

# On Arch
sudo pacman -S python-pyqt6
```

#### Permission Issues
```bash
# Ensure proper permissions for config directory
chmod 755 ~/.config/lumisync
chmod 600 ~/.config/lumisync/credentials.json
```

#### Cloud Connection Issues
1. Check internet connection
2. Verify API credentials
3. Check firewall settings
4. Review application logs

### Getting Help

If you encounter issues:

1. **Check the logs** - Available in the application's Logs tab
2. **Search existing issues** - [GitHub Issues](https://github.com/ruppdi75/lumi-sync/issues)
3. **Create a new issue** - Include system info and logs
4. **Join our community** - Discord server for real-time help

## Development Setup

For developers wanting to contribute:

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/lumi-sync.git
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run tests**
   ```bash
   python -m pytest tests/
   ```

5. **Start developing!**

## Uninstallation

### Remove Application
```bash
# If installed via pip
pip uninstall lumisync

# If installed via script
sudo rm -rf /opt/lumisync
sudo rm /usr/local/bin/lumisync
sudo rm /usr/share/applications/lumisync.desktop
```

### Remove User Data
```bash
# Remove configuration and cached data
rm -rf ~/.config/lumisync
rm -rf ~/.cache/lumisync
```

**Note**: This will not remove your cloud storage backups.
