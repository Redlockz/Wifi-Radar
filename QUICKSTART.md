# Quick Start Guide - WiFi Passive Motion Detection

**Now with Auto-Configuration for macOS and Linux!**

## Prerequisites
- **macOS** (M2 recommended) or **Linux** with WiFi adapter supporting monitor mode
- Python 3.7+
- Root/sudo access

## Quick Start (Recommended)

### Auto-Configuration Method

```bash
# 1. Clone repository
git clone https://github.com/Redlockz/Wifi-Radar.git
cd Wifi-Radar

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Auto-detect and configure your WiFi interface
sudo python3 wifi_radar.py --auto-config

# 4. Run WiFi Radar
sudo python3 wifi_radar.py
```

That's it! The auto-configuration will detect your WiFi interface and optimal settings.

## Platform-Specific Notes

### macOS (M2 Ventura)

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Auto-configure for your Mac
sudo python3 wifi_radar.py --auto-config

# 3. Disconnect from WiFi (required for monitor mode)
sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -z

# 4. Run WiFi Radar
sudo python3 wifi_radar.py
```

See [MACOS.md](MACOS.md) for detailed macOS instructions.

### Linux

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Auto-configure
sudo python3 wifi_radar.py --auto-config

# 3. Setup WiFi adapter in monitor mode (if needed)
sudo systemctl stop NetworkManager
sudo ip link set wlan0 down
sudo iw wlan0 set monitor control
sudo ip link set wlan0 up
sudo ip link set wlan0 name wlan0mon

# 4. Run WiFi Radar
sudo python3 wifi_radar.py
```

## NIC Detection and Reconnaissance

Before configuring, you can scan your WiFi interfaces:

```bash
# Display WiFi interface information
python3 wifi_radar.py --detect-nic
```

This shows:
- Available WiFi interfaces
- Current channel and network
- Available channels
- Recommended configuration

## Manual Installation (Advanced)

```bash
# 1. Clone repository
git clone https://github.com/Redlockz/Wifi-Radar.git
cd Wifi-Radar

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup WiFi adapter in monitor mode
sudo systemctl stop NetworkManager
sudo ip link set wlan0 down
sudo iw wlan0 set monitor control
sudo ip link set wlan0 up
sudo ip link set wlan0 name wlan0mon
```

## Quick Test (No WiFi Hardware Required)

```bash
# Run demo with simulated data
python3 demo.py
```

## Basic Usage

```bash
# Run with auto-configured settings
sudo python3 wifi_radar.py

# Detect your WiFi interface first
python3 wifi_radar.py --detect-nic

# Auto-configure
sudo python3 wifi_radar.py --auto-config

# Specify channel
sudo python3 wifi_radar.py --channel 11

# Specify interface
sudo python3 wifi_radar.py -i wlan1mon  # Linux
sudo python3 wifi_radar.py -i en0       # macOS

# Enable verbose logging
sudo python3 wifi_radar.py -v
```

## Configuration

### Auto-Configuration (Recommended)

```bash
sudo python3 wifi_radar.py --auto-config
```

### Manual Configuration

Edit `config.json` to customize:
- WiFi channel (1-11 for 2.4GHz)
- Grid size (e.g., [15, 15] for higher resolution)
- Update interval (seconds)
- BSSID filter (specific access points)
- Visualization colormap

## Expected Behavior

When running:
1. System starts capturing WiFi packets
2. Live heatmap window opens
3. Heatmap shows motion activity in real-time:
   - **Yellow/White**: High disturbance (motion detected)
   - **Red/Orange**: Moderate activity
   - **Dark**: Low/no activity
4. Statistics shown in corner (Max, Mean, Active Cells, Packets)

## Troubleshooting

**"No packets captured"**
- Verify monitor mode: `iwconfig wlan0mon`
- Try different channels with more traffic
- Remove BSSID filter in config.json

**"Permission denied"**
- Run with sudo: `sudo python3 wifi_radar.py`

**"Poor detection sensitivity"**
- Increase bin_duration in config.json (e.g., 2.0)
- Try channels with more active WiFi traffic
- Remove BSSID filter to capture all traffic

## Key Files

- `wifi_radar.py` - Main application
- `config.json` - Configuration file
- `demo.py` - Test without WiFi hardware
- `README.md` - Full documentation

## Architecture

```
WiFi Packets → Capture → Feature Extraction → Spatial Model → Heatmap
              (BSSID)   (RSSI/Phase/FFT)    (2D Grid)      (Live View)
```

## Features Detected

- **RSSI variance**: Signal strength fluctuation
- **Phase variance**: Multipath changes
- **FFT energy**: Frequency-domain patterns
- **Phase delta**: Temporal phase shifts

All combined into normalized disturbance score (0-1).

## Limitations (PoC)

- Spatial distribution is simulated (no true localization)
- Requires ambient WiFi traffic to function
- Needs WiFi adapter with monitor mode support
- Environmental factors affect accuracy

## Next Steps

1. Test with real WiFi hardware in monitor mode
2. Experiment with different channels/BSSIDs
3. Adjust sensitivity via config parameters
4. Try different visualization colormaps

For full documentation, see README.md
