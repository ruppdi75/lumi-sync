# Changelog

All notable changes to LumiSync will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-10

### Added
- **pCloud Integration** - Full pCloud provider support with real authentication
- **Provider Selection Dialog** - Professional interface for choosing cloud storage provider
- **Automatic Folder Creation** - "Lumi-Sync" folder created automatically in your cloud storage
- **Real-World Authentication** - OAuth 2.0 for Google Drive, username/password for pCloud
- **Enhanced UI Components** - Professional two-column layout with improved visual feedback

### Fixed
- **Selection Buttons** - Select All, Select None, and Recommended buttons now work correctly
- **UI State Updates** - Proper signal emission for selection changes and UI updates
- **Cloud Connection Logic** - Real authentication instead of demo/example accounts
- **Backup Organization** - All backups now stored in dedicated "Lumi-Sync" folder

### Changed
- **Provider Factory** - Updated to include pCloud alongside Google Drive
- **Authentication Flow** - Replaced demo connections with real cloud provider authentication
- **File Storage Structure** - Organized backup storage in cloud-specific folders
- **User Experience** - Improved visual feedback and status updates throughout the application

### Technical Improvements
- Added `requests` dependency for pCloud API integration
- Implemented abstract method requirements for cloud providers
- Enhanced error handling and logging for cloud operations
- Improved component architecture with provider dialog integration

## [Unreleased]

### Added
- Modern dark theme GUI with professional styling
- Tabbed interface (Setup, Progress, Logs, Results)
- Real-time progress tracking with pause/resume/stop controls
- Advanced logging system with filtering and export capabilities
- Multi-cloud provider support (Google Drive, OneDrive, Box, pCloud)
- Categorized backup/restore selection (Desktop, Files, System Settings, System Tools)
- Professional HTML report generation
- Statistics dashboard with success rates and timing
- Responsive design that adapts to different screen sizes
- Modern progress bars with gradient styling
- Enhanced error handling and recovery mechanisms

### Changed
- Complete GUI overhaul from basic interface to modern professional design
- Improved user experience with intuitive controls and clear navigation
- Enhanced backup/restore workflow with better progress indication
- Updated documentation with comprehensive installation and contribution guides

### Technical Improvements
- Modular GUI architecture with reusable components
- Enhanced thread management for background operations
- Improved error handling and user feedback
- Better separation of concerns between UI and core logic
- Professional color scheme and typography

## [0.1.0] - 2024-XX-XX (PoC Release)

### Added
- Initial Proof of Concept release
- Basic backup and restore functionality for GNOME settings
- Google Drive integration with OAuth 2.0
- Firefox and Thunderbird profile detection and backup
- Cross-distribution compatibility (Ubuntu focus)
- Basic PyQt6 GUI interface
- Configuration management system
- Logging infrastructure
- Package detection for installed applications

### Core Features
- GNOME/dconf settings backup and restore
- Firefox profile backup (supports APT, Snap, Flatpak installations)
- Thunderbird profile backup (supports APT, Snap, Flatpak installations)
- Google Drive cloud storage integration
- Intelligent application profile detection
- Cross-platform Python implementation

### Security
- OAuth 2.0 authentication for cloud providers
- Local token encryption
- Minimal permission requirements
- No central server dependency

### Documentation
- Comprehensive README with installation instructions
- API documentation for core components
- User guide for basic operations
- Developer setup instructions

---

## Version History

### Upcoming Releases

#### v0.2.0 - Enhanced GUI (Current Development)
- Modern dark theme interface
- Tabbed layout with organized sections
- Real-time progress tracking
- Advanced logging and reporting
- Multi-cloud provider support

#### v0.3.0 - Extended Platform Support (Planned)
- KDE Plasma desktop environment support
- XFCE desktop environment support
- Additional Linux distribution testing
- Improved application detection algorithms

#### v0.4.0 - Advanced Features (Planned)
- Scheduled automatic backups
- Incremental backup support
- Backup versioning and history
- Advanced filtering options
- Plugin architecture for extensibility

#### v1.0.0 - Production Release (Planned)
- Full multi-desktop environment support
- Complete cloud provider ecosystem
- Enterprise features and management
- Comprehensive testing and stability
- Professional documentation and support

---

## Development Notes

### Breaking Changes
- v0.2.0: GUI architecture completely redesigned
- Future versions may require configuration migration

### Deprecations
- Legacy GUI components will be removed in v0.3.0
- Old configuration format support ends in v0.4.0

### Migration Guides
- v0.1.0 to v0.2.0: No migration required, configurations are compatible
- Future migrations will be documented with automated tools

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to LumiSync development.

## Support

- **Issues**: [GitHub Issues](https://github.com/ruppdi75/lumi-sync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ruppdi75/lumi-sync/discussions)
- **Documentation**: [Installation Guide](INSTALLATION.md)
