#!/usr/bin/env python3
"""
WiFi Passive Motion Detection - Main Application
Passive WiFi sensing PoC creating motion heatmap using existing WiFi traffic
"""

import argparse
import json
import logging
import signal
import sys
import time
from pathlib import Path

from wifi_capture import WiFiCapture
from feature_extraction import FeatureExtractor
from spatial_model import SpatialModel
from heatmap_visualizer import HeatmapVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WiFiRadar:
    """Main WiFi Radar application"""
    
    def __init__(self, config_file='config.json'):
        """
        Initialize WiFi Radar
        
        Args:
            config_file: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Initialize components
        self.capture = None
        self.feature_extractor = FeatureExtractor()
        self.spatial_model = None
        self.visualizer = None
        
        # State
        self.running = False
        self.last_update_time = time.time()
        
        # Statistics
        self.stats = {
            'packet_count': 0,
            'max_value': 0.0,
            'mean_value': 0.0,
            'active_cells': 0
        }
    
    def _load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {config_file}")
                return config
            else:
                logger.warning(f"Config file {config_file} not found, using defaults")
                return self._default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._default_config()
    
    def _default_config(self):
        """Return default configuration"""
        return {
            "capture": {
                "interface": "wlan0mon",
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
            }
        }
    
    def initialize(self):
        """Initialize all components"""
        logger.info("Initializing WiFi Radar system...")
        
        # Initialize capture
        capture_config = self.config['capture']
        filter_config = self.config['filtering']
        
        self.capture = WiFiCapture(
            interface=capture_config['interface'],
            channel=capture_config['channel'],
            bssid_filter=filter_config['bssid_filter']
        )
        
        # Initialize spatial model
        spatial_config = self.config['spatial']
        self.spatial_model = SpatialModel(
            grid_size=tuple(spatial_config['grid_size']),
            bin_duration=spatial_config['bin_duration'],
            normalize=spatial_config['normalization']
        )
        
        # Initialize visualizer
        viz_config = self.config['visualization']
        self.visualizer = HeatmapVisualizer(
            grid_size=tuple(spatial_config['grid_size']),
            update_interval=int(viz_config['update_interval'] * 1000),
            colormap=viz_config['colormap'],
            figsize=tuple(viz_config['figsize'])
        )
        
        # Set data callback for visualizer
        self.visualizer.set_data_callback(self._get_visualization_data)
        
        logger.info("Initialization complete")
    
    def _get_visualization_data(self):
        """
        Callback for visualizer to get updated data
        
        Returns:
            Tuple of (grid_data, statistics)
        """
        # Process new packets
        self._process_packets()
        
        # Get current grid
        grid = self.spatial_model.get_grid()
        
        # Return grid and statistics
        return grid, self.stats
    
    def _process_packets(self):
        """Process captured packets and update spatial model"""
        try:
            # Get packets since last update
            packets = self.capture.get_packets(since_timestamp=self.last_update_time)
            self.last_update_time = time.time()
            
            if not packets:
                return
            
            # Extract features
            features = self.feature_extractor.extract_features(packets)
            
            # Calculate disturbance score
            disturbance = self.feature_extractor.extract_disturbance_score(features)
            
            # Update spatial model
            self.spatial_model.update_grid(disturbance)
            
            # Update statistics
            spatial_stats = self.spatial_model.get_statistics()
            self.stats.update(spatial_stats)
            self.stats['packet_count'] = len(packets)
            
        except Exception as e:
            logger.error(f"Error processing packets: {e}")
    
    def start(self):
        """Start the WiFi Radar system"""
        if self.running:
            logger.warning("System already running")
            return
        
        logger.info("Starting WiFi Radar...")
        self.running = True
        
        # Start packet capture
        self.capture.start_capture()
        
        # Small delay to let capture start
        time.sleep(1.0)
        
        # Start visualization (blocking)
        logger.info("Starting visualization (press Ctrl+C to stop)...")
        self.visualizer.start()
    
    def stop(self):
        """Stop the WiFi Radar system"""
        logger.info("Stopping WiFi Radar...")
        self.running = False
        
        # Stop components
        if self.capture:
            self.capture.stop_capture()
        
        if self.visualizer:
            self.visualizer.stop()
        
        logger.info("WiFi Radar stopped")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("Interrupt received, shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='WiFi Passive Motion Detection - PoC System'
    )
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '-i', '--interface',
        help='WiFi interface in monitor mode (overrides config)'
    )
    parser.add_argument(
        '--channel',
        type=int,
        help='WiFi channel to monitor (overrides config)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--auto-config',
        action='store_true',
        help='Auto-detect WiFi interface and generate config.json'
    )
    parser.add_argument(
        '--detect-nic',
        action='store_true',
        help='Run NIC detection and display information'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle NIC detection mode
    if args.detect_nic:
        from nic_detector import NICDetector
        detector = NICDetector()
        print("\nScanning for WiFi interfaces...")
        interfaces = detector.detect_all_interfaces()
        
        if not interfaces:
            print("No WiFi interfaces detected.")
            return
        
        print(f"\nFound {len(interfaces)} WiFi interface(s):\n")
        for i, iface in enumerate(interfaces, 1):
            print(f"\n--- Interface {i} ---")
            detector.print_interface_info(iface)
        
        best = detector.get_best_wifi_interface()
        if best:
            print("\nRecommended Configuration:")
            print("-" * 60)
            print(f"Interface: {best.get('device', 'unknown')}")
            channel = detector.get_recommended_channel(best)
            print(f"Channel: {channel}")
            print("-" * 60)
            print("\nRun with --auto-config to automatically generate config.json")
        return
    
    # Handle auto-configuration mode
    if args.auto_config:
        from auto_config import AutoConfig
        auto_config = AutoConfig()
        print("\nDetecting system configuration...")
        config = auto_config.detect_and_configure()
        auto_config.print_config_summary(config)
        auto_config.save_config(config, filepath=args.config)
        print(f"✓ Configuration saved to {args.config}")
        print("\nYou can now run wifi_radar.py to start the system.")
        return
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create and initialize radar
        radar = WiFiRadar(config_file=args.config)
        radar.initialize()
        
        # Apply command-line overrides before starting
        if args.interface or args.channel:
            logger.info("Applying command-line overrides to configuration")
            if args.interface:
                radar.config['capture']['interface'] = args.interface
                radar.capture.interface = args.interface
                logger.info(f"  Interface: {args.interface}")
            if args.channel:
                radar.config['capture']['channel'] = args.channel
                radar.capture.channel = args.channel
                logger.info(f"  Channel: {args.channel}")
        
        # Start system
        radar.start()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
