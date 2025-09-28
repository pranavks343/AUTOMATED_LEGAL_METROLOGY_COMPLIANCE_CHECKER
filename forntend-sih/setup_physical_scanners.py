#!/usr/bin/env python3
"""
Physical Barcode Scanner Setup Script
Helps detect and configure physical barcode scanners for the Legal Metrology Checker
"""

import sys
import subprocess
import platform
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3.7, 0):
        print("❌ Error: Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def install_dependencies():
    """Install required dependencies for physical scanner support"""
    print("\n📦 Installing physical scanner dependencies...")
    
    dependencies = [
        "pyserial>=3.5",
        "pyusb>=1.2.1"
    ]
    
    try:
        for dep in dependencies:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def detect_serial_ports():
    """Detect available serial ports"""
    print("\n🔍 Detecting serial ports...")
    
    try:
        import serial.tools.list_ports
        
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            print("⚠️  No serial ports found")
            return []
        
        detected_ports = []
        
        for port in ports:
            port_info = {
                'device': port.device,
                'description': port.description,
                'vid': port.vid,
                'pid': port.pid,
                'is_scanner': False
            }
            
            # Check if port might be a scanner
            if port.description and any(keyword in port.description.lower() 
                                     for keyword in ['scanner', 'barcode', 'symbol', 'honeywell', 'zebra']):
                port_info['is_scanner'] = True
                print(f"📷 Potential scanner found: {port.device} - {port.description}")
            else:
                print(f"🔌 Serial port: {port.device} - {port.description}")
            
            detected_ports.append(port_info)
        
        return detected_ports
        
    except ImportError:
        print("❌ pyserial not available - run with --install-deps first")
        return []
    except Exception as e:
        print(f"❌ Error detecting serial ports: {e}")
        return []

def detect_usb_devices():
    """Detect USB HID devices that might be scanners"""
    print("\n🔍 Detecting USB devices...")
    
    try:
        import usb.core
        import usb.util
        
        # Common scanner vendor IDs
        scanner_vids = {
            0x05E0: "Symbol/Zebra",
            0x0C2E: "Honeywell", 
            0x1504: "Microscan",
            0x04B4: "Cypress (various scanners)",
            0x0536: "Hand Held Products (Honeywell)",
            0x1659: "Prolific (various adapters)"
        }
        
        detected_devices = []
        
        for vid, manufacturer in scanner_vids.items():
            devices = usb.core.find(find_all=True, idVendor=vid)
            
            for device in devices:
                # Check if it's an HID device
                for cfg in device:
                    for intf in cfg:
                        if intf.bInterfaceClass == 3:  # HID class
                            try:
                                product_name = usb.util.get_string(device, device.iProduct) if device.iProduct else 'Unknown'
                                
                                device_info = {
                                    'vid': device.idVendor,
                                    'pid': device.idProduct,
                                    'manufacturer': manufacturer,
                                    'product': product_name,
                                    'is_hid': True
                                }
                                
                                print(f"📷 USB HID Scanner found: {manufacturer} - {product_name} (VID:0x{device.idVendor:04X} PID:0x{device.idProduct:04X})")
                                detected_devices.append(device_info)
                                break
                            except:
                                # Some devices may not allow string access
                                device_info = {
                                    'vid': device.idVendor,
                                    'pid': device.idProduct,
                                    'manufacturer': manufacturer,
                                    'product': 'Unknown',
                                    'is_hid': True
                                }
                                
                                print(f"📷 USB HID Scanner found: {manufacturer} (VID:0x{device.idVendor:04X} PID:0x{device.idProduct:04X})")
                                detected_devices.append(device_info)
                                break
        
        if not detected_devices:
            print("⚠️  No USB HID scanners found")
        
        return detected_devices
        
    except ImportError:
        print("❌ pyusb not available - run with --install-deps first")
        return []
    except Exception as e:
        print(f"❌ Error detecting USB devices: {e}")
        return []

def create_scanner_config(detected_ports, detected_usb):
    """Create default scanner configurations based on detected devices"""
    print("\n⚙️  Creating scanner configurations...")
    
    config_file = Path("app/data/physical_scanners.json")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    scanners = []
    scanner_id = 1
    
    # Create configs for detected serial scanners
    for port in detected_ports:
        if port['is_scanner']:
            scanner_config = {
                "scanner_id": f"USB_SCANNER_{scanner_id:03d}",
                "name": f"Scanner on {port['device']}",
                "manufacturer": "Auto-detected",
                "model": port['description'],
                "connection_type": "USB_SERIAL",
                "port": port['device'],
                "baud_rate": 9600,
                "data_bits": 8,
                "stop_bits": 1,
                "parity": "N",
                "timeout": 1.0,
                "beep_enabled": True,
                "led_enabled": True,
                "prefix": "",
                "suffix": "\r\n",
                "supported_formats": [
                    "Code128", "Code39", "EAN-13", "EAN-8", 
                    "UPC-A", "UPC-E", "QR", "DataMatrix"
                ]
            }
            scanners.append(scanner_config)
            scanner_id += 1
    
    # Create configs for detected USB HID scanners
    for device in detected_usb:
        scanner_config = {
            "scanner_id": f"HID_SCANNER_{scanner_id:03d}",
            "name": f"{device['manufacturer']} {device['product']}",
            "manufacturer": device['manufacturer'],
            "model": device['product'],
            "connection_type": "USB_HID",
            "vendor_id": device['vid'],
            "product_id": device['pid'],
            "beep_enabled": True,
            "led_enabled": True,
            "supported_formats": [
                "Code128", "Code39", "EAN-13", "EAN-8", 
                "UPC-A", "UPC-E", "QR", "DataMatrix"
            ]
        }
        scanners.append(scanner_config)
        scanner_id += 1
    
    # Save configuration
    config_data = {"scanners": scanners}
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ Created configuration file: {config_file}")
        print(f"📷 Configured {len(scanners)} scanner(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating configuration: {e}")
        return False

def check_permissions():
    """Check system permissions for scanner access"""
    print("\n🔐 Checking system permissions...")
    
    system = platform.system()
    
    if system == "Linux":
        import os
        import grp
        
        try:
            # Check if user is in dialout group
            user_groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
            
            if 'dialout' in user_groups:
                print("✅ User is in dialout group - Serial port access OK")
            else:
                print("⚠️  User not in dialout group - Serial port access may be limited")
                print("   Run: sudo usermod -a -G dialout $USER")
                print("   Then log out and back in")
        
        except Exception as e:
            print(f"⚠️  Could not check group membership: {e}")
    
    elif system == "Windows":
        print("ℹ️  Windows detected - USB access should work automatically")
        print("   If you encounter permission issues, try running as administrator")
    
    elif system == "Darwin":  # macOS
        print("ℹ️  macOS detected - USB access should work automatically")
        print("   Grant appropriate permissions when prompted")
    
    else:
        print(f"⚠️  Unknown system: {system}")

def run_system_test():
    """Run basic system tests"""
    print("\n🧪 Running system tests...")
    
    # Test serial port access
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        print(f"✅ Serial port detection: Found {len(ports)} port(s)")
    except Exception as e:
        print(f"❌ Serial port detection failed: {e}")
    
    # Test USB access
    try:
        import usb.core
        devices = list(usb.core.find(find_all=True))
        print(f"✅ USB device detection: Found {len(devices)} device(s)")
    except Exception as e:
        print(f"❌ USB device detection failed: {e}")
    
    # Test configuration directory
    try:
        config_dir = Path("app/data")
        config_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Configuration directory: OK")
    except Exception as e:
        print(f"❌ Configuration directory failed: {e}")

def main():
    """Main setup function"""
    print("🔌 Physical Barcode Scanner Setup")
    print("=" * 40)
    
    # Parse command line arguments
    install_deps = "--install-deps" in sys.argv
    auto_config = "--auto-config" in sys.argv
    test_only = "--test-only" in sys.argv
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies if requested
    if install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Run tests if requested
    if test_only:
        run_system_test()
        return
    
    # Check permissions
    check_permissions()
    
    # Detect devices
    detected_ports = detect_serial_ports()
    detected_usb = detect_usb_devices()
    
    # Create configuration if devices found or auto-config requested
    if (detected_ports or detected_usb) and auto_config:
        create_scanner_config(detected_ports, detected_usb)
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Start the Legal Metrology Checker application")
    print("2. Navigate to '🔌 Physical Scanner' page")
    print("3. Connect and test your scanners")
    print("\nFor detailed setup instructions, see: PHYSICAL_BARCODE_SCANNER_GUIDE.md")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage:")
        print("  python setup_physical_scanners.py --install-deps    # Install dependencies")
        print("  python setup_physical_scanners.py --auto-config     # Auto-configure detected scanners")
        print("  python setup_physical_scanners.py --test-only       # Run system tests only")
        print("  python setup_physical_scanners.py --install-deps --auto-config  # Full setup")
        print()
    
    main()


