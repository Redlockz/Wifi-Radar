# WiFi Passive Motion Detection System

A Proof of Concept (PoC) system for passive WiFi sensing that creates a motion heatmap using existing WiFi traffic only (no active radar).

## Overview

This system leverages ambient WiFi traffic to detect motion and visualize it as a live 2D heatmap. It works by analyzing changes in WiFi signal characteristics (RSSI, phase, frequency patterns) caused by movement in the environment.

## Features

- **Passive Detection**: Uses only existing WiFi traffic, no active transmission required
- **BSSID Filtering**: Configurable filtering to focus on specific access points
- **Real-time Visualization**: Live matplotlib heatmap showing motion activity
- **Multi-feature Analysis**: 
  - RSSI mean and variance
  - Phase variance and delta
  - FFT energy changes
  - Temporal pattern analysis
- **Spatial Grid Model**: 2D grid with normalized disturbance scores
- **Configurable**: JSON-based configuration for all parameters

## Architecture

### Components

1. **WiFi Capture** (`wifi_capture.py`)
   - Continuous 2.4GHz packet sampling
   - BSSID filtering
   - RSSI and phase extraction

2. **Feature Extraction** (`feature_extraction.py`)
   - RSSI statistics (mean, variance)
   - Phase variance and temporal delta
   - FFT energy calculation
   - Disturbance score computation

3. **Spatial Model** (`spatial_model.py`)
   - 2D grid representation
   - Time-binned accumulation
   - Normalized disturbance distribution
   - Temporal decay

4. **Heatmap Visualizer** (`heatmap_visualizer.py`)
   - Live matplotlib animation
   - Real-time statistics display
   - Configurable update rate and colormap

5. **Main Application** (`wifi_radar.py`)
   - Orchestrates all components
   - Configuration management
   - Command-line interface

## Requirements

### System Requirements

- Linux-based system (tested on Ubuntu/Debian)
- WiFi adapter supporting monitor mode
- Python 3.7+
- Root/sudo access (for monitor mode configuration)

### Python Dependencies

```bash
pip install -r requirements.txt
```

Dependencies include:
- scapy >= 2.5.0 (packet capture)
- numpy >= 1.21.0 (numerical operations)
- matplotlib >= 3.5.0 (visualization)
- scipy >= 1.7.0 (signal processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Redlockz/Wifi-Radar.git
cd Wifi-Radar
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your WiFi interface for monitor mode:
```bash
# Stop network manager (if running)
sudo systemctl stop NetworkManager

# Set interface to monitor mode
sudo ip link set wlan0 down
sudo iw wlan0 set monitor control
sudo ip link set wlan0 up

# Rename to standard monitor name (optional)
sudo ip link set wlan0 name wlan0mon
```

## Configuration

Edit `config.json` to customize system parameters:

```json
{
    "capture": {
        "interface": "wlan0mon",      // Monitor mode interface
        "channel": 6,                  // WiFi channel (1-11 for 2.4GHz)
        "frequency_ghz": 2.4,
        "sampling_duration": 0.1
    },
    "filtering": {
        "bssid_filter": [],            // List of BSSIDs to monitor (empty = all)
        "packet_types": ["Beacon", "Data"]
    },
    "features": {
        "rssi_enabled": true,
        "phase_enabled": true,
        "fft_enabled": true
    },
    "spatial": {
        "grid_size": [10, 10],         // Heatmap grid dimensions
        "bin_mode": "time",
        "bin_duration": 1.0,           // Time window in seconds
        "normalization": true
    },
    "visualization": {
        "update_interval": 0.5,        // Update rate in seconds
        "colormap": "hot",             // Matplotlib colormap
        "figsize": [10, 8]
    }
}
```

## Usage

### Basic Usage

Run with default configuration:
```bash
sudo python3 wifi_radar.py
```

### Command-Line Options

```bash
sudo python3 wifi_radar.py [OPTIONS]

Options:
  -c, --config CONFIG    Path to configuration file (default: config.json)
  -i, --interface IFACE  WiFi interface in monitor mode (overrides config)
  --channel CHANNEL      WiFi channel to monitor (overrides config)
  -v, --verbose         Enable verbose logging
```

### Examples

Monitor on specific channel:
```bash
sudo python3 wifi_radar.py --channel 11
```

Use custom configuration:
```bash
sudo python3 wifi_radar.py -c my_config.json
```

Verbose output:
```bash
sudo python3 wifi_radar.py -v
```

### BSSID Filtering

To monitor specific access points, add their BSSIDs to the config:

```json
{
    "filtering": {
        "bssid_filter": [
            "AA:BB:CC:DD:EE:FF",
            "11:22:33:44:55:66"
        ]
    }
}
```

## How It Works

### Detection Principle

The system exploits the fact that human movement causes changes in WiFi signal propagation:

1. **Multipath Effects**: Movement changes the reflection patterns
2. **RSSI Fluctuations**: Signal strength varies as paths change
3. **Phase Shifts**: Carrier phase is affected by path length changes
4. **Temporal Patterns**: Movement creates characteristic time-domain signatures

### Processing Pipeline

1. **Capture**: Continuously sniff WiFi packets on 2.4GHz
2. **Filter**: Apply BSSID filter to focus on relevant traffic
3. **Extract**: Calculate RSSI, phase, and temporal features
4. **Analyze**: Compute disturbance scores from feature changes
5. **Map**: Distribute scores across 2D spatial grid
6. **Visualize**: Update live heatmap showing motion activity

### Feature Calculation

- **RSSI Mean**: Average signal strength
- **RSSI Variance**: Signal strength fluctuation (high = activity)
- **Phase Variance**: Phase distribution spread
- **Phase Delta**: Phase change over time
- **FFT Energy**: Frequency-domain energy content

### Disturbance Score

Weighted combination of features:
- RSSI variance: 30%
- Phase variance: 20%
- FFT energy: 30%
- Phase delta: 20%

Normalized to 0-1 range for heatmap display.

## Limitations

This is a Proof of Concept with several limitations:

1. **Spatial Resolution**: Current PoC uses simulated spatial distribution. Real implementation would require multiple synchronized receivers for true spatial mapping.

2. **Requires WiFi Traffic**: Detection only works when ambient WiFi packets are being transmitted.

3. **Monitor Mode**: Requires WiFi adapter supporting monitor mode and root privileges.

4. **Environmental Factors**: Metal objects, walls, and other environmental factors affect accuracy.

5. **No Ground Truth**: The system shows relative motion activity but doesn't provide absolute position or velocity.

## Troubleshooting

### No packets captured
- Verify interface is in monitor mode: `iwconfig wlan0mon`
- Check channel is set correctly: `iwconfig wlan0mon channel`
- Ensure there's WiFi traffic on the selected channel
- Try different channels or remove BSSID filter

### Permission denied
- Run with sudo/root privileges
- Check interface permissions

### Poor detection
- Adjust bin_duration (longer = more stable, shorter = more responsive)
- Try different channels with more traffic
- Remove or adjust BSSID filter
- Increase grid_size for finer spatial resolution

### Visualization not updating
- Check update_interval isn't too short
- Verify packets are being captured (use -v flag)
- Ensure matplotlib backend is properly configured

## Future Enhancements

- Multi-receiver spatial triangulation
- Machine learning for motion classification
- Tracking of multiple targets
- Historical playback and analysis
- Web-based dashboard
- Integration with MQTT/home automation

## References

- WiFi-based passive radar and motion sensing
- OFDM signal characteristics
- CSI (Channel State Information) analysis
- Passive human detection using ambient signals

## License

This is a proof-of-concept research project. Use responsibly and in compliance with local regulations regarding WiFi monitoring.

## Author

Redlockz

## Contributing

This is a PoC project. Feel free to fork and experiment!
