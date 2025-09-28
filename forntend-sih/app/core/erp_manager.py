"""
ERP Product Data Management System
Handles product data entry, management, and integration with Legal Metrology compliance
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from .json_utils import safe_json_dump, safe_json_dumps

class ProductStatus(Enum):
    """Product status enumeration"""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    DISPATCHED = "DISPATCHED"

class ProductCategory(Enum):
    """Product category enumeration"""
    FOOD = "FOOD"
    BEVERAGES = "BEVERAGES"
    COSMETICS = "COSMETICS"
    PHARMACEUTICALS = "PHARMACEUTICALS"
    CHEMICALS = "CHEMICALS"
    TEXTILES = "TEXTILES"
    ELECTRONICS = "ELECTRONICS"
    AUTOMOTIVE = "AUTOMOTIVE"
    OTHER = "OTHER"

@dataclass
class ProductData:
    """ERP Product data model"""
    sku: str
    product_name: str
    mrp: float
    net_quantity: float
    unit: str
    manufacturer_name: str
    manufacturer_address: Optional[str] = None
    category: ProductCategory = ProductCategory.OTHER
    status: ProductStatus = ProductStatus.DRAFT
    created_by: str = None
    created_date: str = None
    last_modified_by: str = None
    last_modified_date: str = None
    
    # Legal Metrology specific fields
    mfg_date: Optional[str] = None
    expiry_date: Optional[str] = None
    batch_number: Optional[str] = None
    fssai_number: Optional[str] = None
    country_of_origin: Optional[str] = None
    
    # Compliance tracking
    compliance_status: Optional[str] = None
    validation_date: Optional[str] = None
    validated_by: Optional[str] = None
    compliance_issues: List[str] = None
    approval_date: Optional[str] = None
    approved_by: Optional[str] = None
    
    # Additional metadata
    notes: List[Dict[str, str]] = None
    tags: List[str] = None
    version: int = 1
    
    def __post_init__(self):
        if self.compliance_issues is None:
            self.compliance_issues = []
        if self.notes is None:
            self.notes = []
        if self.tags is None:
            self.tags = []
        if self.created_date is None:
            self.created_date = datetime.now().isoformat()
        if self.last_modified_date is None:
            self.last_modified_date = datetime.now().isoformat()

class ERPManager:
    """Manages ERP product data and integration with Legal Metrology compliance"""
    
    def __init__(self):
        self.products_file = Path("app/data/erp_products.json")
        self.products_file.parent.mkdir(parents=True, exist_ok=True)
        self.products = self._load_products()
    
    def _load_products(self) -> List[ProductData]:
        """Load products from file"""
        if not self.products_file.exists():
            return []
        
        try:
            with open(self.products_file, 'r') as f:
                data = json.load(f)
                products = []
                for item in data:
                    # Convert enum values back to enum objects
                    item['category'] = ProductCategory(item['category'])
                    item['status'] = ProductStatus(item['status'])
                    products.append(ProductData(**item))
                return products
        except Exception as e:
            print(f"Error loading products: {e}")
            return []
    
    def _save_products(self):
        """Save products to file"""
        try:
            # Convert products to dictionaries
            data = []
            for product in self.products:
                product_dict = asdict(product)
                # Convert enums to string values
                product_dict['category'] = product.category.value
                product_dict['status'] = product.status.value
                data.append(product_dict)
            
            with open(self.products_file, 'w') as f:
                safe_json_dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving products: {e}")
    
    def generate_sku(self, product_name: str) -> str:
        """Generate unique SKU"""
        base_sku = ''.join(c.upper() for c in product_name if c.isalnum())[:6]
        timestamp = datetime.now().strftime("%y%m%d")
        
        # Find next number for this base SKU
        existing_skus = [p.sku for p in self.products if p.sku.startswith(f"{base_sku}-{timestamp}")]
        if existing_skus:
            last_num = max(int(sku.split('-')[-1]) for sku in existing_skus if sku.split('-')[-1].isdigit())
            num = last_num + 1
        else:
            num = 1
        
        return f"{base_sku}-{timestamp}-{num:03d}"
    
    def add_product(self, product_name: str, mrp: float, net_quantity: float, 
                   unit: str, manufacturer_name: str, category: ProductCategory,
                   created_by: str, **kwargs) -> ProductData:
        """Add new product to ERP system"""
        
        # Generate SKU if not provided
        sku = kwargs.get('sku', self.generate_sku(product_name))
        
        # Check if SKU already exists
        if self.get_product_by_sku(sku):
            raise ValueError(f"Product with SKU {sku} already exists")
        
        product = ProductData(
            sku=sku,
            product_name=product_name,
            mrp=mrp,
            net_quantity=net_quantity,
            unit=unit,
            manufacturer_name=manufacturer_name,
            category=category,
            created_by=created_by,
            created_date=datetime.now().isoformat(),
            last_modified_by=created_by,
            last_modified_date=datetime.now().isoformat(),
            manufacturer_address=kwargs.get('manufacturer_address'),
            mfg_date=kwargs.get('mfg_date'),
            expiry_date=kwargs.get('expiry_date'),
            batch_number=kwargs.get('batch_number'),
            fssai_number=kwargs.get('fssai_number'),
            country_of_origin=kwargs.get('country_of_origin'),
            tags=kwargs.get('tags', [])
        )
        
        self.products.append(product)
        self._save_products()
        
        return product
    
    def get_product_by_sku(self, sku: str) -> Optional[ProductData]:
        """Get product by SKU"""
        for product in self.products:
            if product.sku == sku:
                return product
        return None
    
    def get_all_products(self) -> List[ProductData]:
        """Get all products"""
        return self.products
    
    def get_products_by_status(self, status: ProductStatus) -> List[ProductData]:
        """Get products by status"""
        return [p for p in self.products if p.status == status]
    
    def get_products_by_category(self, category: ProductCategory) -> List[ProductData]:
        """Get products by category"""
        return [p for p in self.products if p.category == category]
    
    def update_product_status(self, sku: str, new_status: ProductStatus, 
                             updated_by: str, notes: str = None) -> bool:
        """Update product status"""
        product = self.get_product_by_sku(sku)
        if not product:
            return False
        
        old_status = product.status
        product.status = new_status
        product.last_modified_by = updated_by
        product.last_modified_date = datetime.now().isoformat()
        product.version += 1
        
        # Add note about status change
        if notes:
            product.notes.append({
                "timestamp": datetime.now().isoformat(),
                "user": updated_by,
                "note": f"Status changed from {old_status.value} to {new_status.value}: {notes}"
            })
        else:
            product.notes.append({
                "timestamp": datetime.now().isoformat(),
                "user": updated_by,
                "note": f"Status changed from {old_status.value} to {new_status.value}"
            })
        
        self._save_products()
        return True
    
    def update_compliance_status(self, sku: str, compliance_status: str, 
                                validated_by: str, issues: List[str] = None) -> bool:
        """Update product compliance status"""
        product = self.get_product_by_sku(sku)
        if not product:
            return False
        
        product.compliance_status = compliance_status
        product.validation_date = datetime.now().isoformat()
        product.validated_by = validated_by
        product.last_modified_by = validated_by
        product.last_modified_date = datetime.now().isoformat()
        product.version += 1
        
        if issues:
            product.compliance_issues = issues
        
        # Add validation note
        product.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": validated_by,
            "note": f"Compliance validation completed: {compliance_status}"
        })
        
        if issues:
            for issue in issues:
                product.notes.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": validated_by,
                    "note": f"Compliance issue: {issue}"
                })
        
        self._save_products()
        return True
    
    def approve_product(self, sku: str, approved_by: str, notes: str = None) -> bool:
        """Approve product for dispatch"""
        product = self.get_product_by_sku(sku)
        if not product:
            return False
        
        product.status = ProductStatus.APPROVED
        product.approval_date = datetime.now().isoformat()
        product.approved_by = approved_by
        product.last_modified_by = approved_by
        product.last_modified_date = datetime.now().isoformat()
        product.version += 1
        
        # Add approval note
        approval_note = f"Product approved by {approved_by}"
        if notes:
            approval_note += f": {notes}"
        
        product.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": approved_by,
            "note": approval_note
        })
        
        self._save_products()
        return True
    
    def block_product(self, sku: str, blocked_by: str, reason: str) -> bool:
        """Block product from dispatch"""
        product = self.get_product_by_sku(sku)
        if not product:
            return False
        
        product.status = ProductStatus.BLOCKED
        product.last_modified_by = blocked_by
        product.last_modified_date = datetime.now().isoformat()
        product.version += 1
        
        # Add blocking note
        product.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": blocked_by,
            "note": f"Product blocked: {reason}"
        })
        
        self._save_products()
        return True
    
    def dispatch_product(self, sku: str, dispatched_by: str, dispatch_notes: str = None) -> bool:
        """Mark product as dispatched"""
        product = self.get_product_by_sku(sku)
        if not product or product.status != ProductStatus.APPROVED:
            return False
        
        product.status = ProductStatus.DISPATCHED
        product.last_modified_by = dispatched_by
        product.last_modified_date = datetime.now().isoformat()
        product.version += 1
        
        # Add dispatch note
        dispatch_note = f"Product dispatched by {dispatched_by}"
        if dispatch_notes:
            dispatch_note += f": {dispatch_notes}"
        
        product.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": dispatched_by,
            "note": dispatch_note
        })
        
        self._save_products()
        return True
    
    def add_product_note(self, sku: str, note: str, user: str) -> bool:
        """Add note to product"""
        product = self.get_product_by_sku(sku)
        if not product:
            return False
        
        product.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "note": note
        })
        
        product.last_modified_date = datetime.now().isoformat()
        self._save_products()
        return True
    
    def get_product_statistics(self) -> Dict[str, Any]:
        """Get product statistics"""
        total = len(self.products)
        
        # Initialize all counts with zeros
        status_counts = {}
        category_counts = {}
        compliance_counts = {}
        
        for status in ProductStatus:
            status_counts[status.value] = 0
        for category in ProductCategory:
            category_counts[category.value] = 0
        
        compliance_counts = {
            "COMPLIANT": 0,
            "NON_COMPLIANT": 0,
            "PENDING": 0
        }
        
        if total > 0:
            # Count by status
            for status in ProductStatus:
                status_counts[status.value] = len(self.get_products_by_status(status))
            
            # Count by category
            for category in ProductCategory:
                category_counts[category.value] = len(self.get_products_by_category(category))
            
            # Count by compliance status
            for product in self.products:
                if product.compliance_status == "COMPLIANT":
                    compliance_counts["COMPLIANT"] += 1
                elif product.compliance_status == "NON_COMPLIANT":
                    compliance_counts["NON_COMPLIANT"] += 1
                else:
                    compliance_counts["PENDING"] += 1
        
        return {
            "total_products": total,
            "by_status": status_counts,
            "by_category": category_counts,
            "by_compliance": compliance_counts,
            "draft_products": status_counts.get("DRAFT", 0),
            "approved_products": status_counts.get("APPROVED", 0),
            "dispatched_products": status_counts.get("DISPATCHED", 0),
            "blocked_products": status_counts.get("BLOCKED", 0)
        }
    
    def search_products(self, query: str) -> List[ProductData]:
        """Search products by name, SKU, or manufacturer"""
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            if (query_lower in product.product_name.lower() or 
                query_lower in product.sku.lower() or
                query_lower in product.manufacturer_name.lower() or
                any(query_lower in tag.lower() for tag in product.tags)):
                results.append(product)
        
        return results

# Global ERP manager instance
erp_manager = ERPManager()
