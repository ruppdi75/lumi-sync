# LumiSync 🌟

**Professional Linux Settings Synchronization Tool**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://pypi.org/project/PyQt6/)
[![Status: PoC](https://img.shields.io/badge/Status-Proof%20of%20Concept-orange.svg)]()

LumiSync is a cutting-edge, professional-grade application designed for worldwide use by both beginners and Linux professionals. It provides seamless backup and restoration of your Linux desktop settings, application profiles, and configurations using your preferred cloud storage provider.

## 🎯 Vision

Create the most intuitive and powerful Linux settings synchronization tool that works across all distributions, supports multiple cloud providers, and provides enterprise-grade reliability with consumer-friendly simplicity.

## ✨ Features

### 🎯 Core Functionality
- **One-click backup and restore** of desktop settings
- **Intelligent profile detection** for Firefox and Thunderbird (APT, Snap, Flatpak)
- **GNOME/dconf settings synchronization** (themes, wallpapers, dock favorites)
- **Multi-cloud support** - Google Drive, OneDrive, Box, pCloud with your own API credentials
- **Cross-distribution compatibility** - Ubuntu, Fedora, openSUSE, Arch, and more
- **Categorized selection** - Desktop, Files, System Settings, System Tools
- **Real-time progress tracking** with pause/resume/stop controls
- **Advanced logging system** with filtering and export capabilities

### 🛡️ Privacy & Security
- **Your data stays yours** - No central servers, use your own cloud storage
- **OAuth 2.0 authentication** for secure cloud access
- **Local encryption** of sensitive tokens
- **Minimal permissions** - Only accesses what's necessary

### 🎨 Modern User Interface
- **Dark Theme Design** - Professional, eye-friendly interface
- **Tabbed Layout** - Progress, Logs, and Results in organized tabs
- **Responsive Design** - Adapts to different screen sizes
- **Intuitive Controls** - Easy-to-use buttons and checkboxes
- **Real-time Progress Tracking** - Live progress bars and status updates
- **Advanced Logging System** - Multi-level logging with filtering and export
- **Professional Reporting** - HTML export and detailed analytics
- **Multi-language support** (English, German, more coming)

## 🚀 Quick Start

### Installation

#### Option 1: From Source (Recommended for PoC)
```bash
git clone https://github.com/lumisync/lumisync.git
cd lumisync
pip install -r requirements.txt
python -m lumisync.main
```

#### Option 2: AppImage (Coming Soon)
```bash
wget https://github.com/lumisync/lumisync/releases/latest/download/LumiSync.AppImage
chmod +x LumiSync.AppImage
./LumiSync.AppImage
```

### First Run
1. **Setup API Credentials** (for Google Drive)
   - Copy `lumisync/config/google_credentials.json` to `google_credentials_dev.json`
   - Add your Google API credentials to the dev file
   - See [INSTALLATION.md](INSTALLATION.md) for detailed setup

2. **Launch LumiSync**
   ```bash
   python -m lumisync.main
   ```

3. **Connect to your cloud storage**
4. **Create your first backup** with one click
4. **Restore on any other Linux system** just as easily!

## 🏗️ Architecture

LumiSync is built with a modular, extensible architecture:

```
lumisync/
├── core/                   # Core business logic
│   ├── cloud_providers/    # Cloud storage abstraction
│   ├── profile_detector/   # Intelligent app profile detection
│   └── backup_manager/     # Backup and restore orchestration
├── gui/                    # Modern PyQt6 interface
├── utils/                  # System utilities and helpers
└── config/                 # Configuration and constants
```

## 🔧 Supported Applications

### Desktop Environment
- ✅ GNOME settings (dconf/gsettings)
- ✅ Desktop themes and appearance
- ✅ Dock/panel favorites and layout
- 🔄 KDE Plasma (planned)
- 🔄 XFCE (planned)

### Applications
- ✅ Firefox (all installation methods)
- ✅ Thunderbird (all installation methods)
- 🔄 VS Code/Codium (planned)
- 🔄 Terminal configurations (planned)
- 🔄 Custom application support (planned)

### Cloud Providers
- ✅ Google Drive (PoC ready)
- 🔄 Microsoft OneDrive (planned)
- 🔄 Box.com (planned)
- 🔄 pCloud (planned)

## 🛠️ Development

### Prerequisites
- Python 3.8+
- Linux system with GNOME (for PoC)
- Cloud storage account

### Development Setup
```bash
git clone https://github.com/lumisync/lumisync.git
cd lumisync
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
black lumisync/
flake8 lumisync/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Areas where we need help:
- 🌍 **Translations** - Help make LumiSync available in your language
- 🐧 **Distribution testing** - Test on different Linux distributions
- 🔌 **Cloud providers** - Implement additional cloud storage backends
- 📱 **Application support** - Add support for more applications
- 🎨 **UI/UX improvements** - Make LumiSync even more user-friendly

## 📋 Roadmap

### Version 0.1.0 (PoC) - Current
- [x] Project structure and architecture
- [x] Google Drive integration
- [x] Basic GUI framework
- [ ] Firefox/Thunderbird profile detection
- [ ] GNOME settings backup/restore
- [ ] End-to-end workflow

### Version 0.2.0 (Beta)
- [ ] Multi-cloud provider support
- [ ] Enhanced error handling
- [ ] Selective backup options
- [ ] Automatic conflict resolution

### Version 1.0.0 (Stable)
- [ ] Full application ecosystem support
- [ ] Advanced scheduling options
- [ ] Plugin architecture
- [ ] Professional packaging (AppImage, Flatpak, Snap)

## 📄 License

LumiSync is released under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Inspired by the excellent work of [AnduinOS](https://github.com/Anduin2017/AnduinOS)
- Built with love for the Linux community
- Special thanks to all contributors and testers

## 📞 Support

- 📖 **Documentation**: [docs.lumisync.org](https://docs.lumisync.org)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/lumisync/lumisync/issues)
- 💬 **Community**: [Discord Server](https://discord.gg/lumisync)
- 📧 **Email**: support@lumisync.org

---

**Made with ❤️ for the Linux community**
