"""
Physical System Integration Module
Handles integration with printing and vision systems for end-to-end compliance assurance
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from .json_utils import safe_json_dump, safe_json_dumps

class IntegrationStatus(Enum):
    """Integration status enumeration"""
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    ERROR = "ERROR"
    MAINTENANCE = "MAINTENANCE"

class PrintStatus(Enum):
    """Print status enumeration"""
    PENDING = "PENDING"
    PRINTING = "PRINTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class VisionCheckStatus(Enum):
    """Vision check status enumeration"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"

class DeviceType(Enum):
    """Device type enumeration"""
    PRINTER = "PRINTER"
    VISION_SYSTEM = "VISION_SYSTEM"
    BARCODE_SCANNER = "BARCODE_SCANNER"
    LABEL_APPLICATOR = "LABEL_APPLICATOR"
    CONVEYOR_SYSTEM = "CONVEYOR_SYSTEM"
    # Extended device types for physical barcode scanners
    USB_SERIAL_SCANNER = "USB_SERIAL_SCANNER"
    USB_HID_SCANNER = "USB_HID_SCANNER"
    BLUETOOTH_SCANNER = "BLUETOOTH_SCANNER"
    NETWORK_SCANNER = "NETWORK_SCANNER"

@dataclass
class PhysicalDevice:
    """Physical device configuration"""
    device_id: str
    device_name: str
    device_type: DeviceType
    manufacturer: str
    model: str
    status: IntegrationStatus
    ip_address: Optional[str] = None
    port: Optional[int] = None
    connection_string: Optional[str] = None
    
    # Device capabilities
    capabilities: List[str] = None
    supported_formats: List[str] = None
    max_resolution: Optional[Dict[str, int]] = None
    
    # Configuration
    config: Dict[str, Any] = None
    last_heartbeat: Optional[str] = None
    error_count: int = 0
    last_error: Optional[str] = None
    
    # Metadata
    installed_date: str = None
    last_maintenance: Optional[str] = None
    maintenance_schedule: Optional[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.supported_formats is None:
            self.supported_formats = []
        if self.config is None:
            self.config = {}
        if self.installed_date is None:
            self.installed_date = datetime.now().isoformat()

@dataclass
class PrintJob:
    """Print job definition"""
    job_id: str
    label_id: str
    product_sku: str
    device_id: str
    status: PrintStatus
    created_by: str
    created_date: str
    
    # Print specifications
    copies: int = 1
    print_format: str = "PNG"
    resolution: int = 300
    color_mode: str = "RGB"
    
    # Job details
    priority: int = 1
    scheduled_time: Optional[str] = None
    started_time: Optional[str] = None
    completed_time: Optional[str] = None
    
    # Results
    success_count: int = 0
    failure_count: int = 0
    error_message: Optional[str] = None
    
    # Metadata
    notes: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.notes is None:
            self.notes = []

@dataclass
class VisionCheck:
    """Vision system check result"""
    check_id: str
    product_sku: str
    image_path: str
    status: VisionCheckStatus
    performed_by: str
    performed_date: str
    
    # Check results
    compliance_score: float = 0.0
    detected_issues: List[str] = None
    confidence_level: float = 0.0
    
    # Analysis details
    text_recognition_results: Dict[str, Any] = None
    element_detection_results: Dict[str, Any] = None
    compliance_analysis: Dict[str, Any] = None
    
    # Quality metrics
    image_quality_score: float = 0.0
    lighting_score: float = 0.0
    sharpness_score: float = 0.0
    
    # Metadata
    notes: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.detected_issues is None:
            self.detected_issues = []
        if self.text_recognition_results is None:
            self.text_recognition_results = {}
        if self.element_detection_results is None:
            self.element_detection_results = {}
        if self.compliance_analysis is None:
            self.compliance_analysis = {}
        if self.notes is None:
            self.notes = []

class PhysicalIntegrationManager:
    """Manages integration with physical systems"""
    
    def __init__(self):
        self.devices_file = Path("app/data/physical_devices.json")
        self.print_jobs_file = Path("app/data/print_jobs.json")
        self.vision_checks_file = Path("app/data/vision_checks.json")
        
        # Create directories if they don't exist
        for file_path in [self.devices_file, self.print_jobs_file, self.vision_checks_file]:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.devices = self._load_devices()
        self.print_jobs = self._load_print_jobs()
        self.vision_checks = self._load_vision_checks()
        
        # Initialize default devices if none exist
        if not self.devices:
            self._initialize_default_devices()
    
    def _load_devices(self) -> List[PhysicalDevice]:
        """Load physical devices from file"""
        if not self.devices_file.exists():
            return []
        
        try:
            with open(self.devices_file, 'r') as f:
                data = json.load(f)
                devices = []
                for item in data:
                    # Convert enum values back to enum objects
                    item['device_type'] = DeviceType(item['device_type'])
                    item['status'] = IntegrationStatus(item['status'])
                    devices.append(PhysicalDevice(**item))
                return devices
        except Exception as e:
            print(f"Error loading physical devices: {e}")
            return []
    
    def _load_print_jobs(self) -> List[PrintJob]:
        """Load print jobs from file"""
        if not self.print_jobs_file.exists():
            return []
        
        try:
            with open(self.print_jobs_file, 'r') as f:
                data = json.load(f)
                jobs = []
                for item in data:
                    # Convert enum values back to enum objects
                    item['status'] = PrintStatus(item['status'])
                    jobs.append(PrintJob(**item))
                return jobs
        except Exception as e:
            print(f"Error loading print jobs: {e}")
            return []
    
    def _load_vision_checks(self) -> List[VisionCheck]:
        """Load vision checks from file"""
        if not self.vision_checks_file.exists():
            return []
        
        try:
            with open(self.vision_checks_file, 'r') as f:
                data = json.load(f)
                checks = []
                for item in data:
                    # Convert enum values back to enum objects
                    item['status'] = VisionCheckStatus(item['status'])
                    checks.append(VisionCheck(**item))
                return checks
        except Exception as e:
            print(f"Error loading vision checks: {e}")
            return []
    
    def _save_devices(self):
        """Save physical devices to file"""
        try:
            # Convert devices to dictionaries
            data = []
            for device in self.devices:
                device_dict = asdict(device)
                # Convert enums to string values
                device_dict['device_type'] = device.device_type.value
                device_dict['status'] = device.status.value
                data.append(device_dict)
            
            with open(self.devices_file, 'w') as f:
                safe_json_dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving physical devices: {e}")
    
    def _save_print_jobs(self):
        """Save print jobs to file"""
        try:
            # Convert print jobs to dictionaries
            data = []
            for job in self.print_jobs:
                job_dict = asdict(job)
                # Convert enums to string values
                job_dict['status'] = job.status.value
                data.append(job_dict)
            
            with open(self.print_jobs_file, 'w') as f:
                safe_json_dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving print jobs: {e}")
    
    def _save_vision_checks(self):
        """Save vision checks to file"""
        try:
            # Convert vision checks to dictionaries
            data = []
            for check in self.vision_checks:
                check_dict = asdict(check)
                # Convert enums to string values
                check_dict['status'] = check.status.value
                data.append(check_dict)
            
            with open(self.vision_checks_file, 'w') as f:
                safe_json_dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving vision checks: {e}")
    
    def _initialize_default_devices(self):
        """Initialize default physical devices"""
        default_devices = [
            PhysicalDevice(
                device_id="PRINTER001",
                device_name="Label Printer - Main Production",
                device_type=DeviceType.PRINTER,
                manufacturer="Zebra Technologies",
                model="ZT230",
                status=IntegrationStatus.DISCONNECTED,
                ip_address="192.168.1.100",
                port=9100,
                capabilities=["label_printing", "barcode_generation", "qr_code_generation"],
                supported_formats=["PNG", "PDF", "ZPL"],
                max_resolution={"width": 203, "height": 1016},
                config={"dpi": 203, "print_speed": "6", "darkness": "10"}
            ),
            PhysicalDevice(
                device_id="VISION001",
                device_name="Vision Inspection System - Quality Control",
                device_type=DeviceType.VISION_SYSTEM,
                manufacturer="Cognex",
                model="In-Sight 7000",
                status=IntegrationStatus.DISCONNECTED,
                ip_address="192.168.1.101",
                port=8080,
                capabilities=["text_recognition", "element_detection", "compliance_validation"],
                supported_formats=["JPEG", "PNG", "TIFF"],
                max_resolution={"width": 1280, "height": 1024},
                config={"camera_exposure": "auto", "lighting_intensity": "medium"}
            ),
            PhysicalDevice(
                device_id="SCANNER001",
                device_name="Barcode Scanner - Verification",
                device_type=DeviceType.BARCODE_SCANNER,
                manufacturer="Honeywell",
                model="1450g",
                status=IntegrationStatus.DISCONNECTED,
                connection_string="USB",
                capabilities=["barcode_scanning", "qr_code_scanning", "data_validation"],
                supported_formats=["Code128", "QR", "DataMatrix"],
                config={"beep_enabled": True, "led_enabled": True}
            )
        ]
        
        self.devices.extend(default_devices)
        self._save_devices()
    
    def generate_job_id(self) -> str:
        """Generate unique job ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        count = len([j for j in self.print_jobs if j.job_id.startswith(f"JOB-{timestamp}")])
        return f"JOB-{timestamp}-{count:03d}"
    
    def generate_check_id(self) -> str:
        """Generate unique check ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        count = len([c for c in self.vision_checks if c.check_id.startswith(f"CHECK-{timestamp}")])
        return f"CHECK-{timestamp}-{count:03d}"
    
    def add_device(self, device_name: str, device_type: DeviceType, manufacturer: str,
                   model: str, ip_address: str = None, port: int = None,
                   capabilities: List[str] = None, config: Dict[str, Any] = None) -> PhysicalDevice:
        """Add new physical device"""
        
        device_id = f"{device_type.value}001"  # Simplified ID generation
        if any(d.device_id == device_id for d in self.devices):
            # Find next available ID
            count = 1
            while any(d.device_id == f"{device_type.value}{count:03d}" for d in self.devices):
                count += 1
            device_id = f"{device_type.value}{count:03d}"
        
        device = PhysicalDevice(
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            manufacturer=manufacturer,
            model=model,
            status=IntegrationStatus.DISCONNECTED,
            ip_address=ip_address,
            port=port,
            capabilities=capabilities or [],
            config=config or {}
        )
        
        self.devices.append(device)
        self._save_devices()
        
        return device
    
    def connect_device(self, device_id: str) -> bool:
        """Simulate device connection"""
        device = self.get_device(device_id)
        if not device:
            return False
        
        device.status = IntegrationStatus.CONNECTING
        self._save_devices()
        
        # Simulate connection process
        import time
        time.sleep(1)  # Simulate connection delay
        
        device.status = IntegrationStatus.CONNECTED
        device.last_heartbeat = datetime.now().isoformat()
        device.error_count = 0
        device.last_error = None
        
        self._save_devices()
        return True
    
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect device"""
        device = self.get_device(device_id)
        if not device:
            return False
        
        device.status = IntegrationStatus.DISCONNECTED
        device.last_heartbeat = None
        
        self._save_devices()
        return True
    
    def create_print_job(self, label_id: str, product_sku: str, device_id: str,
                        created_by: str, copies: int = 1, **kwargs) -> PrintJob:
        """Create new print job"""
        
        job_id = self.generate_job_id()
        
        job = PrintJob(
            job_id=job_id,
            label_id=label_id,
            product_sku=product_sku,
            device_id=device_id,
            status=PrintStatus.PENDING,
            created_by=created_by,
            created_date=datetime.now().isoformat(),
            copies=copies,
            print_format=kwargs.get('print_format', 'PNG'),
            resolution=kwargs.get('resolution', 300),
            color_mode=kwargs.get('color_mode', 'RGB'),
            priority=kwargs.get('priority', 1),
            scheduled_time=kwargs.get('scheduled_time')
        )
        
        self.print_jobs.append(job)
        self._save_print_jobs()
        
        return job
    
    def execute_print_job(self, job_id: str) -> bool:
        """Execute print job"""
        job = self.get_print_job(job_id)
        if not job:
            return False
        
        device = self.get_device(job.device_id)
        if not device or device.status != IntegrationStatus.CONNECTED:
            job.status = PrintStatus.FAILED
            job.error_message = "Device not connected"
            self._save_print_jobs()
            return False
        
        # Update job status
        job.status = PrintStatus.PRINTING
        job.started_time = datetime.now().isoformat()
        self._save_print_jobs()
        
        # Simulate printing process
        import time
        time.sleep(2)  # Simulate printing time
        
        # Complete job
        job.status = PrintStatus.COMPLETED
        job.completed_time = datetime.now().isoformat()
        job.success_count = job.copies
        job.failure_count = 0
        
        # Add completion note
        job.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": "system",
            "note": f"Print job completed successfully. Printed {job.copies} copies."
        })
        
        self._save_print_jobs()
        return True
    
    def create_vision_check(self, product_sku: str, image_path: str, performed_by: str) -> VisionCheck:
        """Create new vision check"""
        
        check_id = self.generate_check_id()
        
        check = VisionCheck(
            check_id=check_id,
            product_sku=product_sku,
            image_path=image_path,
            status=VisionCheckStatus.PENDING,
            performed_by=performed_by,
            performed_date=datetime.now().isoformat()
        )
        
        self.vision_checks.append(check)
        self._save_vision_checks()
        
        return check
    
    def execute_vision_check(self, check_id: str) -> bool:
        """Execute vision check"""
        check = self.get_vision_check(check_id)
        if not check:
            return False
        
        # Update check status
        check.status = VisionCheckStatus.IN_PROGRESS
        self._save_vision_checks()
        
        # Simulate vision analysis
        import time
        import random
        time.sleep(3)  # Simulate analysis time
        
        # Simulate analysis results
        check.compliance_score = random.uniform(75, 95)
        check.confidence_level = random.uniform(80, 95)
        check.image_quality_score = random.uniform(70, 90)
        check.lighting_score = random.uniform(75, 85)
        check.sharpness_score = random.uniform(80, 95)
        
        # Simulate text recognition
        check.text_recognition_results = {
            "mrp_detected": random.choice([True, False]),
            "quantity_detected": random.choice([True, False]),
            "manufacturer_detected": random.choice([True, False]),
            "confidence": random.uniform(75, 95)
        }
        
        # Simulate element detection
        check.element_detection_results = {
            "barcode_detected": random.choice([True, False]),
            "qr_code_detected": random.choice([True, False]),
            "text_elements": random.randint(3, 8),
            "layout_score": random.uniform(70, 90)
        }
        
        # Simulate compliance analysis
        check.compliance_analysis = {
            "mrp_compliance": check.compliance_score > 80,
            "quantity_compliance": check.compliance_score > 75,
            "labeling_compliance": check.compliance_score > 85,
            "overall_compliance": check.compliance_score > 80
        }
        
        # Determine final status
        if check.compliance_score >= 80:
            check.status = VisionCheckStatus.PASSED
            check.detected_issues = []
        else:
            check.status = VisionCheckStatus.FAILED
            check.detected_issues = [
                "Low compliance score detected",
                "Some text elements not clearly visible",
                "Label positioning may need adjustment"
            ]
        
        # Add analysis note
        check.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": "system",
            "note": f"Vision check completed. Compliance score: {check.compliance_score:.1f}%"
        })
        
        self._save_vision_checks()
        return True
    
    def get_device(self, device_id: str) -> Optional[PhysicalDevice]:
        """Get device by ID"""
        for device in self.devices:
            if device.device_id == device_id:
                return device
        return None
    
    def get_print_job(self, job_id: str) -> Optional[PrintJob]:
        """Get print job by ID"""
        for job in self.print_jobs:
            if job.job_id == job_id:
                return job
        return None
    
    def get_vision_check(self, check_id: str) -> Optional[VisionCheck]:
        """Get vision check by ID"""
        for check in self.vision_checks:
            if check.check_id == check_id:
                return check
        return None
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[PhysicalDevice]:
        """Get devices by type"""
        return [device for device in self.devices if device.device_type == device_type]
    
    def get_connected_devices(self) -> List[PhysicalDevice]:
        """Get connected devices"""
        return [device for device in self.devices if device.status == IntegrationStatus.CONNECTED]
    
    def get_print_jobs_by_status(self, status: PrintStatus) -> List[PrintJob]:
        """Get print jobs by status"""
        return [job for job in self.print_jobs if job.status == status]
    
    def get_vision_checks_by_status(self, status: VisionCheckStatus) -> List[VisionCheck]:
        """Get vision checks by status"""
        return [check for check in self.vision_checks if check.status == status]
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get physical integration statistics"""
        
        # Device statistics
        total_devices = len(self.devices)
        connected_devices = len(self.get_connected_devices())
        
        device_type_counts = {}
        for device_type in DeviceType:
            device_type_counts[device_type.value] = len(self.get_devices_by_type(device_type))
        
        device_status_counts = {}
        for status in IntegrationStatus:
            device_status_counts[status.value] = len([d for d in self.devices if d.status == status])
        
        # Print job statistics
        total_jobs = len(self.print_jobs)
        
        job_status_counts = {}
        for status in PrintStatus:
            job_status_counts[status.value] = len(self.get_print_jobs_by_status(status))
        
        # Vision check statistics
        total_checks = len(self.vision_checks)
        
        check_status_counts = {}
        for status in VisionCheckStatus:
            check_status_counts[status.value] = len(self.get_vision_checks_by_status(status))
        
        # Calculate success rates
        completed_jobs = len(self.get_print_jobs_by_status(PrintStatus.COMPLETED))
        print_success_rate = (completed_jobs / total_jobs) * 100 if total_jobs > 0 else 0
        
        passed_checks = len(self.get_vision_checks_by_status(VisionCheckStatus.PASSED))
        vision_success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        return {
            "total_devices": total_devices,
            "connected_devices": connected_devices,
            "total_print_jobs": total_jobs,
            "total_vision_checks": total_checks,
            "devices_by_type": device_type_counts,
            "devices_by_status": device_status_counts,
            "jobs_by_status": job_status_counts,
            "checks_by_status": check_status_counts,
            "print_success_rate": round(print_success_rate, 2),
            "vision_success_rate": round(vision_success_rate, 2),
            "pending_jobs": job_status_counts.get("PENDING", 0),
            "pending_checks": check_status_counts.get("PENDING", 0)
        }

# Global physical integration manager instance
physical_integration_manager = PhysicalIntegrationManager()
