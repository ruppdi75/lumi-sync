#!/usr/bin/env python3
"""
LumiSync Demo Mode
Runs LumiSync without Google API dependencies for testing
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_demo():
    """Run LumiSync in demo mode."""
    print("🌟 LumiSync Demo Mode")
    print("=" * 40)
    
    try:
        # Test core functionality without Google API
        print("Testing core components...")
        
        # Test profile detection
        from lumisync.core.profile_detector import ApplicationProfileDetector
        detector = ApplicationProfileDetector()
        profiles = detector.detect_all_profiles()
        
        print(f"✅ Profile Detection: {len(profiles)} apps found")
        for app_name, app_profiles in profiles.items():
            for profile in app_profiles:
                print(f"  📦 {app_name}: {profile.install_type} - {profile.size_mb} MB")
        
        # Test system utils
        from lumisync.utils.system_utils import GnomeSettingsManager
        manager = GnomeSettingsManager()
        system_info = manager.get_system_info()
        print(f"✅ System Info: {system_info}")
        
        # Test settings backup (without cloud)
        print("\n🔄 Testing settings backup...")
        settings = manager.backup_settings()
        settings_count = len(settings.get('settings', {}))
        print(f"✅ GNOME Settings: {settings_count} settings backed up")
        
        print("\n🎉 LumiSync Core Functionality: WORKING!")
        print("📝 Note: For full functionality, install Google API libraries:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate") 
        print("   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib PyQt6")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
