"""
WiFi Packet Capture Module
Handles 2.4GHz continuous sampling with BSSID filtering
"""

import logging
from scapy.all import sniff, Dot11, RadioTap
from collections import deque
import threading
import time

logger = logging.getLogger(__name__)


class WiFiCapture:
    """Captures WiFi packets from ambient traffic with BSSID filtering"""
    
    def __init__(self, interface, channel=6, bssid_filter=None):
        """
        Initialize WiFi capture
        
        Args:
            interface: Network interface in monitor mode (e.g., 'wlan0mon')
            channel: WiFi channel to monitor (default: 6 for 2.4GHz)
            bssid_filter: List of BSSIDs to filter (None = all packets)
        """
        self.interface = interface
        self.channel = channel
        self.bssid_filter = set(bssid_filter) if bssid_filter else None
        self.packets = deque(maxlen=10000)  # Store recent packets
        self.running = False
        self.capture_thread = None
        
    def set_channel(self, channel):
        """Set WiFi channel for monitoring"""
        try:
            import os
            os.system(f"iwconfig {self.interface} channel {channel}")
            logger.info(f"Set {self.interface} to channel {channel}")
        except Exception as e:
            logger.error(f"Failed to set channel: {e}")
    
    def packet_handler(self, packet):
        """Process captured packets"""
        try:
            # Check if packet has required layers
            if not packet.haslayer(Dot11):
                return
            
            dot11 = packet[Dot11]
            
            # Apply BSSID filter if configured
            if self.bssid_filter:
                bssid = dot11.addr2  # Transmitter address
                if bssid not in self.bssid_filter:
                    return
            
            # Extract RSSI if available (from RadioTap)
            rssi = None
            phase = None
            if packet.haslayer(RadioTap):
                radiotap = packet[RadioTap]
                # RSSI is typically in dBm_AntSignal field
                if hasattr(radiotap, 'dBm_AntSignal'):
                    rssi = radiotap.dBm_AntSignal
                # Phase information (if available)
                if hasattr(radiotap, 'ChannelFlags'):
                    phase = radiotap.ChannelFlags
            
            # Store packet information
            packet_info = {
                'timestamp': time.time(),
                'bssid': dot11.addr2,
                'rssi': rssi,
                'phase': phase,
                'type': dot11.type,
                'subtype': dot11.subtype,
                'packet': packet
            }
            
            self.packets.append(packet_info)
            
        except Exception as e:
            logger.debug(f"Error processing packet: {e}")
    
    def start_capture(self):
        """Start capturing packets in background thread"""
        if self.running:
            logger.warning("Capture already running")
            return
        
        self.running = True
        self.set_channel(self.channel)
        
        def capture_loop():
            logger.info(f"Starting packet capture on {self.interface}")
            try:
                sniff(
                    iface=self.interface,
                    prn=self.packet_handler,
                    store=0,
                    stop_filter=lambda x: not self.running
                )
            except Exception as e:
                logger.error(f"Capture error: {e}")
                self.running = False
        
        self.capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info("Capture thread started")
    
    def stop_capture(self):
        """Stop packet capture"""
        logger.info("Stopping capture")
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
    
    def get_packets(self, since_timestamp=None):
        """
        Get captured packets
        
        Args:
            since_timestamp: Only return packets after this timestamp
            
        Returns:
            List of packet information dictionaries
        """
        if since_timestamp is None:
            return list(self.packets)
        else:
            return [p for p in self.packets if p['timestamp'] > since_timestamp]
    
    def clear_packets(self):
        """Clear packet buffer"""
        self.packets.clear()
