# Physical Barcode Scanner Integration Guide

## Overview

This guide explains how to connect and use external physical barcode scanners with the Legal Metrology Compliance Checker system. The integration supports various connection types and popular scanner models.

## Supported Connection Types

### 1. USB Serial (Recommended)
- **Description**: Scanners that communicate via USB-to-Serial interface
- **Common Models**: Most handheld scanners, Honeywell 1450g, Symbol LS2208
- **Pros**: Easy setup, reliable communication, works with most scanners
- **Cons**: Requires correct COM port identification

### 2. USB HID (Human Interface Device)
- **Description**: Scanners that appear as keyboard input devices
- **Common Models**: Zebra DS2208, Datalogic QuickScan
- **Pros**: No drivers needed, plug-and-play
- **Cons**: Limited configuration options

### 3. Bluetooth
- **Description**: Wireless scanners with Bluetooth connectivity
- **Common Models**: Honeywell 1902g, Symbol CS4070
- **Pros**: Wireless operation, mobility
- **Cons**: Battery management, pairing requirements

### 4. Network (TCP/IP)
- **Description**: Fixed-mount scanners with Ethernet connectivity
- **Common Models**: Cognex DataMan series, Keyence SR series
- **Pros**: High-speed, industrial applications
- **Cons**: Network configuration required

## Installation Requirements

### System Dependencies

Install the required Python packages:

```bash
pip install pyserial pyusb
```

### Windows-Specific Setup

1. **USB Serial Drivers**:
   - Most modern scanners use standard USB CDC drivers
   - Some may require manufacturer-specific drivers
   - Check Device Manager for COM port assignment

2. **USB HID Access**:
   - No additional drivers needed
   - Windows automatically recognizes HID devices

3. **Permissions**:
   - Run the application with appropriate permissions
   - Some USB operations may require administrator rights

### Linux-Specific Setup

1. **USB Serial Setup**:
   ```bash
   # Add user to dialout group for serial port access
   sudo usermod -a -G dialout $USER
   
   # Install USB serial drivers (usually included)
   sudo apt-get install linux-modules-extra-$(uname -r)
   ```

2. **USB HID Access**:
   ```bash
   # Install libusb
   sudo apt-get install libusb-1.0-0-dev
   
   # Create udev rule for scanner access (optional)
   sudo nano /etc/udev/rules.d/99-barcode-scanner.rules
   ```

3. **Udev Rule Example** (for specific scanner):
   ```
   SUBSYSTEM=="usb", ATTR{idVendor}=="05e0", ATTR{idProduct}=="1450", MODE="0666"
   ```

### macOS-Specific Setup

1. **Install Dependencies**:
   ```bash
   # Using Homebrew
   brew install libusb
   
   # Install Python packages
   pip install pyserial pyusb
   ```

2. **Permissions**:
   - Grant Terminal or your IDE appropriate permissions in System Preferences
   - USB access may require administrator privileges

## Scanner Configuration

### Step 1: Physical Connection

1. **USB Serial Scanners**:
   - Connect scanner to USB port
   - Note the assigned COM port (Windows) or device path (Linux/macOS)
   - Test with terminal emulator if needed

2. **USB HID Scanners**:
   - Connect scanner to USB port
   - Device should be recognized immediately
   - Note Vendor ID and Product ID from device manager

3. **Bluetooth Scanners**:
   - Put scanner in pairing mode
   - Pair with computer through system Bluetooth settings
   - Note the assigned COM port or device path

### Step 2: Application Configuration

1. **Open Physical Scanner Page**:
   - Navigate to "🔌 Physical Scanner" in the application
   - Go to "⚙️ Configuration" tab

2. **Add New Scanner**:
   - Click "➕ Add New Scanner"
   - Fill in scanner details:
     - **Name**: Descriptive name (e.g., "Honeywell 1450g Main")
     - **Manufacturer**: Scanner manufacturer
     - **Model**: Scanner model number
     - **Connection Type**: Select appropriate type

3. **Connection-Specific Settings**:

   **For USB Serial**:
   - **COM Port**: e.g., COM3 (Windows) or /dev/ttyUSB0 (Linux)
   - **Baud Rate**: Usually 9600 (check scanner manual)
   - **Data Bits**: Usually 8
   - **Stop Bits**: Usually 1
   - **Parity**: Usually None

   **For USB HID**:
   - **Vendor ID**: e.g., 0x05E0 (Honeywell)
   - **Product ID**: e.g., 0x1450 (specific model)

   **For Network**:
   - **IP Address**: Scanner's network IP
   - **TCP Port**: Usually 8080 or manufacturer-specific

4. **Scanner Settings**:
   - **Enable Beep**: Audio feedback on scan
   - **Enable LED**: Visual feedback on scan
   - **Prefix/Suffix**: Data formatting (usually default)

### Step 3: Testing Connection

1. **Connect Scanner**:
   - Click "🔌 Connect" button next to your scanner
   - Wait for status to change to "CONNECTED"
   - Green indicator should appear

2. **Start Scanning**:
   - Click "▶️ Start Scan" button
   - Status should change to "SCANNING"
   - Yellow blinking indicator appears

3. **Test Scan**:
   - Scan a barcode with the physical scanner
   - Result should appear in the "Latest Scan Result" section
   - Audio/visual feedback should occur (if enabled)

## Common Scanner Models Setup

### Honeywell 1450g (USB Serial)

```
Name: Honeywell 1450g
Manufacturer: Honeywell
Model: 1450g
Connection: USB_SERIAL
Port: COM3 (Windows) / /dev/ttyUSB0 (Linux)
Baud Rate: 9600
Beep: Enabled
LED: Enabled
```

### Symbol/Zebra LS2208 (USB Serial)

```
Name: Symbol LS2208
Manufacturer: Symbol Technologies
Model: LS2208
Connection: USB_SERIAL
Port: COM4 (Windows) / /dev/ttyUSB1 (Linux)
Baud Rate: 9600
Beep: Enabled
LED: Enabled
```

### Zebra DS2208 (USB HID)

```
Name: Zebra DS2208
Manufacturer: Zebra Technologies
Model: DS2208
Connection: USB_HID
Vendor ID: 0x05E0
Product ID: 0x1450
Beep: Enabled
LED: Enabled
```

### Honeywell 1902g (Bluetooth)

```
Name: Honeywell 1902g Wireless
Manufacturer: Honeywell
Model: 1902g
Connection: BLUETOOTH
Port: COM5 (assigned after pairing)
Baud Rate: 9600
Beep: Enabled
LED: Enabled
```

## Troubleshooting

### Connection Issues

**Problem**: Scanner not detected
- **Solution**: Check USB connection, try different port
- **Check**: Device Manager (Windows) or lsusb (Linux) for device recognition
- **Verify**: Correct drivers installed

**Problem**: Permission denied errors
- **Solution**: Run application with administrator privileges
- **Linux**: Add user to dialout group: `sudo usermod -a -G dialout $USER`
- **Restart**: Log out and back in for group changes to take effect

**Problem**: COM port not found
- **Solution**: Use Device Manager to identify correct port
- **Check**: Scanner manual for default communication settings
- **Try**: Different baud rates (9600, 19200, 38400)

### Scanning Issues

**Problem**: No scan results received
- **Solution**: Check scanner configuration and trigger mode
- **Verify**: Scanner is in "auto-trigger" or "presentation" mode
- **Test**: Manual trigger by pressing scanner button

**Problem**: Garbled or incomplete data
- **Solution**: Check baud rate and data format settings
- **Adjust**: Prefix/suffix settings to match scanner output
- **Verify**: Scanner is configured for correct data format

**Problem**: Multiple scans of same barcode
- **Solution**: Enable "duplicate timeout" on scanner
- **Configure**: Scanner to prevent rapid duplicate reads
- **Check**: Application logic for duplicate filtering

### Performance Issues

**Problem**: Slow scan response
- **Solution**: Check USB cable quality and length
- **Optimize**: Reduce application polling frequency
- **Consider**: USB 3.0 port for better performance

**Problem**: Scanner disconnects frequently
- **Solution**: Check power management settings
- **Disable**: USB selective suspend in power options
- **Use**: Powered USB hub if needed

## Advanced Configuration

### Custom Scanner Commands

Some scanners support configuration via command strings:

```python
# Example initialization commands (scanner-specific)
init_commands = [
    b'\x16T\r',      # Enable beep
    b'\x16U\r',      # Disable beep
    b'\x16P\r',      # Set prefix
    b'\x16S\r\n\r'   # Set suffix
]
```

### Scanner Programming

Many scanners can be programmed using configuration barcodes:

1. **Enable Configuration Mode**: Scan the "Enter Config" barcode
2. **Set Communication Parameters**: Scan appropriate setup barcodes
3. **Save Settings**: Scan the "Save Config" barcode
4. **Exit Configuration**: Scan the "Exit Config" barcode

Refer to your scanner's manual for specific programming barcodes.

### Integration with Existing Workflow

The physical scanner integrates seamlessly with the existing barcode scanning workflow:

1. **Physical Scan**: Use external scanner for barcode capture
2. **Auto-Lookup**: System automatically looks up product information
3. **Compliance Check**: Automatic legal metrology validation
4. **Report Generation**: Same reporting features as image-based scanning

## API Integration

For advanced users, the physical scanner can be integrated programmatically:

```python
from core.physical_barcode_scanner import get_physical_scanner_manager

# Get scanner manager
manager = get_physical_scanner_manager()

# Connect to scanner
await manager.connect_scanner("USB_SCANNER_001")

# Define scan callback
def handle_scan(result):
    print(f"Scanned: {result.barcode}")

# Start scanning
await manager.start_scanning(handle_scan)
```

## Security Considerations

1. **USB Device Security**:
   - Only connect trusted scanner devices
   - Be aware of USB-based security risks
   - Use endpoint protection if available

2. **Data Handling**:
   - Scanned data is processed locally
   - No external transmission of barcode data
   - Audit logs maintained for compliance

3. **Network Scanners**:
   - Use secure network connections
   - Implement appropriate firewall rules
   - Consider VPN for remote scanners

## Support and Maintenance

### Regular Maintenance

1. **Clean Scanner Window**: Use appropriate cleaning materials
2. **Check Connections**: Ensure USB cables are secure
3. **Update Drivers**: Keep scanner drivers current
4. **Test Functionality**: Regular scanning tests

### Getting Support

1. **Application Issues**: Check application logs for error messages
2. **Scanner Issues**: Consult scanner manufacturer documentation
3. **Driver Problems**: Check manufacturer's website for updates
4. **Integration Help**: Refer to this guide or contact system administrator

## Appendix: Scanner Vendor Information

### Honeywell
- Website: https://www.honeywellaidc.com
- Support: Technical support and driver downloads
- Popular Models: 1450g, 1902g, 1911i

### Zebra Technologies (formerly Symbol)
- Website: https://www.zebra.com
- Support: Comprehensive documentation and drivers
- Popular Models: DS2208, LS2208, CS4070

### Datalogic
- Website: https://www.datalogic.com
- Support: Technical documentation and software
- Popular Models: QuickScan series, Gryphon series

### Cognex
- Website: https://www.cognex.com
- Support: Industrial scanning solutions
- Popular Models: DataMan series

---

This guide provides comprehensive information for setting up and using physical barcode scanners with the Legal Metrology Compliance Checker. For additional support or specific scanner models not covered, please consult the manufacturer's documentation or contact your system administrator.


