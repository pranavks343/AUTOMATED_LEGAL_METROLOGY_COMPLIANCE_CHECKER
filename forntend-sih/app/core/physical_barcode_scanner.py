"""
Physical Barcode Scanner Integration Module
Handles integration with external USB, Serial, and Bluetooth barcode scanners
"""

import asyncio
import json
import logging
import serial
import serial.tools.list_ports
import usb.core
import usb.util
import threading
import time
import queue
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import streamlit as st
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class ScannerConnectionType(Enum):
    """Scanner connection types"""
    USB_HID = "USB_HID"
    USB_SERIAL = "USB_SERIAL"
    SERIAL_RS232 = "SERIAL_RS232"
    BLUETOOTH = "BLUETOOTH"
    NETWORK = "NETWORK"
    KEYBOARD_WEDGE = "KEYBOARD_WEDGE"

class ScannerStatus(Enum):
    """Scanner status enumeration"""
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    SCANNING = "SCANNING"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"

@dataclass
class ScannerConfig:
    """Physical scanner configuration"""
    scanner_id: str
    name: str
    manufacturer: str
    model: str
    connection_type: ScannerConnectionType
    
    # Connection parameters
    port: Optional[str] = None
    baud_rate: int = 9600
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = 'N'
    timeout: float = 1.0
    
    # USB parameters
    vendor_id: Optional[int] = None
    product_id: Optional[int] = None
    endpoint: Optional[int] = None
    
    # Network parameters
    ip_address: Optional[str] = None
    tcp_port: Optional[int] = None
    
    # Scanner settings
    scan_trigger: str = "auto"  # auto, manual, continuous
    beep_enabled: bool = True
    led_enabled: bool = True
    prefix: str = ""
    suffix: str = "\r\n"
    
    # Supported formats
    supported_formats: List[str] = None
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = [
                "Code128", "Code39", "EAN-13", "EAN-8", 
                "UPC-A", "UPC-E", "QR", "DataMatrix"
            ]

@dataclass
class ScanResult:
    """Barcode scan result"""
    scanner_id: str
    barcode: str
    format: str
    timestamp: str
    quality: float
    raw_data: Optional[bytes] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class PhysicalBarcodeScanner:
    """Base class for physical barcode scanners"""
    
    def __init__(self, config: ScannerConfig):
        self.config = config
        self.status = ScannerStatus.DISCONNECTED
        self.connection = None
        self.scan_callback = None
        self.error_callback = None
        self.scan_thread = None
        self.stop_scanning = False
        self.last_scan = None
        
    async def connect(self) -> bool:
        """Connect to the scanner"""
        raise NotImplementedError("Subclasses must implement connect method")
    
    async def disconnect(self) -> bool:
        """Disconnect from the scanner"""
        raise NotImplementedError("Subclasses must implement disconnect method")
    
    async def start_scanning(self, callback: Callable[[ScanResult], None]) -> bool:
        """Start scanning for barcodes"""
        raise NotImplementedError("Subclasses must implement start_scanning method")
    
    async def stop_scanning(self) -> bool:
        """Stop scanning"""
        raise NotImplementedError("Subclasses must implement stop_scanning method")
    
    async def configure(self, settings: Dict[str, Any]) -> bool:
        """Configure scanner settings"""
        raise NotImplementedError("Subclasses must implement configure method")

class USBSerialScanner(PhysicalBarcodeScanner):
    """USB Serial barcode scanner implementation"""
    
    async def connect(self) -> bool:
        """Connect to USB serial scanner"""
        try:
            self.status = ScannerStatus.CONNECTING
            
            # Auto-detect port if not specified
            if not self.config.port:
                self.config.port = self._auto_detect_port()
            
            if not self.config.port:
                logger.error("No suitable scanner port found")
                self.status = ScannerStatus.ERROR
                return False
            
            # Open serial connection
            self.connection = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baud_rate,
                bytesize=self.config.data_bits,
                stopbits=self.config.stop_bits,
                parity=self.config.parity,
                timeout=self.config.timeout
            )
            
            # Test connection
            if self.connection.is_open:
                self.status = ScannerStatus.CONNECTED
                logger.info(f"Connected to scanner on {self.config.port}")
                
                # Send initialization commands if needed
                await self._initialize_scanner()
                
                return True
            else:
                self.status = ScannerStatus.ERROR
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to scanner: {e}")
            self.status = ScannerStatus.ERROR
            return False
    
    def _auto_detect_port(self) -> Optional[str]:
        """Auto-detect scanner port"""
        ports = serial.tools.list_ports.comports()
        
        # Common scanner manufacturers and their USB VIDs
        scanner_vids = {
            0x05E0: "Symbol/Zebra",
            0x0C2E: "Honeywell",
            0x1504: "Microscan",
            0x04B4: "Cypress (various scanners)",
            0x0536: "Hand Held Products (Honeywell)",
            0x1659: "Prolific (various adapters)"
        }
        
        for port in ports:
            # Check if port matches known scanner VID
            if port.vid in scanner_vids:
                logger.info(f"Found potential scanner: {scanner_vids[port.vid]} on {port.device}")
                return port.device
            
            # Check device description for scanner keywords
            if port.description and any(keyword in port.description.lower() 
                                     for keyword in ['scanner', 'barcode', 'symbol', 'honeywell']):
                logger.info(f"Found scanner by description: {port.description} on {port.device}")
                return port.device
        
        # Fallback: return first available COM port
        if ports:
            logger.warning(f"No scanner detected, using first available port: {ports[0].device}")
            return ports[0].device
        
        return None
    
    async def _initialize_scanner(self):
        """Initialize scanner with configuration commands"""
        try:
            # Common scanner initialization commands
            init_commands = []
            
            # Enable/disable beep
            if self.config.beep_enabled:
                init_commands.append(b'\x16T\r')  # Enable beep
            else:
                init_commands.append(b'\x16U\r')  # Disable beep
            
            # Set prefix and suffix
            if self.config.prefix:
                init_commands.append(f'\x16P{self.config.prefix}\r'.encode())
            
            if self.config.suffix != "\r\n":
                init_commands.append(f'\x16S{self.config.suffix}\r'.encode())
            
            # Send initialization commands
            for cmd in init_commands:
                self.connection.write(cmd)
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.warning(f"Scanner initialization failed: {e}")
    
    async def disconnect(self) -> bool:
        """Disconnect from scanner"""
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
            
            self.status = ScannerStatus.DISCONNECTED
            logger.info("Scanner disconnected")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting scanner: {e}")
            return False
    
    async def start_scanning(self, callback: Callable[[ScanResult], None]) -> bool:
        """Start scanning for barcodes"""
        if self.status != ScannerStatus.CONNECTED:
            logger.error("Scanner not connected")
            return False
        
        try:
            self.scan_callback = callback
            self.stop_scanning = False
            
            # Start scanning thread
            self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
            self.scan_thread.start()
            
            self.status = ScannerStatus.SCANNING
            logger.info("Started scanning")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start scanning: {e}")
            return False
    
    def _scan_loop(self):
        """Scanning loop running in separate thread"""
        buffer = b""
        
        while not self.stop_scanning and self.connection and self.connection.is_open:
            try:
                # Read data from scanner
                if self.connection.in_waiting > 0:
                    data = self.connection.read(self.connection.in_waiting)
                    buffer += data
                    
                    # Check for complete barcode (ends with suffix)
                    suffix_bytes = self.config.suffix.encode()
                    if suffix_bytes in buffer:
                        # Extract barcode
                        barcode_end = buffer.find(suffix_bytes)
                        barcode_data = buffer[:barcode_end]
                        buffer = buffer[barcode_end + len(suffix_bytes):]
                        
                        # Remove prefix if present
                        prefix_bytes = self.config.prefix.encode()
                        if prefix_bytes and barcode_data.startswith(prefix_bytes):
                            barcode_data = barcode_data[len(prefix_bytes):]
                        
                        # Create scan result
                        barcode_str = barcode_data.decode('utf-8', errors='ignore').strip()
                        if barcode_str:
                            scan_result = ScanResult(
                                scanner_id=self.config.scanner_id,
                                barcode=barcode_str,
                                format="Unknown",  # Scanner doesn't typically report format
                                timestamp=datetime.now().isoformat(),
                                quality=95.0,  # Assume high quality for physical scanner
                                raw_data=barcode_data
                            )
                            
                            self.last_scan = scan_result
                            
                            # Call callback
                            if self.scan_callback:
                                self.scan_callback(scan_result)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in scan loop: {e}")
                if self.error_callback:
                    self.error_callback(e)
                break
    
    async def stop_scanning(self) -> bool:
        """Stop scanning"""
        try:
            self.stop_scanning = True
            
            if self.scan_thread and self.scan_thread.is_alive():
                self.scan_thread.join(timeout=2.0)
            
            self.status = ScannerStatus.CONNECTED
            logger.info("Stopped scanning")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping scan: {e}")
            return False
    
    async def configure(self, settings: Dict[str, Any]) -> bool:
        """Configure scanner settings"""
        try:
            if not self.connection or not self.connection.is_open:
                return False
            
            # Update configuration
            for key, value in settings.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # Re-initialize with new settings
            await self._initialize_scanner()
            
            return True
            
        except Exception as e:
            logger.error(f"Error configuring scanner: {e}")
            return False

class USBHIDScanner(PhysicalBarcodeScanner):
    """USB HID barcode scanner implementation"""
    
    async def connect(self) -> bool:
        """Connect to USB HID scanner"""
        try:
            self.status = ScannerStatus.CONNECTING
            
            # Find USB device
            device = usb.core.find(
                idVendor=self.config.vendor_id,
                idProduct=self.config.product_id
            )
            
            if device is None:
                # Try to find any HID scanner device
                device = self._find_scanner_device()
            
            if device is None:
                logger.error("USB HID scanner not found")
                self.status = ScannerStatus.ERROR
                return False
            
            # Detach kernel driver if necessary
            if device.is_kernel_driver_active(0):
                device.detach_kernel_driver(0)
            
            # Set configuration
            device.set_configuration()
            
            self.connection = device
            self.status = ScannerStatus.CONNECTED
            logger.info(f"Connected to USB HID scanner VID:0x{device.idVendor:04X} PID:0x{device.idProduct:04X}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to USB HID scanner: {e}")
            self.status = ScannerStatus.ERROR
            return False
    
    def _find_scanner_device(self):
        """Find USB HID scanner device"""
        # Common scanner vendor IDs
        scanner_vids = [0x05E0, 0x0C2E, 0x1504, 0x04B4, 0x0536]
        
        for vid in scanner_vids:
            devices = usb.core.find(find_all=True, idVendor=vid)
            for device in devices:
                # Check if it's an HID device (class 3)
                for cfg in device:
                    for intf in cfg:
                        if intf.bInterfaceClass == 3:  # HID class
                            return device
        
        return None
    
    async def disconnect(self) -> bool:
        """Disconnect from USB HID scanner"""
        try:
            if self.connection:
                usb.util.dispose_resources(self.connection)
            
            self.status = ScannerStatus.DISCONNECTED
            logger.info("USB HID scanner disconnected")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting USB HID scanner: {e}")
            return False
    
    async def start_scanning(self, callback: Callable[[ScanResult], None]) -> bool:
        """Start scanning for barcodes"""
        if self.status != ScannerStatus.CONNECTED:
            logger.error("Scanner not connected")
            return False
        
        try:
            self.scan_callback = callback
            self.stop_scanning = False
            
            # Start scanning thread
            self.scan_thread = threading.Thread(target=self._hid_scan_loop, daemon=True)
            self.scan_thread.start()
            
            self.status = ScannerStatus.SCANNING
            logger.info("Started USB HID scanning")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start USB HID scanning: {e}")
            return False
    
    def _hid_scan_loop(self):
        """USB HID scanning loop"""
        endpoint = self.connection[0][(0, 0)][0]
        
        while not self.stop_scanning and self.connection:
            try:
                # Read data from HID endpoint
                data = self.connection.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, timeout=100)
                
                if data:
                    # Process HID data to extract barcode
                    barcode = self._process_hid_data(data)
                    
                    if barcode:
                        scan_result = ScanResult(
                            scanner_id=self.config.scanner_id,
                            barcode=barcode,
                            format="Unknown",
                            timestamp=datetime.now().isoformat(),
                            quality=95.0,
                            raw_data=bytes(data)
                        )
                        
                        self.last_scan = scan_result
                        
                        if self.scan_callback:
                            self.scan_callback(scan_result)
                
            except usb.core.USBTimeoutError:
                # Timeout is normal, continue scanning
                continue
            except Exception as e:
                logger.error(f"Error in USB HID scan loop: {e}")
                if self.error_callback:
                    self.error_callback(e)
                break
    
    def _process_hid_data(self, data) -> Optional[str]:
        """Process HID data to extract barcode string"""
        # This is a simplified implementation
        # Real HID processing depends on the specific scanner protocol
        
        # Convert HID scan codes to ASCII
        # This is a basic implementation - real scanners may use different protocols
        try:
            # Filter out non-printable characters and convert to string
            printable_chars = [chr(b) for b in data if 32 <= b <= 126]
            barcode = ''.join(printable_chars).strip()
            
            # Return barcode if it looks valid (contains only digits/letters)
            if len(barcode) >= 8 and barcode.replace('-', '').isalnum():
                return barcode
            
        except Exception as e:
            logger.debug(f"Error processing HID data: {e}")
        
        return None
    
    async def stop_scanning(self) -> bool:
        """Stop USB HID scanning"""
        return await super().stop_scanning()
    
    async def configure(self, settings: Dict[str, Any]) -> bool:
        """Configure USB HID scanner"""
        # Most USB HID scanners have limited configuration options
        # Configuration is typically done through manufacturer-specific tools
        logger.info("USB HID scanner configuration is limited")
        return True

class PhysicalScannerManager:
    """Manager for physical barcode scanners"""
    
    def __init__(self):
        self.scanners: Dict[str, PhysicalBarcodeScanner] = {}
        self.active_scanner: Optional[PhysicalBarcodeScanner] = None
        self.config_file = Path("app/data/physical_scanners.json")
        self.scan_queue = queue.Queue()
        
        # Create config directory if it doesn't exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load scanner configurations
        self.load_configurations()
    
    def load_configurations(self):
        """Load scanner configurations from file"""
        if not self.config_file.exists():
            self._create_default_configurations()
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                
                for config_dict in data.get('scanners', []):
                    # Convert connection type back to enum
                    config_dict['connection_type'] = ScannerConnectionType(config_dict['connection_type'])
                    
                    config = ScannerConfig(**config_dict)
                    
                    # Create scanner instance based on connection type
                    if config.connection_type == ScannerConnectionType.USB_SERIAL:
                        scanner = USBSerialScanner(config)
                    elif config.connection_type == ScannerConnectionType.USB_HID:
                        scanner = USBHIDScanner(config)
                    else:
                        logger.warning(f"Unsupported connection type: {config.connection_type}")
                        continue
                    
                    self.scanners[config.scanner_id] = scanner
                    
        except Exception as e:
            logger.error(f"Error loading scanner configurations: {e}")
            self._create_default_configurations()
    
    def _create_default_configurations(self):
        """Create default scanner configurations"""
        default_configs = [
            ScannerConfig(
                scanner_id="USB_SCANNER_001",
                name="Generic USB Serial Scanner",
                manufacturer="Generic",
                model="USB-001",
                connection_type=ScannerConnectionType.USB_SERIAL,
                baud_rate=9600,
                timeout=1.0
            ),
            ScannerConfig(
                scanner_id="HID_SCANNER_001", 
                name="Generic USB HID Scanner",
                manufacturer="Generic",
                model="HID-001",
                connection_type=ScannerConnectionType.USB_HID
            )
        ]
        
        for config in default_configs:
            if config.connection_type == ScannerConnectionType.USB_SERIAL:
                scanner = USBSerialScanner(config)
            else:
                scanner = USBHIDScanner(config)
            
            self.scanners[config.scanner_id] = scanner
        
        self.save_configurations()
    
    def save_configurations(self):
        """Save scanner configurations to file"""
        try:
            data = {
                'scanners': []
            }
            
            for scanner in self.scanners.values():
                config_dict = asdict(scanner.config)
                # Convert enum to string
                config_dict['connection_type'] = scanner.config.connection_type.value
                data['scanners'].append(config_dict)
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving scanner configurations: {e}")
    
    def add_scanner(self, config: ScannerConfig) -> bool:
        """Add new scanner configuration"""
        try:
            # Create scanner instance
            if config.connection_type == ScannerConnectionType.USB_SERIAL:
                scanner = USBSerialScanner(config)
            elif config.connection_type == ScannerConnectionType.USB_HID:
                scanner = USBHIDScanner(config)
            else:
                logger.error(f"Unsupported connection type: {config.connection_type}")
                return False
            
            self.scanners[config.scanner_id] = scanner
            self.save_configurations()
            
            logger.info(f"Added scanner: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding scanner: {e}")
            return False
    
    def remove_scanner(self, scanner_id: str) -> bool:
        """Remove scanner configuration"""
        try:
            if scanner_id in self.scanners:
                # Disconnect if connected
                scanner = self.scanners[scanner_id]
                if scanner.status != ScannerStatus.DISCONNECTED:
                    asyncio.run(scanner.disconnect())
                
                del self.scanners[scanner_id]
                
                # Update active scanner if it was removed
                if self.active_scanner and self.active_scanner.config.scanner_id == scanner_id:
                    self.active_scanner = None
                
                self.save_configurations()
                logger.info(f"Removed scanner: {scanner_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing scanner: {e}")
            return False
    
    async def connect_scanner(self, scanner_id: str) -> bool:
        """Connect to a specific scanner"""
        if scanner_id not in self.scanners:
            logger.error(f"Scanner not found: {scanner_id}")
            return False
        
        scanner = self.scanners[scanner_id]
        
        # Disconnect active scanner first
        if self.active_scanner and self.active_scanner.status != ScannerStatus.DISCONNECTED:
            await self.active_scanner.disconnect()
        
        # Connect to new scanner
        success = await scanner.connect()
        
        if success:
            self.active_scanner = scanner
            logger.info(f"Connected to scanner: {scanner.config.name}")
        
        return success
    
    async def disconnect_active_scanner(self) -> bool:
        """Disconnect active scanner"""
        if not self.active_scanner:
            return True
        
        success = await self.active_scanner.disconnect()
        
        if success:
            self.active_scanner = None
            logger.info("Disconnected active scanner")
        
        return success
    
    async def start_scanning(self, callback: Callable[[ScanResult], None]) -> bool:
        """Start scanning with active scanner"""
        if not self.active_scanner:
            logger.error("No active scanner")
            return False
        
        return await self.active_scanner.start_scanning(callback)
    
    async def stop_scanning(self) -> bool:
        """Stop scanning with active scanner"""
        if not self.active_scanner:
            return True
        
        return await self.active_scanner.stop_scanning()
    
    def get_scanner_status(self, scanner_id: str) -> Optional[ScannerStatus]:
        """Get scanner status"""
        if scanner_id in self.scanners:
            return self.scanners[scanner_id].status
        return None
    
    def get_available_scanners(self) -> List[Dict[str, Any]]:
        """Get list of available scanners"""
        scanners = []
        
        for scanner in self.scanners.values():
            scanners.append({
                'scanner_id': scanner.config.scanner_id,
                'name': scanner.config.name,
                'manufacturer': scanner.config.manufacturer,
                'model': scanner.config.model,
                'connection_type': scanner.config.connection_type.value,
                'status': scanner.status.value,
                'is_active': scanner == self.active_scanner
            })
        
        return scanners
    
    def detect_connected_scanners(self) -> List[Dict[str, Any]]:
        """Detect physically connected scanners"""
        detected = []
        
        # Detect USB Serial scanners
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.description and any(keyword in port.description.lower() 
                                      for keyword in ['scanner', 'barcode', 'symbol', 'honeywell']):
                detected.append({
                    'type': 'USB_SERIAL',
                    'port': port.device,
                    'description': port.description,
                    'vid': port.vid,
                    'pid': port.pid
                })
        
        # Detect USB HID scanners
        try:
            import usb.core
            scanner_vids = [0x05E0, 0x0C2E, 0x1504, 0x04B4, 0x0536]
            
            for vid in scanner_vids:
                devices = usb.core.find(find_all=True, idVendor=vid)
                for device in devices:
                    for cfg in device:
                        for intf in cfg:
                            if intf.bInterfaceClass == 3:  # HID class
                                detected.append({
                                    'type': 'USB_HID',
                                    'vid': device.idVendor,
                                    'pid': device.idProduct,
                                    'manufacturer': usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else 'Unknown',
                                    'product': usb.util.get_string(device, device.iProduct) if device.iProduct else 'Unknown'
                                })
                                break
        except Exception as e:
            logger.debug(f"USB HID detection failed: {e}")
        
        return detected

# Global scanner manager instance
physical_scanner_manager = PhysicalScannerManager()

def get_physical_scanner_manager() -> PhysicalScannerManager:
    """Get global physical scanner manager instance"""
    return physical_scanner_manager
