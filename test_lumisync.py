#!/usr/bin/env python3
"""
LumiSync Test Script
Quick test to verify core functionality
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from lumisync.core.profile_detector import ApplicationProfileDetector
        print("✅ Profile detector import OK")
        
        from lumisync.core.cloud_providers.google_drive import GoogleDriveProvider
        print("✅ Google Drive provider import OK")
        
        from lumisync.utils.system_utils import GnomeSettingsManager
        print("✅ System utils import OK")
        
        from lumisync.gui.main_window import MainWindow
        print("✅ GUI main window import OK")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_profile_detection():
    """Test profile detection functionality."""
    print("\nTesting profile detection...")
    
    try:
        from lumisync.core.profile_detector import ApplicationProfileDetector
        
        detector = ApplicationProfileDetector()
        profiles = detector.detect_all_profiles()
        
        print(f"✅ Detected {len(profiles)} application types")
        for app_name, app_profiles in profiles.items():
            for profile in app_profiles:
                print(f"  📦 {app_name}: {profile.install_type} - {profile.size_mb} MB")
        
        return True
    except Exception as e:
        print(f"❌ Profile detection failed: {e}")
        return False

def test_system_utils():
    """Test system utilities."""
    print("\nTesting system utilities...")
    
    try:
        from lumisync.utils.system_utils import GnomeSettingsManager
        
        manager = GnomeSettingsManager()
        system_info = manager.get_system_info()
        
        print(f"✅ System info: {system_info}")
        return True
    except Exception as e:
        print(f"❌ System utils test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 LumiSync Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_profile_detection,
        test_system_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! LumiSync is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check dependencies.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
