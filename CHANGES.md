# macOS M2 Optimization - Change Summary

## Overview
This update optimizes WiFi Radar for macOS M2 Macs running Ventura 13.7.8, while maintaining full backwards compatibility with Linux systems. The key improvement is automatic WiFi interface detection and configuration.

## New Features

### 1. NIC Detection and Reconnaissance (`nic_detector.py`)
A new standalone module that automatically detects and analyzes WiFi interfaces.

**Features:**
- Platform-aware detection (macOS and Linux)
- Automatic WiFi interface discovery
- Channel scanning and detection
- Hardware capability analysis
- Detailed interface information display

**Platform-Specific Implementation:**
- **macOS**: Uses `networksetup` and `airport` utilities
- **Linux**: Uses `iw` command

**Usage:**
```bash
# Standalone
python3 nic_detector.py

# Via main application
python3 wifi_radar.py --detect-nic
```

### 2. Auto-Configuration (`auto_config.py`)
Automatically generates optimized configuration based on detected hardware.

**Features:**
- Automatic WiFi interface detection
- Smart channel selection
- Platform-specific defaults
- Configuration backup
- Dry-run mode for preview

**Generated Config Includes:**
- Detected WiFi interface name
- Recommended channel
- Available channels list
- Platform information
- Detection timestamp

**Usage:**
```bash
# Standalone
python3 auto_config.py
python3 auto_config.py --dry-run
python3 auto_config.py -o custom_config.json

# Via main application
sudo python3 wifi_radar.py --auto-config
```

### 3. Enhanced Main Application (`wifi_radar.py`)
Two new command-line options integrated into the main application.

**New Options:**
- `--detect-nic`: Run NIC detection and display information
- `--auto-config`: Auto-detect and generate config.json

**Example Workflow:**
```bash
# Step 1: Detect hardware
python3 wifi_radar.py --detect-nic

# Step 2: Auto-configure
sudo python3 wifi_radar.py --auto-config

# Step 3: Run
sudo python3 wifi_radar.py
```

### 4. macOS WiFi Control (`wifi_capture.py`)
Updated channel control to support both macOS and Linux.

**Changes:**
- Platform detection in `set_channel()` method
- Uses `airport` utility on macOS
- Uses `iwconfig` on Linux
- Graceful fallback on errors

## Platform-Specific Support

### macOS (M2 Ventura 13.7.8+)
- Interface naming: `en0`, `en1`, etc.
- Monitor mode: Via `airport` utility
- Channel control: `airport -c <channel>`
- Detection: `networksetup` and `airport` commands

**macOS-Specific Features:**
- Automatic detection of built-in WiFi
- Current SSID detection
- Active channel scanning
- Network service enumeration

### Linux
- Interface naming: `wlan0`, `wlan1`, etc.
- Monitor mode: Via `iw` and `iwconfig`
- Channel control: `iwconfig channel <channel>`
- Detection: `iw dev` command

**Linux-Specific Features:**
- Physical layer enumeration
- Interface type detection
- Comprehensive channel list

## Documentation Updates

### New Documentation
1. **MACOS.md** - Comprehensive macOS setup guide
   - Quick start instructions
   - Platform-specific considerations
   - Troubleshooting guide
   - Performance recommendations for M2
   - Advanced usage examples

### Updated Documentation
1. **README.md**
   - Added macOS support section
   - Updated quick start with auto-config
   - Cross-platform installation instructions
   - New features highlighted

2. **QUICKSTART.md**
   - Auto-configuration quick start
   - Platform-specific notes
   - NIC detection instructions
   - Updated command examples

3. **.gitignore**
   - Added `*.backup` for config backups

## Technical Details

### Platform Detection
```python
import platform
system = platform.system()  # Returns 'Darwin' for macOS, 'Linux' for Linux
```

### macOS WiFi Utilities
- **Airport**: `/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport`
  - `-I`: Get current WiFi info
  - `-s`: Scan for networks
  - `-c <channel>`: Set channel
  - `-z`: Disassociate from network

- **networksetup**: System utility for network configuration
  - `-listallhardwareports`: List all network interfaces

### Auto-Detection Logic
1. Detect operating system
2. Scan for WiFi interfaces using platform-specific tools
3. Extract current channel and available channels
4. Determine best interface (not in monitor mode)
5. Select optimal channel (current if available, else 6, else first available)
6. Generate platform-appropriate config

### Configuration Format
```json
{
    "capture": {
        "interface": "en0",  // Auto-detected
        "channel": 6,        // Auto-selected
        ...
    },
    "_auto_detected": {
        "platform": "Darwin",
        "device": "en0",
        "available_channels": [1, 2, 3, ...],
        "detected_at": "2026-02-13T..."
    }
}
```

## Backwards Compatibility

### Linux Systems
- All existing functionality preserved
- Auto-detection adds new capabilities
- Manual configuration still supported
- No breaking changes

### Existing Configs
- Auto-config backs up existing config.json
- Manual configs can still be used with `-c` option
- Command-line overrides still work

## Testing

### Tested Scenarios
✅ Auto-detection on Linux (without WiFi hardware)
✅ Auto-config generation with defaults
✅ Config backup functionality
✅ Standalone script execution
✅ Integrated command-line options
✅ Help text generation
✅ Module imports and basic functionality

### Not Tested (Due to Environment Limitations)
⚠️ Actual macOS WiFi interface detection
⚠️ Airport utility integration
⚠️ Monitor mode on macOS
⚠️ Real WiFi packet capture

**Note**: The code is designed for macOS based on Apple's documented utilities and standard practices, but will require testing on actual macOS hardware.

## Usage Examples

### Quick Start (macOS)
```bash
# Install
pip3 install -r requirements.txt

# Auto-configure
sudo python3 wifi_radar.py --auto-config

# Run
sudo python3 wifi_radar.py
```

### Quick Start (Linux)
```bash
# Install
pip install -r requirements.txt

# Auto-configure
sudo python3 wifi_radar.py --auto-config

# Setup monitor mode (if needed)
sudo ip link set wlan0 down
sudo iw wlan0 set monitor control
sudo ip link set wlan0 up

# Run
sudo python3 wifi_radar.py
```

### Advanced Usage
```bash
# Detect interfaces
python3 wifi_radar.py --detect-nic

# Preview config without saving
python3 auto_config.py --dry-run

# Save to custom location
python3 auto_config.py -o /path/to/config.json

# Override auto-detected settings
sudo python3 wifi_radar.py -i en1 --channel 11
```

## Benefits

### For Users
- **Simplified Setup**: No need to manually find interface names
- **Platform Agnostic**: Works on both macOS and Linux
- **Smart Defaults**: Automatically selects optimal settings
- **Less Errors**: Reduces configuration mistakes
- **Easy Discovery**: Can explore capabilities before running

### For Developers
- **Modular Design**: NIC detection and config generation are separate modules
- **Reusable Components**: Can be used independently or integrated
- **Well Documented**: Comprehensive inline documentation
- **Error Handling**: Graceful fallbacks and error messages

## Security Considerations
✅ No hardcoded credentials
✅ No remote code execution
✅ Minimal system calls (only for network detection)
✅ Safe file operations (backup before overwrite)
✅ Subprocess calls use check=False to prevent exceptions
✅ Input validation on file paths

**CodeQL Scan**: 0 security alerts

## Future Enhancements
- [ ] Support for 5GHz channels
- [ ] USB WiFi adapter detection
- [ ] More detailed capability detection (802.11ac, 802.11ax)
- [ ] Integration with system WiFi preferences
- [ ] Automatic channel quality assessment
- [ ] GUI for configuration

## Files Changed/Added

### New Files
- `nic_detector.py` (355 lines)
- `auto_config.py` (253 lines)
- `MACOS.md` (328 lines)

### Modified Files
- `wifi_radar.py` (+72 lines)
- `wifi_capture.py` (+15 lines)
- `README.md` (+150 lines, restructured)
- `QUICKSTART.md` (+100 lines, restructured)
- `.gitignore` (+3 lines)

### Total Changes
- **Lines Added**: ~1,276
- **Lines Modified**: ~187
- **New Features**: 3 major features
- **Documentation Pages**: 1 new, 3 updated
