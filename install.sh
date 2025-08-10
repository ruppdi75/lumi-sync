#!/bin/bash
# LumiSync Installation Script
# Installs dependencies and sets up LumiSync

set -e

echo "🌟 LumiSync Installation Script"
echo "================================"

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: LumiSync requires Linux"
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required"
    echo "Install with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Check for GNOME
if [[ "$XDG_CURRENT_DESKTOP" != *"GNOME"* ]] && [[ "$DESKTOP_SESSION" != *"gnome"* ]]; then
    echo "⚠️  Warning: LumiSync is optimized for GNOME desktop"
    echo "Some features may not work on other desktop environments"
fi

echo "✅ System requirements check passed"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt update
sudo apt install -y python3-dev python3-dbus python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Install Python packages
echo "📚 Installing Python packages..."
pip install --no-cache-dir -r requirements.txt

# Create desktop entry
echo "🖥️  Creating desktop entry..."
DESKTOP_FILE="$HOME/.local/share/applications/lumisync.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=LumiSync
Comment=Synchronize your Linux desktop settings across devices
Comment[de]=Synchronisieren Sie Ihre Linux-Desktop-Einstellungen zwischen Geräten
Exec=$PWD/venv/bin/python -m lumisync.main
Path=$PWD
Icon=preferences-desktop-theme
Terminal=false
Type=Application
Categories=Utility;System;Settings;
Keywords=sync;backup;settings;desktop;cloud;
StartupNotify=true
StartupWMClass=LumiSync
EOF

# Make executable
chmod +x "$DESKTOP_FILE"

# Create launcher script
echo "🚀 Creating launcher script..."
cat > lumisync << 'EOF'
#!/bin/bash
# LumiSync Launcher Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run LumiSync
python -m lumisync.main "$@"
EOF

chmod +x lumisync

# Test installation
echo "🧪 Testing installation..."
source venv/bin/activate
python test_lumisync.py

echo ""
echo "🎉 LumiSync installation completed successfully!"
echo ""
echo "To run LumiSync:"
echo "  ./lumisync                    # From this directory"
echo "  python -m lumisync.main       # With virtual environment activated"
echo "  Search 'LumiSync' in applications menu"
echo ""
echo "First time setup:"
echo "1. Run LumiSync"
echo "2. Click 'Mit Google Drive verbinden'"
echo "3. Authorize access in your browser"
echo "4. Create your first backup!"
echo ""
echo "📖 For help and documentation, visit: https://github.com/lumisync/lumisync"
