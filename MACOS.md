# macOS Setup Guide - WiFi Passive Motion Detection

This guide provides instructions for setting up and running WiFi Radar on macOS, specifically optimized for Macbook M2 with Ventura (13.7.8).

## Prerequisites

- macOS Ventura 13.7.8 or later (tested on M2)
- Python 3.7+
- Built-in WiFi hardware
- Administrator/sudo access

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip3 install -r requirements.txt
```

### 2. Auto-Configure for Your Mac

The easiest way to get started is to use the auto-configuration tool:

```bash
# Detect your WiFi interface and create config.json automatically
sudo python3 wifi_radar.py --auto-config
```

This will:
- Detect your Mac's WiFi interface (typically `en0`)
- Scan for available WiFi channels
- Determine the best channel to monitor
- Generate an optimized `config.json` file
- Backup any existing configuration

### 3. Run WiFi Radar

```bash
# Start the WiFi Radar system
sudo python3 wifi_radar.py
```

## Manual Configuration

### Step 1: Detect Your WiFi Interface

```bash
# Run NIC detection to see your WiFi hardware
python3 wifi_radar.py --detect-nic
```

This will display information about your WiFi interface, including:
- Device name (e.g., `en0`, `en1`)
- Current SSID (if connected)
- Current channel
- Available channels
- Monitor mode support

### Step 2: Configure Manually (if needed)

If you prefer to configure manually, edit `config.json`:

```json
{
    "capture": {
        "interface": "en0",          // Your WiFi interface
        "channel": 6,                 // WiFi channel to monitor
        "frequency_ghz": 2.4,
        "sampling_duration": 0.1
    },
    ...
}
```

### Step 3: Enable Monitor Mode (macOS)

On macOS, monitor mode works differently than on Linux. You have two options:

#### Option A: Using Built-in Airport Utility (Recommended)

macOS includes the `airport` utility that can put your WiFi into monitor mode:

```bash
# Create symlink for easier access (one-time setup)
sudo ln -s /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport /usr/local/bin/airport

# Disconnect from WiFi (required for monitor mode)
sudo airport -z

# Start sniffing on channel 6 (example)
sudo airport en0 sniff 6
```

**Note:** WiFi Radar will automatically handle channel switching when you run it.

#### Option B: Disassociate from Network

If you want to capture packets while monitoring:

```bash
# Disassociate from current network
sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -z

# Run WiFi Radar
sudo python3 wifi_radar.py
```

## macOS-Specific Considerations

### WiFi Interface Names

- **macOS**: WiFi interfaces are typically named `en0`, `en1`, etc.
- **Linux**: WiFi interfaces are typically named `wlan0`, `wlan1`, etc.

The auto-configuration tool automatically detects the correct interface name for your system.

### Monitor Mode Differences

- **macOS**: Uses the built-in `airport` utility for monitor mode and channel control
- **Linux**: Uses `iw` and `iwconfig` commands

WiFi Radar automatically detects your platform and uses the appropriate commands.

### Permissions

Monitor mode packet capture requires root/sudo privileges:

```bash
# Always run with sudo
sudo python3 wifi_radar.py
```

### System Integrity Protection (SIP)

macOS System Integrity Protection may limit some low-level WiFi operations. If you encounter issues:

1. The auto-configuration tool works without disabling SIP
2. Basic packet capture works with standard sudo access
3. Advanced features may require additional permissions

## Command-Line Options

### Auto-Configuration

```bash
# Auto-detect and configure
sudo python3 wifi_radar.py --auto-config

# Auto-detect and save to custom file
sudo python3 wifi_radar.py --auto-config -c my_config.json
```

### NIC Detection

```bash
# Show WiFi interface information
python3 wifi_radar.py --detect-nic
```

### Running WiFi Radar

```bash
# Run with default config
sudo python3 wifi_radar.py

# Run with custom config
sudo python3 wifi_radar.py -c my_config.json

# Override interface
sudo python3 wifi_radar.py -i en0

# Override channel
sudo python3 wifi_radar.py --channel 11

# Verbose logging
sudo python3 wifi_radar.py -v
```

## Standalone Tools

### NIC Detector

Run the NIC detector as a standalone tool:

```bash
python3 nic_detector.py
```

This displays detailed information about all WiFi interfaces on your system.

### Auto-Config Generator

Run the auto-config generator as a standalone tool:

```bash
# Generate and save config
python3 auto_config.py

# Preview without saving
python3 auto_config.py --dry-run

# Save to custom location
python3 auto_config.py -o my_config.json

# Don't backup existing config
python3 auto_config.py --no-backup
```

## Troubleshooting

### "No WiFi interfaces detected"

1. Make sure your Mac has built-in WiFi (not USB adapter)
2. Check WiFi is enabled in System Settings
3. Run with verbose logging: `python3 wifi_radar.py --detect-nic -v`

### "Permission denied"

- Always run with `sudo` for packet capture:
  ```bash
  sudo python3 wifi_radar.py
  ```

### "Failed to set channel"

1. Make sure WiFi is disconnected from any network
2. Try disconnecting manually:
   ```bash
   sudo airport -z
   ```
3. Check if another application is using WiFi

### "No packets captured"

1. Verify you're on a channel with WiFi traffic:
   ```bash
   python3 wifi_radar.py --detect-nic
   ```
2. Try different channels with more activity
3. Remove BSSID filter in config.json (set to empty array `[]`)
4. Make sure you're running with sudo

### WiFi Connection Required

If you need to stay connected to WiFi:

1. Use a second WiFi adapter (USB) for monitoring
2. Use your built-in WiFi for internet, USB WiFi for monitoring
3. Configure WiFi Radar to use the USB adapter

## Performance on M2 Macs

The M2 processor provides excellent performance for WiFi Radar:

- **Packet Processing**: M2's efficiency cores handle packet capture with minimal CPU usage
- **Visualization**: Fast rendering of the live heatmap
- **Low Latency**: Responsive real-time motion detection

Recommended settings for M2:
- Grid size: `[10, 10]` or higher (e.g., `[15, 15]`)
- Update interval: `0.3` seconds for smooth visualization
- All features enabled (RSSI, phase, FFT)

## Channel Recommendations for macOS

The auto-configuration tool scans for active channels. Typical 2.4GHz channels:

- **Channels 1, 6, 11**: Most common, least overlap
- **Channels 2-5, 7-10**: May have overlap but more traffic

For best results:
1. Use auto-configuration to detect busy channels
2. Monitor channels with active WiFi traffic
3. Try multiple channels to find best performance

## Example Session

```bash
# Step 1: Detect your WiFi setup
python3 wifi_radar.py --detect-nic

# Output:
# Found 1 WiFi interface(s):
# 
# --- Interface 1 ---
# Device: en0
# Name: Wi-Fi
# Current Channel: 6
# Available Channels: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
# Monitor Mode Support: Yes

# Step 2: Auto-configure
sudo python3 wifi_radar.py --auto-config

# Output:
# ✓ Configuration saved to config.json

# Step 3: Disconnect from WiFi (important!)
sudo airport -z

# Step 4: Run WiFi Radar
sudo python3 wifi_radar.py

# The heatmap window will open showing motion detection!
```

## Advanced Usage

### Custom BSSID Filtering (macOS)

To monitor specific access points:

1. Scan for networks:
   ```bash
   airport -s
   ```

2. Note the BSSID (MAC address) of access points

3. Add to config.json:
   ```json
   {
       "filtering": {
           "bssid_filter": [
               "aa:bb:cc:dd:ee:ff",
               "11:22:33:44:55:66"
           ]
       }
   }
   ```

### Multiple WiFi Adapters

If you have multiple WiFi interfaces:

```bash
# List all interfaces
python3 wifi_radar.py --detect-nic

# Use specific interface
sudo python3 wifi_radar.py -i en1
```

## Differences from Linux

| Feature | macOS | Linux |
|---------|-------|-------|
| Interface Name | `en0`, `en1` | `wlan0`, `wlan1` |
| Monitor Mode | `airport` utility | `iw`, `iwconfig` |
| Channel Setting | `airport -c` | `iwconfig channel` |
| Root Required | Yes (`sudo`) | Yes (`sudo`) |
| Auto-Config | ✓ Supported | ✓ Supported |

## Resources

- **Airport Utility**: `/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport`
- **System Info**: `system_profiler SPNetworkDataType`
- **WiFi Diagnostics**: Hold Option key, click WiFi icon in menu bar

## Getting Help

If you encounter issues:

1. Run with verbose logging:
   ```bash
   sudo python3 wifi_radar.py -v
   ```

2. Check the auto-detected configuration:
   ```bash
   python3 wifi_radar.py --detect-nic
   ```

3. Test with demo mode (no WiFi hardware required):
   ```bash
   python3 demo.py
   ```

## Notes

- **M2 Optimization**: This version is optimized for M2 Macs running Ventura
- **Auto-Detection**: The system automatically detects your WiFi hardware
- **Platform-Aware**: Code detects macOS vs Linux and adapts accordingly
- **Backwards Compatible**: Still works on Intel Macs and Linux systems
