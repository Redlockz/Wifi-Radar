#!/usr/bin/env python3
"""
Validation script for macOS M2 optimization features
Tests the auto-configuration and NIC detection functionality
"""

import sys
import json
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    try:
        from nic_detector import NICDetector
        from auto_config import AutoConfig
        print("  ✓ nic_detector imported successfully")
        print("  ✓ auto_config imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_nic_detector():
    """Test NIC detector functionality"""
    print("\nTesting NIC Detector...")
    try:
        from nic_detector import NICDetector
        
        detector = NICDetector()
        print(f"  ✓ Platform detected: {detector.platform}")
        
        # Try to detect interfaces
        interfaces = detector.detect_all_interfaces()
        print(f"  ✓ Interface detection completed ({len(interfaces)} found)")
        
        # Try to get best interface
        best = detector.get_best_wifi_interface()
        if best:
            print(f"  ✓ Best interface: {best.get('device', 'unknown')}")
        else:
            print("  ℹ No WiFi interface detected (expected in test environment)")
        
        return True
    except Exception as e:
        print(f"  ✗ NIC Detector test failed: {e}")
        return False

def test_auto_config():
    """Test auto-configuration functionality"""
    print("\nTesting Auto Configuration...")
    try:
        from auto_config import AutoConfig
        
        auto_config = AutoConfig()
        print(f"  ✓ AutoConfig initialized for platform: {auto_config.platform}")
        
        # Generate config
        config = auto_config.detect_and_configure()
        print("  ✓ Configuration generated successfully")
        
        # Validate config structure
        required_keys = ['capture', 'filtering', 'features', 'spatial', 'visualization']
        for key in required_keys:
            if key not in config:
                print(f"  ✗ Missing required key: {key}")
                return False
        print("  ✓ Configuration structure validated")
        
        # Check auto-detected info
        if '_auto_detected' in config:
            auto_info = config['_auto_detected']
            print(f"  ✓ Auto-detected info included: {auto_info.get('platform')}")
        
        # Validate interface name
        interface = config['capture']['interface']
        print(f"  ✓ Interface configured: {interface}")
        
        # Validate channel
        channel = config['capture']['channel']
        if not (1 <= channel <= 14):
            print(f"  ⚠ Channel {channel} outside typical range")
        else:
            print(f"  ✓ Channel configured: {channel}")
        
        return True
    except Exception as e:
        print(f"  ✗ Auto Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_file_operations():
    """Test config file save/load"""
    print("\nTesting Config File Operations...")
    try:
        from auto_config import AutoConfig
        import tempfile
        import os
        
        auto_config = AutoConfig()
        config = auto_config.detect_and_configure()
        
        # Test save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            auto_config.save_config(config, filepath=temp_path, backup=False)
            print(f"  ✓ Config saved to temporary file")
            
            # Verify file exists
            if not Path(temp_path).exists():
                print("  ✗ Config file not created")
                return False
            print("  ✓ Config file exists")
            
            # Verify can be loaded
            with open(temp_path, 'r') as f:
                loaded_config = json.load(f)
            print("  ✓ Config file is valid JSON")
            
            # Verify content matches
            if loaded_config['capture']['interface'] != config['capture']['interface']:
                print("  ✗ Config content mismatch")
                return False
            print("  ✓ Config content verified")
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return True
    except Exception as e:
        print(f"  ✗ File operations test failed: {e}")
        return False

def test_platform_awareness():
    """Test platform-specific behavior"""
    print("\nTesting Platform Awareness...")
    try:
        import platform
        from auto_config import AutoConfig
        
        system = platform.system()
        print(f"  ✓ Running on: {system}")
        
        auto_config = AutoConfig()
        config = auto_config.detect_and_configure()
        
        interface = config['capture']['interface']
        
        # Verify platform-appropriate defaults
        if system == 'Darwin':  # macOS
            # macOS should use en0-style naming
            if interface.startswith('en'):
                print(f"  ✓ macOS interface naming detected: {interface}")
            else:
                print(f"  ℹ Unexpected macOS interface name: {interface}")
        elif system == 'Linux':
            # Linux should use wlan-style naming
            if 'wlan' in interface or 'mon' in interface:
                print(f"  ✓ Linux interface naming detected: {interface}")
            else:
                print(f"  ℹ Unexpected Linux interface name: {interface}")
        
        return True
    except Exception as e:
        print(f"  ✗ Platform awareness test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("="*60)
    print("WiFi Radar - macOS M2 Optimization Validation")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("NIC Detector", test_nic_detector),
        ("Auto Configuration", test_auto_config),
        ("File Operations", test_config_file_operations),
        ("Platform Awareness", test_platform_awareness),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "="*60)
    print("Validation Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All validation tests passed!")
        print("\nThe macOS M2 optimization features are working correctly.")
        print("\nYou can now use:")
        print("  - python3 wifi_radar.py --detect-nic")
        print("  - python3 wifi_radar.py --auto-config")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
