"""
Regulatory Update Module
Manages dynamic rule updates for Legal Metrology compliance
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from .json_utils import safe_json_dump, safe_json_dumps

class RuleStatus(Enum):
    """Rule status enumeration"""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    SUSPENDED = "SUSPENDED"

class RuleType(Enum):
    """Rule type enumeration"""
    MRP_REGULATION = "MRP_REGULATION"
    QUANTITY_MEASUREMENT = "QUANTITY_MEASUREMENT"
    MANUFACTURER_INFO = "MANUFACTURER_INFO"
    DATE_FORMAT = "DATE_FORMAT"
    LABELING_REQUIREMENT = "LABELING_REQUIREMENT"
    COMPLIANCE_THRESHOLD = "COMPLIANCE_THRESHOLD"
    NEW_FIELD_REQUIREMENT = "NEW_FIELD_REQUIREMENT"

class UpdatePriority(Enum):
    """Update priority enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class RegulatoryRule:
    """Regulatory rule definition"""
    rule_id: str
    rule_name: str
    rule_type: RuleType
    description: str
    status: RuleStatus
    priority: UpdatePriority
    effective_date: str
    created_by: str
    created_date: str
    approved_by: Optional[str] = None
    approved_date: Optional[str] = None
    
    # Rule definition
    rule_definition: Dict[str, Any] = None
    validation_pattern: Optional[str] = None
    error_message: Optional[str] = None
    warning_threshold: Optional[float] = None
    
    # Impact assessment
    affected_products: List[str] = None
    impact_assessment: Optional[str] = None
    migration_required: bool = False
    migration_plan: Optional[str] = None
    
    # Metadata
    version: int = 1
    notes: List[Dict[str, str]] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.rule_definition is None:
            self.rule_definition = {}
        if self.affected_products is None:
            self.affected_products = []
        if self.notes is None:
            self.notes = []
        if self.tags is None:
            self.tags = []

@dataclass
class RegulatoryUpdate:
    """Regulatory update tracking"""
    update_id: str
    update_title: str
    description: str
    source: str  # "GOVERNMENT", "INTERNAL", "COMPLIANCE_REVIEW", "NON_COMPLIANCE_FEEDBACK"
    priority: UpdatePriority
    status: RuleStatus
    created_by: str
    created_date: str
    effective_date: str
    
    # Update details
    rules_affected: List[str] = None  # Rule IDs
    new_rules: List[RegulatoryRule] = None
    modified_rules: List[RegulatoryRule] = None
    
    # Impact analysis
    products_impacted: int = 0
    compliance_issues_expected: int = 0
    estimated_resolution_time: Optional[str] = None
    
    # Approval workflow
    approved_by: Optional[str] = None
    approved_date: Optional[str] = None
    implementation_date: Optional[str] = None
    
    # Metadata
    notes: List[Dict[str, str]] = None
    attachments: List[str] = None
    
    def __post_init__(self):
        if self.rules_affected is None:
            self.rules_affected = []
        if self.new_rules is None:
            self.new_rules = []
        if self.modified_rules is None:
            self.modified_rules = []
        if self.notes is None:
            self.notes = []
        if self.attachments is None:
            self.attachments = []

class RegulatoryManager:
    """Manages regulatory rules and updates"""
    
    def __init__(self):
        self.rules_file = Path("app/data/regulatory_rules.json")
        self.updates_file = Path("app/data/regulatory_updates.json")
        
        # Create directories if they don't exist
        for file_path in [self.rules_file, self.updates_file]:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.rules = self._load_rules()
        self.updates = self._load_updates()
        
        # Initialize default rules if none exist
        if not self.rules:
            self._initialize_default_rules()
    
    def _load_rules(self) -> List[RegulatoryRule]:
        """Load regulatory rules from file"""
        if not self.rules_file.exists():
            return []
        
        try:
            with open(self.rules_file, 'r') as f:
                data = json.load(f)
                rules = []
                for item in data:
                    # Convert enum values back to enum objects
                    item['rule_type'] = RuleType(item['rule_type'])
                    item['status'] = RuleStatus(item['status'])
                    item['priority'] = UpdatePriority(item['priority'])
                    rules.append(RegulatoryRule(**item))
                return rules
        except Exception as e:
            print(f"Error loading regulatory rules: {e}")
            return []
    
    def _load_updates(self) -> List[RegulatoryUpdate]:
        """Load regulatory updates from file"""
        if not self.updates_file.exists():
            return []
        
        try:
            with open(self.updates_file, 'r') as f:
                data = json.load(f)
                updates = []
                for item in data:
                    # Convert enum values back to enum objects
                    item['priority'] = UpdatePriority(item['priority'])
                    item['status'] = RuleStatus(item['status'])
                    
                    # Convert new_rules and modified_rules
                    new_rules = []
                    for rule_data in item.get('new_rules', []):
                        rule_data['rule_type'] = RuleType(rule_data['rule_type'])
                        rule_data['status'] = RuleStatus(rule_data['status'])
                        rule_data['priority'] = UpdatePriority(rule_data['priority'])
                        new_rules.append(RegulatoryRule(**rule_data))
                    item['new_rules'] = new_rules
                    
                    modified_rules = []
                    for rule_data in item.get('modified_rules', []):
                        rule_data['rule_type'] = RuleType(rule_data['rule_type'])
                        rule_data['status'] = RuleStatus(rule_data['status'])
                        rule_data['priority'] = UpdatePriority(rule_data['priority'])
                        modified_rules.append(RegulatoryRule(**rule_data))
                    item['modified_rules'] = modified_rules
                    
                    updates.append(RegulatoryUpdate(**item))
                return updates
        except Exception as e:
            print(f"Error loading regulatory updates: {e}")
            return []
    
    def _save_rules(self):
        """Save regulatory rules to file"""
        try:
            # Convert rules to dictionaries
            data = []
            for rule in self.rules:
                rule_dict = asdict(rule)
                # Convert enums to string values
                rule_dict['rule_type'] = rule.rule_type.value
                rule_dict['status'] = rule.status.value
                rule_dict['priority'] = rule.priority.value
                data.append(rule_dict)
            
            with open(self.rules_file, 'w') as f:
                safe_json_dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving regulatory rules: {e}")
    
    def _save_updates(self):
        """Save regulatory updates to file"""
        try:
            # Convert updates to dictionaries
            data = []
            for update in self.updates:
                update_dict = asdict(update)
                # Convert enums to string values
                update_dict['priority'] = update.priority.value
                update_dict['status'] = update.status.value
                
                # Convert new_rules and modified_rules
                new_rules_data = []
                for rule in update.new_rules:
                    rule_dict = asdict(rule)
                    rule_dict['rule_type'] = rule.rule_type.value
                    rule_dict['status'] = rule.status.value
                    rule_dict['priority'] = rule.priority.value
                    new_rules_data.append(rule_dict)
                update_dict['new_rules'] = new_rules_data
                
                modified_rules_data = []
                for rule in update.modified_rules:
                    rule_dict = asdict(rule)
                    rule_dict['rule_type'] = rule.rule_type.value
                    rule_dict['status'] = rule.status.value
                    rule_dict['priority'] = rule.priority.value
                    modified_rules_data.append(rule_dict)
                update_dict['modified_rules'] = modified_rules_data
                
                data.append(update_dict)
            
            with open(self.updates_file, 'w') as f:
                safe_json_dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving regulatory updates: {e}")
    
    def _initialize_default_rules(self):
        """Initialize default Legal Metrology rules"""
        default_rules = [
            RegulatoryRule(
                rule_id="LM001",
                rule_name="MRP Display Requirement",
                rule_type=RuleType.MRP_REGULATION,
                description="Maximum Retail Price must be prominently displayed on product packaging",
                status=RuleStatus.ACTIVE,
                priority=UpdatePriority.HIGH,
                effective_date="2024-01-01",
                created_by="system",
                created_date=datetime.now().isoformat(),
                rule_definition={
                    "field": "mrp",
                    "required": True,
                    "min_value": 0.01,
                    "format": "currency",
                    "display_requirement": True
                },
                validation_pattern=r"^\d+(\.\d{2})?$",
                error_message="MRP must be a valid currency amount"
            ),
            RegulatoryRule(
                rule_id="LM002",
                rule_name="Net Quantity Declaration",
                rule_type=RuleType.QUANTITY_MEASUREMENT,
                description="Net quantity must be clearly declared with appropriate unit",
                status=RuleStatus.ACTIVE,
                priority=UpdatePriority.HIGH,
                effective_date="2024-01-01",
                created_by="system",
                created_date=datetime.now().isoformat(),
                rule_definition={
                    "field": "net_quantity",
                    "required": True,
                    "min_value": 0.01,
                    "units_allowed": ["g", "kg", "ml", "l", "L", "pcs", "piece", "pack", "gm", "mg"],
                    "display_requirement": True
                },
                validation_pattern=r"^\d+(\.\d+)?\s*(g|kg|ml|l|L|pcs|piece|pack|gm|mg)$",
                error_message="Net quantity must include valid unit of measurement"
            ),
            RegulatoryRule(
                rule_id="LM003",
                rule_name="Manufacturer Information",
                rule_type=RuleType.MANUFACTURER_INFO,
                description="Manufacturer name and address must be provided",
                status=RuleStatus.ACTIVE,
                priority=UpdatePriority.MEDIUM,
                effective_date="2024-01-01",
                created_by="system",
                created_date=datetime.now().isoformat(),
                rule_definition={
                    "field": "manufacturer_name",
                    "required": True,
                    "min_length": 2,
                    "display_requirement": True
                },
                validation_pattern=r"^[a-zA-Z\s&.,]+$",
                error_message="Manufacturer name must contain valid characters"
            ),
            RegulatoryRule(
                rule_id="LM004",
                rule_name="Date Format Standardization",
                rule_type=RuleType.DATE_FORMAT,
                description="Manufacturing and expiry dates must follow standard format",
                status=RuleStatus.ACTIVE,
                priority=UpdatePriority.MEDIUM,
                effective_date="2024-01-01",
                created_by="system",
                created_date=datetime.now().isoformat(),
                rule_definition={
                    "field": "mfg_date",
                    "format": "DD/MM/YYYY",
                    "required": False,
                    "validation_required": True
                },
                validation_pattern=r"^\d{2}/\d{2}/\d{4}$",
                error_message="Date must be in DD/MM/YYYY format"
            )
        ]
        
        self.rules.extend(default_rules)
        self._save_rules()
    
    def generate_rule_id(self, rule_type: RuleType) -> str:
        """Generate unique rule ID"""
        type_prefix = rule_type.value[:3].upper()
        count = len([r for r in self.rules if r.rule_id.startswith(type_prefix)])
        return f"{type_prefix}{count + 1:03d}"
    
    def generate_update_id(self) -> str:
        """Generate unique update ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        count = len([u for u in self.updates if u.update_id.startswith(f"UPDATE-{timestamp}")])
        return f"UPDATE-{timestamp}-{count:03d}"
    
    def add_regulatory_rule(self, rule_name: str, rule_type: RuleType, description: str,
                           priority: UpdatePriority, effective_date: str, created_by: str,
                           rule_definition: Dict[str, Any], **kwargs) -> RegulatoryRule:
        """Add new regulatory rule"""
        
        rule_id = self.generate_rule_id(rule_type)
        
        rule = RegulatoryRule(
            rule_id=rule_id,
            rule_name=rule_name,
            rule_type=rule_type,
            description=description,
            status=RuleStatus.DRAFT,
            priority=priority,
            effective_date=effective_date,
            created_by=created_by,
            created_date=datetime.now().isoformat(),
            rule_definition=rule_definition,
            validation_pattern=kwargs.get('validation_pattern'),
            error_message=kwargs.get('error_message'),
            warning_threshold=kwargs.get('warning_threshold'),
            tags=kwargs.get('tags', [])
        )
        
        self.rules.append(rule)
        self._save_rules()
        
        return rule
    
    def create_regulatory_update(self, update_title: str, description: str, source: str,
                                priority: UpdatePriority, effective_date: str, created_by: str,
                                new_rules: List[RegulatoryRule] = None,
                                modified_rules: List[RegulatoryRule] = None) -> RegulatoryUpdate:
        """Create new regulatory update"""
        
        update_id = self.generate_update_id()
        
        update = RegulatoryUpdate(
            update_id=update_id,
            update_title=update_title,
            description=description,
            source=source,
            priority=priority,
            status=RuleStatus.DRAFT,
            created_by=created_by,
            created_date=datetime.now().isoformat(),
            effective_date=effective_date,
            new_rules=new_rules or [],
            modified_rules=modified_rules or [],
            rules_affected=[r.rule_id for r in (new_rules or []) + (modified_rules or [])]
        )
        
        self.updates.append(update)
        self._save_updates()
        
        return update
    
    def get_active_rules(self) -> List[RegulatoryRule]:
        """Get all active regulatory rules"""
        return [rule for rule in self.rules if rule.status == RuleStatus.ACTIVE]
    
    def get_rules_by_type(self, rule_type: RuleType) -> List[RegulatoryRule]:
        """Get rules by type"""
        return [rule for rule in self.rules if rule.rule_type == rule_type]
    
    def get_rule(self, rule_id: str) -> Optional[RegulatoryRule]:
        """Get rule by ID"""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None
    
    def get_update(self, update_id: str) -> Optional[RegulatoryUpdate]:
        """Get update by ID"""
        for update in self.updates:
            if update.update_id == update_id:
                return update
        return None
    
    def approve_rule(self, rule_id: str, approved_by: str, notes: str = None) -> bool:
        """Approve a regulatory rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return False
        
        rule.status = RuleStatus.ACTIVE
        rule.approved_by = approved_by
        rule.approved_date = datetime.now().isoformat()
        rule.version += 1
        
        # Add approval note
        approval_note = f"Rule approved by {approved_by}"
        if notes:
            approval_note += f": {notes}"
        
        rule.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": approved_by,
            "note": approval_note
        })
        
        self._save_rules()
        return True
    
    def approve_update(self, update_id: str, approved_by: str, notes: str = None) -> bool:
        """Approve a regulatory update"""
        update = self.get_update(update_id)
        if not update:
            return False
        
        update.status = RuleStatus.ACTIVE
        update.approved_by = approved_by
        update.approved_date = datetime.now().isoformat()
        update.implementation_date = datetime.now().isoformat()
        
        # Approve all associated rules
        for rule in update.new_rules + update.modified_rules:
            rule.status = RuleStatus.ACTIVE
            rule.approved_by = approved_by
            rule.approved_date = datetime.now().isoformat()
            rule.version += 1
        
        # Add approval note
        approval_note = f"Regulatory update approved by {approved_by}"
        if notes:
            approval_note += f": {notes}"
        
        update.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": approved_by,
            "note": approval_note
        })
        
        self._save_updates()
        self._save_rules()
        return True
    
    def deprecate_rule(self, rule_id: str, deprecated_by: str, reason: str) -> bool:
        """Deprecate a regulatory rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return False
        
        rule.status = RuleStatus.DEPRECATED
        rule.version += 1
        
        # Add deprecation note
        rule.notes.append({
            "timestamp": datetime.now().isoformat(),
            "user": deprecated_by,
            "note": f"Rule deprecated: {reason}"
        })
        
        self._save_rules()
        return True
    
    def get_regulatory_statistics(self) -> Dict[str, Any]:
        """Get regulatory management statistics"""
        
        # Rule statistics
        total_rules = len(self.rules)
        active_rules = len(self.get_active_rules())
        
        rule_status_counts = {}
        for status in RuleStatus:
            rule_status_counts[status.value] = len([r for r in self.rules if r.status == status])
        
        rule_type_counts = {}
        for rule_type in RuleType:
            rule_type_counts[rule_type.value] = len(self.get_rules_by_type(rule_type))
        
        # Update statistics
        total_updates = len(self.updates)
        
        update_status_counts = {}
        for status in RuleStatus:
            update_status_counts[status.value] = len([u for u in self.updates if u.status == status])
        
        priority_counts = {}
        for priority in UpdatePriority:
            priority_counts[priority.value] = len([u for u in self.updates if u.priority == priority])
        
        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "total_updates": total_updates,
            "rules_by_status": rule_status_counts,
            "rules_by_type": rule_type_counts,
            "updates_by_status": update_status_counts,
            "updates_by_priority": priority_counts,
            "pending_rules": rule_status_counts.get("DRAFT", 0) + rule_status_counts.get("PENDING_APPROVAL", 0),
            "pending_updates": update_status_counts.get("DRAFT", 0) + update_status_counts.get("PENDING_APPROVAL", 0)
        }

# Global regulatory manager instance
regulatory_manager = RegulatoryManager()
