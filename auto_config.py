#!/usr/bin/env python3
"""
Auto-Configuration Module
Automatically detects system settings and generates config.json
"""

import json
import logging
import platform
from pathlib import Path
from typing import Dict, Optional

from nic_detector import NICDetector

logger = logging.getLogger(__name__)


class AutoConfig:
    """Automatically configure WiFi Radar based on detected hardware"""
    
    def __init__(self):
        self.detector = NICDetector()
        self.platform = platform.system()
        
    def detect_and_configure(self) -> Dict:
        """
        Detect system configuration and generate config
        
        Returns:
            Configuration dictionary
        """
        logger.info("Starting auto-configuration...")
        
        # Detect WiFi interface
        wifi_interface = self.detector.get_best_wifi_interface()
        
        if not wifi_interface:
            logger.warning("No WiFi interface detected, using defaults")
            return self._get_default_config()
        
        # Build configuration
        config = self._build_config(wifi_interface)
        
        logger.info("Auto-configuration complete")
        return config
    
    def _build_config(self, interface_info: Dict) -> Dict:
        """
        Build configuration from detected interface
        
        Args:
            interface_info: Detected interface information
            
        Returns:
            Configuration dictionary
        """
        device = interface_info.get('device', 'wlan0')
        
        # Determine interface name based on platform
        if self.platform == 'Darwin':  # macOS
            # On macOS, we use the device name directly (e.g., en0)
            # Monitor mode is handled differently via airport utility
            interface_name = device
        else:  # Linux
            # On Linux, append 'mon' if not already present
            if 'mon' not in device:
                interface_name = f"{device}mon"
            else:
                interface_name = device
        
        # Get recommended channel
        channel = self.detector.get_recommended_channel(interface_info)
        
        # Build config
        config = {
            "capture": {
                "interface": interface_name,
                "channel": channel,
                "frequency_ghz": 2.4,
                "sampling_duration": 0.1
            },
            "filtering": {
                "bssid_filter": [],
                "packet_types": ["Beacon", "Data"]
            },
            "features": {
                "rssi_enabled": True,
                "phase_enabled": True,
                "fft_enabled": True
            },
            "spatial": {
                "grid_size": [10, 10],
                "bin_mode": "time",
                "bin_duration": 1.0,
                "normalization": True
            },
            "visualization": {
                "update_interval": 0.5,
                "colormap": "hot",
                "figsize": [10, 8]
            },
            "_auto_detected": {
                "platform": self.platform,
                "device": device,
                "available_channels": interface_info.get('available_channels', []),
                "detected_at": self._get_timestamp()
            }
        }
        
        return config
    
    def _get_default_config(self) -> Dict:
        """
        Get default configuration
        
        Returns:
            Default configuration dictionary
        """
        # Platform-specific defaults
        if self.platform == 'Darwin':  # macOS
            interface = "en0"
        else:  # Linux
            interface = "wlan0mon"
        
        config = {
            "capture": {
                "interface": interface,
                "channel": 6,
                "frequency_ghz": 2.4,
                "sampling_duration": 0.1
            },
            "filtering": {
                "bssid_filter": [],
                "packet_types": ["Beacon", "Data"]
            },
            "features": {
                "rssi_enabled": True,
                "phase_enabled": True,
                "fft_enabled": True
            },
            "spatial": {
                "grid_size": [10, 10],
                "bin_mode": "time",
                "bin_duration": 1.0,
                "normalization": True
            },
            "visualization": {
                "update_interval": 0.5,
                "colormap": "hot",
                "figsize": [10, 8]
            },
            "_auto_detected": {
                "platform": self.platform,
                "note": "No WiFi interface detected, using platform defaults",
                "detected_at": self._get_timestamp()
            }
        }
        
        return config
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save_config(self, config: Dict, filepath: str = "config.json", backup: bool = True):
        """
        Save configuration to file
        
        Args:
            config: Configuration dictionary
            filepath: Path to save configuration
            backup: Whether to backup existing config
        """
        config_path = Path(filepath)
        
        # Backup existing config
        if backup and config_path.exists():
            backup_path = config_path.with_suffix('.json.backup')
            logger.info(f"Backing up existing config to {backup_path}")
            import shutil
            shutil.copy(config_path, backup_path)
        
        # Save new config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info(f"Configuration saved to {filepath}")
    
    def print_config_summary(self, config: Dict):
        """Print configuration summary"""
        print("\n" + "="*60)
        print("Auto-Generated Configuration")
        print("="*60)
        print(f"Platform: {config.get('_auto_detected', {}).get('platform', 'Unknown')}")
        print(f"Interface: {config['capture']['interface']}")
        print(f"Channel: {config['capture']['channel']}")
        print(f"Grid Size: {config['spatial']['grid_size']}")
        print(f"Update Interval: {config['visualization']['update_interval']}s")
        
        auto_info = config.get('_auto_detected', {})
        if 'available_channels' in auto_info:
            channels = auto_info['available_channels']
            if channels:
                print(f"Available Channels: {', '.join(map(str, channels[:10]))}")
        
        print("="*60 + "\n")


def main():
    """Main function for standalone execution"""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    parser = argparse.ArgumentParser(
        description='Auto-configure WiFi Radar for your system'
    )
    parser.add_argument(
        '-o', '--output',
        default='config.json',
        help='Output configuration file (default: config.json)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not backup existing config file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show configuration without saving'
    )
    
    args = parser.parse_args()
    
    # Create auto-config instance
    auto_config = AutoConfig()
    
    # Detect and generate config
    print("\nDetecting system configuration...")
    config = auto_config.detect_and_configure()
    
    # Print summary
    auto_config.print_config_summary(config)
    
    # Save or display
    if args.dry_run:
        print("Configuration (dry-run, not saved):")
        print(json.dumps(config, indent=4))
    else:
        auto_config.save_config(
            config,
            filepath=args.output,
            backup=not args.no_backup
        )
        print(f"✓ Configuration saved to {args.output}")
        
        if not args.no_backup and Path(args.output).with_suffix('.json.backup').exists():
            print(f"✓ Previous configuration backed up to {args.output}.backup")


if __name__ == '__main__':
    main()
