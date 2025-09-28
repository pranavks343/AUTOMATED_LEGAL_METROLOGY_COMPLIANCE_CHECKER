"""
Label and Artwork Generation System
Handles compliant label generation with pre-print compliance validation
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from .json_utils import safe_json_dump, safe_json_dumps

class LabelStatus(Enum):
    """Label status enumeration"""
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PRINTED = "PRINTED"
    ARCHIVED = "ARCHIVED"

class LabelFormat(Enum):
    """Label format enumeration"""
    STANDARD = "STANDARD"      # Standard product label
    PREMIUM = "PREMIUM"        # Premium product label
    MINIMAL = "MINIMAL"        # Minimal compliance label
    DETAILED = "DETAILED"      # Detailed information label
    MULTILINGUAL = "MULTILINGUAL"  # Multi-language label

class ComplianceGateStatus(Enum):
    """Pre-print compliance gate status"""
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    OVERRIDE = "OVERRIDE"

@dataclass
class LabelElement:
    """Individual label element"""
    element_id: str
    element_type: str  # "text", "image", "barcode", "qr_code"
    content: str
    position: Tuple[int, int]  # (x, y)
    size: Tuple[int, int]      # (width, height)
    font_size: int = 12
    font_color: str = "#000000"
    background_color: Optional[str] = None
    is_mandatory: bool = False
    compliance_checked: bool = False
    validation_message: Optional[str] = None

@dataclass
class LabelDesign:
    """Label design specification"""
    label_id: str
    product_sku: str
    label_format: LabelFormat
    status: LabelStatus
    created_by: str
    created_date: str
    approved_by: Optional[str] = None
    approved_date: Optional[str] = None
    
    # Design specifications
    width: int = 400
    height: int = 300
    background_color: str = "#FFFFFF"
    border_color: str = "#000000"
    border_width: int = 2
    
    # Elements
    elements: List[LabelElement] = None
    
    # Compliance validation
    compliance_gate_status: ComplianceGateStatus = ComplianceGateStatus.PENDING
    compliance_issues: List[str] = None
    compliance_checked_date: Optional[str] = None
    compliance_checked_by: Optional[str] = None
    
    # Metadata
    version: int = 1
    notes: List[Dict[str, str]] = None
    template_id: Optional[str] = None
    
    def __post_init__(self):
        if self.elements is None:
            self.elements = []
        if self.compliance_issues is None:
            self.compliance_issues = []
        if self.notes is None:
            self.notes = []

class LabelGenerator:
    """Manages label and artwork generation with compliance validation"""
    
    def __init__(self):
        self.labels_file = Path("app/data/labels.json")
        self.labels_file.parent.mkdir(parents=True, exist_ok=True)
        self.labels = self._load_labels()
        
        # Define mandatory elements for Legal Metrology compliance
        self.mandatory_elements = {
            "product_name": {"position": (20, 20), "size": (200, 30), "mandatory": True},
            "mrp": {"position": (20, 60), "size": (100, 25), "mandatory": True, "format": "MRP: ₹{value}"},
            "net_quantity": {"position": (20, 90), "size": (150, 25), "mandatory": True, "format": "Net Qty: {value} {unit}"},
            "manufacturer": {"position": (20, 120), "size": (200, 25), "mandatory": True},
            "mfg_date": {"position": (20, 150), "size": (100, 25), "mandatory": False, "format": "Mfg Date: {date}"},
            "expiry_date": {"position": (130, 150), "size": (100, 25), "mandatory": False, "format": "Exp Date: {date}"},
            "batch_number": {"position": (20, 180), "size": (100, 25), "mandatory": False, "format": "Batch: {batch}"},
            "fssai_number": {"position": (130, 180), "size": (120, 25), "mandatory": False, "format": "FSSAI: {fssai}"},
            "country_origin": {"position": (20, 210), "size": (150, 25), "mandatory": False, "format": "Made in: {country}"},
            "barcode": {"position": (250, 20), "size": (120, 80), "mandatory": False},
            "qr_code": {"position": (250, 110), "size": (80, 80), "mandatory": False}
        }
        
        # Define label templates
        self.label_templates = self._define_label_templates()
    
    def _load_labels(self) -> List[LabelDesign]:
        """Load labels from file"""
        if not self.labels_file.exists():
            return []
        
        try:
            with open(self.labels_file, 'r') as f:
                data = json.load(f)
                labels = []
                for item in data:
                    # Convert enum values back to enum objects
                    item['label_format'] = LabelFormat(item['label_format'])
                    item['status'] = LabelStatus(item['status'])
                    item['compliance_gate_status'] = ComplianceGateStatus(item['compliance_gate_status'])
                    
                    # Convert elements
                    elements = []
                    for element_data in item.get('elements', []):
                        elements.append(LabelElement(**element_data))
                    item['elements'] = elements
                    
                    labels.append(LabelDesign(**item))
                return labels
        except Exception as e:
            print(f"Error loading labels: {e}")
            return []
    
    def _save_labels(self):
        """Save labels to file"""
        try:
            # Convert labels to dictionaries
            data = []
            for label in self.labels:
                label_dict = asdict(label)
                # Convert enums to string values
                label_dict['label_format'] = label.label_format.value
                label_dict['status'] = label.status.value
                label_dict['compliance_gate_status'] = label.compliance_gate_status.value
                
                # Convert elements
                elements_data = []
                for element in label.elements:
                    elements_data.append(asdict(element))
                label_dict['elements'] = elements_data
                
                data.append(label_dict)
            
            with open(self.labels_file, 'w') as f:
                safe_json_dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving labels: {e}")
    
    def _define_label_templates(self) -> Dict[LabelFormat, Dict[str, Any]]:
        """Define label templates for different formats"""
        return {
            LabelFormat.STANDARD: {
                "width": 400,
                "height": 300,
                "background_color": "#FFFFFF",
                "border_color": "#000000",
                "border_width": 2,
                "required_elements": ["product_name", "mrp", "net_quantity", "manufacturer"]
            },
            LabelFormat.PREMIUM: {
                "width": 500,
                "height": 400,
                "background_color": "#F8F9FA",
                "border_color": "#6C757D",
                "border_width": 3,
                "required_elements": ["product_name", "mrp", "net_quantity", "manufacturer", "mfg_date", "expiry_date"]
            },
            LabelFormat.MINIMAL: {
                "width": 300,
                "height": 200,
                "background_color": "#FFFFFF",
                "border_color": "#000000",
                "border_width": 1,
                "required_elements": ["product_name", "mrp", "net_quantity"]
            },
            LabelFormat.DETAILED: {
                "width": 600,
                "height": 500,
                "background_color": "#FFFFFF",
                "border_color": "#000000",
                "border_width": 2,
                "required_elements": ["product_name", "mrp", "net_quantity", "manufacturer", "mfg_date", "expiry_date", "batch_number", "fssai_number", "country_origin"]
            }
        }
    
    def generate_label_id(self, product_sku: str) -> str:
        """Generate unique label ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"LABEL-{product_sku}-{timestamp}"
    
    def create_label_from_product(self, product_data: Dict[str, Any], label_format: LabelFormat, 
                                 created_by: str) -> LabelDesign:
        """Create label design from product data"""
        
        label_id = self.generate_label_id(product_data.get('sku', 'UNKNOWN'))
        template = self.label_templates[label_format]
        
        # Create label design
        label = LabelDesign(
            label_id=label_id,
            product_sku=product_data.get('sku', ''),
            label_format=label_format,
            status=LabelStatus.DRAFT,
            created_by=created_by,
            created_date=datetime.now().isoformat(),
            width=template["width"],
            height=template["height"],
            background_color=template["background_color"],
            border_color=template["border_color"],
            border_width=template["border_width"]
        )
        
        # Add elements based on template and product data
        self._add_label_elements(label, product_data, template)
        
        # Perform initial compliance check
        self._perform_compliance_check(label, created_by)
        
        self.labels.append(label)
        self._save_labels()
        
        return label
    
    def _add_label_elements(self, label: LabelDesign, product_data: Dict[str, Any], template: Dict[str, Any]):
        """Add elements to label based on template and product data"""
        
        for element_name, element_config in self.mandatory_elements.items():
            if element_name in template.get("required_elements", []):
                element_id = f"{label.label_id}-{element_name}"
                
                # Format content based on element type
                content = self._format_element_content(element_name, element_config, product_data)
                
                if content:  # Only add if content is available
                    element = LabelElement(
                        element_id=element_id,
                        element_type="text",
                        content=content,
                        position=element_config["position"],
                        size=element_config["size"],
                        is_mandatory=element_config.get("mandatory", False),
                        font_size=12,
                        font_color="#000000"
                    )
                    label.elements.append(element)
    
    def _format_element_content(self, element_name: str, element_config: Dict[str, Any], product_data: Dict[str, Any]) -> str:
        """Format element content based on type and product data"""
        
        if element_name == "product_name":
            return product_data.get('product_name', '')
        elif element_name == "mrp":
            mrp = product_data.get('mrp', 0)
            return f"MRP: ₹{mrp:.2f}"
        elif element_name == "net_quantity":
            qty = product_data.get('net_quantity', 0)
            unit = product_data.get('unit', '')
            return f"Net Qty: {qty} {unit}"
        elif element_name == "manufacturer":
            return product_data.get('manufacturer_name', '')
        elif element_name == "mfg_date":
            mfg_date = product_data.get('mfg_date', '')
            return f"Mfg Date: {mfg_date}" if mfg_date else ""
        elif element_name == "expiry_date":
            exp_date = product_data.get('expiry_date', '')
            return f"Exp Date: {exp_date}" if exp_date else ""
        elif element_name == "batch_number":
            batch = product_data.get('batch_number', '')
            return f"Batch: {batch}" if batch else ""
        elif element_name == "fssai_number":
            fssai = product_data.get('fssai_number', '')
            return f"FSSAI: {fssai}" if fssai else ""
        elif element_name == "country_origin":
            country = product_data.get('country_of_origin', '')
            return f"Made in: {country}" if country else ""
        elif element_name in ["barcode", "qr_code"]:
            return f"[{element_name.upper()}]"  # Placeholder for barcode/QR code
        
        return ""
    
    def _perform_compliance_check(self, label: LabelDesign, checked_by: str):
        """Perform pre-print compliance validation"""
        
        compliance_issues = []
        
        # Check mandatory elements
        mandatory_elements = [e for e in label.elements if e.is_mandatory]
        for element in mandatory_elements:
            if not element.content or element.content.strip() == "":
                compliance_issues.append(f"Mandatory element '{element.element_id}' is empty")
            else:
                element.compliance_checked = True
                element.validation_message = "Compliance check passed"
        
        # Check Legal Metrology specific requirements
        if not any("MRP" in e.content for e in label.elements):
            compliance_issues.append("MRP information is missing or incomplete")
        
        if not any("Net Qty" in e.content for e in label.elements):
            compliance_issues.append("Net quantity information is missing or incomplete")
        
        # Check font size requirements (minimum 6pt for readability)
        for element in label.elements:
            if element.font_size < 6:
                compliance_issues.append(f"Font size too small for element '{element.element_id}'")
        
        # Check label dimensions
        if label.width < 100 or label.height < 50:
            compliance_issues.append("Label dimensions too small for compliance")
        
        # Update compliance status
        label.compliance_issues = compliance_issues
        label.compliance_checked_date = datetime.now().isoformat()
        label.compliance_checked_by = checked_by
        
        if not compliance_issues:
            label.compliance_gate_status = ComplianceGateStatus.PASSED
        else:
            label.compliance_gate_status = ComplianceGateStatus.FAILED
        
        # Add compliance check note
        label.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": checked_by,
            "note": f"Compliance check {'PASSED' if not compliance_issues else 'FAILED'}: {len(compliance_issues)} issues found"
        })
    
    def generate_label_image(self, label_id: str) -> Optional[bytes]:
        """Generate actual label image"""
        
        label = self.get_label(label_id)
        if not label:
            return None
        
        try:
            # Create image
            image = Image.new('RGB', (label.width, label.height), label.background_color)
            draw = ImageDraw.Draw(image)
            
            # Draw border
            if label.border_width > 0:
                draw.rectangle([0, 0, label.width-1, label.height-1], 
                             outline=label.border_color, width=label.border_width)
            
            # Try to load a font, fallback to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            # Draw elements
            for element in label.elements:
                if element.element_type == "text" and element.content:
                    # Draw text
                    draw.text(element.position, element.content, 
                             fill=element.font_color, font=font)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            print(f"Error generating label image: {e}")
            return None
    
    def approve_label(self, label_id: str, approved_by: str, notes: str = None) -> bool:
        """Approve label for printing"""
        
        label = self.get_label(label_id)
        if not label:
            return False
        
        if label.compliance_gate_status != ComplianceGateStatus.PASSED:
            return False  # Cannot approve non-compliant labels
        
        label.status = LabelStatus.APPROVED
        label.approved_by = approved_by
        label.approved_date = datetime.now().isoformat()
        label.version += 1
        
        # Add approval note
        approval_note = f"Label approved by {approved_by}"
        if notes:
            approval_note += f": {notes}"
        
        label.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": approved_by,
            "note": approval_note
        })
        
        self._save_labels()
        return True
    
    def reject_label(self, label_id: str, rejected_by: str, reason: str) -> bool:
        """Reject label design"""
        
        label = self.get_label(label_id)
        if not label:
            return False
        
        label.status = LabelStatus.REJECTED
        label.version += 1
        
        # Add rejection note
        label.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": rejected_by,
            "note": f"Label rejected by {rejected_by}: {reason}"
        })
        
        self._save_labels()
        return True
    
    def get_label(self, label_id: str) -> Optional[LabelDesign]:
        """Get label by ID"""
        for label in self.labels:
            if label.label_id == label_id:
                return label
        return None
    
    def get_labels_by_product(self, product_sku: str) -> List[LabelDesign]:
        """Get labels by product SKU"""
        return [label for label in self.labels if label.product_sku == product_sku]
    
    def get_labels_by_status(self, status: LabelStatus) -> List[LabelDesign]:
        """Get labels by status"""
        return [label for label in self.labels if label.status == status]
    
    def get_label_statistics(self) -> Dict[str, Any]:
        """Get label generation statistics"""
        total = len(self.labels)
        
        if total == 0:
            return {
                "total_labels": 0,
                "by_status": {},
                "by_format": {},
                "compliance_pass_rate": 0,
                "approved_labels": 0,
                "pending_labels": 0
            }
        
        # Count by status
        status_counts = {}
        for status in LabelStatus:
            status_counts[status.value] = len(self.get_labels_by_status(status))
        
        # Count by format
        format_counts = {}
        for format_type in LabelFormat:
            format_counts[format_type.value] = len([l for l in self.labels if l.label_format == format_type])
        
        # Calculate compliance pass rate
        passed_labels = len([l for l in self.labels if l.compliance_gate_status == ComplianceGateStatus.PASSED])
        compliance_pass_rate = (passed_labels / total) * 100 if total > 0 else 0
        
        return {
            "total_labels": total,
            "by_status": status_counts,
            "by_format": format_counts,
            "compliance_pass_rate": round(compliance_pass_rate, 2),
            "approved_labels": status_counts.get("APPROVED", 0),
            "pending_labels": status_counts.get("DRAFT", 0) + status_counts.get("UNDER_REVIEW", 0)
        }

# Global label generator instance
label_generator = LabelGenerator()
