#!/usr/bin/env python3
"""
Network Interface Card (NIC) Detection and Reconnaissance
Detects WiFi interfaces and capabilities on Linux and macOS
"""

import platform
import subprocess
import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class NICDetector:
    """Detects and analyzes network interfaces for WiFi capability"""
    
    def __init__(self):
        self.platform = platform.system()
        self.interfaces = []
        
    def detect_all_interfaces(self) -> List[Dict]:
        """
        Detect all network interfaces on the system
        
        Returns:
            List of interface information dictionaries
        """
        if self.platform == 'Darwin':  # macOS
            return self._detect_macos_interfaces()
        elif self.platform == 'Linux':
            return self._detect_linux_interfaces()
        else:
            logger.warning(f"Unsupported platform: {self.platform}")
            return []
    
    def _detect_macos_interfaces(self) -> List[Dict]:
        """Detect network interfaces on macOS"""
        interfaces = []
        
        try:
            # Use networksetup to list all network services
            result = subprocess.run(
                ['networksetup', '-listallhardwareports'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output
            current_device = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('Hardware Port:'):
                    if current_device:
                        interfaces.append(current_device)
                    current_device = {'name': line.split(':', 1)[1].strip()}
                elif line.startswith('Device:'):
                    current_device['device'] = line.split(':', 1)[1].strip()
                elif line.startswith('Ethernet Address:'):
                    current_device['mac'] = line.split(':', 1)[1].strip()
            
            if current_device:
                interfaces.append(current_device)
            
            # Filter for WiFi interfaces
            wifi_interfaces = []
            for iface in interfaces:
                if 'Wi-Fi' in iface.get('name', '') or 'AirPort' in iface.get('name', ''):
                    device = iface.get('device', '')
                    wifi_info = self._get_macos_wifi_info(device)
                    iface.update(wifi_info)
                    iface['is_wifi'] = True
                    wifi_interfaces.append(iface)
            
            return wifi_interfaces
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error detecting macOS interfaces: {e}")
            return []
        except FileNotFoundError:
            logger.error("networksetup command not found (macOS only)")
            return []
    
    def _get_macos_wifi_info(self, device: str) -> Dict:
        """Get detailed WiFi information for macOS interface"""
        info = {
            'device': device,
            'supports_monitor': True,  # macOS generally supports monitor mode
            'current_channel': None,
            'available_channels': []
        }
        
        try:
            # Use airport utility to get WiFi info
            airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
            
            # Get current channel
            result = subprocess.run(
                [airport_path, '-I'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'channel:' in line.lower():
                        match = re.search(r'channel:\s*(\d+)', line, re.IGNORECASE)
                        if match:
                            info['current_channel'] = int(match.group(1))
                    elif 'ssid:' in line.lower():
                        match = re.search(r'ssid:\s*(.+)', line, re.IGNORECASE)
                        if match:
                            info['current_ssid'] = match.group(1).strip()
            
            # Get available channels (scan)
            result = subprocess.run(
                [airport_path, '-s'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                channels = set()
                for line in result.stdout.split('\n')[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            channel = int(parts[2])
                            channels.add(channel)
                        except (ValueError, IndexError):
                            pass
                info['available_channels'] = sorted(list(channels))
        
        except FileNotFoundError:
            logger.warning("airport utility not found")
        except Exception as e:
            logger.error(f"Error getting macOS WiFi info: {e}")
        
        return info
    
    def _detect_linux_interfaces(self) -> List[Dict]:
        """Detect network interfaces on Linux"""
        interfaces = []
        
        try:
            # Use iw to list wireless interfaces
            result = subprocess.run(
                ['iw', 'dev'],
                capture_output=True,
                text=True,
                check=True
            )
            
            current_iface = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('Interface'):
                    if current_iface:
                        interfaces.append(current_iface)
                    current_iface = {
                        'device': line.split()[1],
                        'is_wifi': True,
                        'platform': 'Linux'
                    }
                elif line.startswith('type'):
                    current_iface['type'] = line.split()[1]
                    current_iface['supports_monitor'] = True
                elif line.startswith('channel'):
                    match = re.search(r'(\d+)', line)
                    if match:
                        current_iface['current_channel'] = int(match.group(1))
            
            if current_iface:
                interfaces.append(current_iface)
            
            # Get additional info for each interface
            for iface in interfaces:
                device = iface['device']
                # Get available channels
                channels = self._get_linux_channels(device)
                iface['available_channels'] = channels
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error detecting Linux interfaces: {e}")
            return []
        except FileNotFoundError:
            logger.error("iw command not found (Linux only)")
            return []
        
        return interfaces
    
    def _get_linux_channels(self, device: str) -> List[int]:
        """Get available channels for Linux WiFi interface"""
        channels = []
        
        try:
            result = subprocess.run(
                ['iw', 'phy'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'MHz' in line and '[' in line:
                        match = re.search(r'\[(\d+)\]', line)
                        if match:
                            channels.append(int(match.group(1)))
        except Exception as e:
            logger.error(f"Error getting Linux channels: {e}")
        
        return channels if channels else list(range(1, 12))  # Default 2.4GHz channels
    
    def get_best_wifi_interface(self) -> Optional[Dict]:
        """
        Get the best WiFi interface for monitoring
        
        Returns:
            Dictionary with interface information or None
        """
        interfaces = self.detect_all_interfaces()
        
        if not interfaces:
            logger.warning("No WiFi interfaces detected")
            return None
        
        # Prefer interfaces not currently in monitor mode
        for iface in interfaces:
            if iface.get('type') != 'monitor':
                return iface
        
        # Return first available
        return interfaces[0] if interfaces else None
    
    def get_recommended_channel(self, interface_info: Dict) -> int:
        """
        Get recommended channel based on available channels and current usage
        
        Args:
            interface_info: Interface information dictionary
            
        Returns:
            Recommended channel number
        """
        available = interface_info.get('available_channels', [])
        current = interface_info.get('current_channel')
        
        # If current channel is available, use it
        if current and current in available:
            return current
        
        # Otherwise, use channel 6 (common default) if available
        if 6 in available:
            return 6
        
        # Or first available channel
        if available:
            return available[0]
        
        # Default to channel 6
        return 6
    
    def print_interface_info(self, interface_info: Dict):
        """Print formatted interface information"""
        print("\n" + "="*60)
        print("WiFi Interface Information")
        print("="*60)
        print(f"Platform: {self.platform}")
        print(f"Device: {interface_info.get('device', 'Unknown')}")
        print(f"Name: {interface_info.get('name', 'Unknown')}")
        
        if 'mac' in interface_info:
            print(f"MAC Address: {interface_info['mac']}")
        
        if 'current_ssid' in interface_info:
            print(f"Current SSID: {interface_info['current_ssid']}")
        
        if 'current_channel' in interface_info:
            print(f"Current Channel: {interface_info['current_channel']}")
        
        if 'available_channels' in interface_info:
            channels = interface_info['available_channels']
            if channels:
                print(f"Available Channels: {', '.join(map(str, channels[:10]))}")
                if len(channels) > 10:
                    print(f"                    ... and {len(channels) - 10} more")
        
        print(f"Monitor Mode Support: {'Yes' if interface_info.get('supports_monitor') else 'Unknown'}")
        print("="*60 + "\n")


def main():
    """Main function for standalone execution"""
    logging.basicConfig(level=logging.INFO)
    
    detector = NICDetector()
    
    print("\nScanning for WiFi interfaces...")
    interfaces = detector.detect_all_interfaces()
    
    if not interfaces:
        print("No WiFi interfaces detected.")
        print("\nNote: This tool requires:")
        print("  - macOS: Built-in WiFi hardware")
        print("  - Linux: 'iw' utility installed")
        return
    
    print(f"\nFound {len(interfaces)} WiFi interface(s):\n")
    
    for i, iface in enumerate(interfaces, 1):
        print(f"\n--- Interface {i} ---")
        detector.print_interface_info(iface)
    
    # Show recommendation
    best = detector.get_best_wifi_interface()
    if best:
        print("\nRecommended Configuration:")
        print("-" * 60)
        device = best.get('device', 'unknown')
        
        # For macOS, suggest the device name directly
        if detector.platform == 'Darwin':
            print(f"Interface: {device}")
        else:
            # For Linux, suggest monitor mode name
            print(f"Interface: {device}mon" if not device.endswith('mon') else device)
        
        channel = detector.get_recommended_channel(best)
        print(f"Channel: {channel}")
        print("-" * 60)


if __name__ == '__main__':
    main()
