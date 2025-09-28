from typing import List, Dict, Any, Tuple
import yaml
import re
from .schemas import ExtractedFields, ValidationIssue, ValidationResult

def load_rules(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def validate(fields: ExtractedFields, rules: Dict[str, Any], ocr_boxes=None) -> ValidationResult:
    issues: List[ValidationIssue] = []
    required = rules.get('required_fields', [])
    validators = rules.get('validators', {})

    # Required fields present - Legal Metrology Rules 2011 compliance
    present_map = {
        'mrp': bool(fields.mrp_value),
        'net_quantity': bool(fields.net_quantity_value),
        'unit': bool(fields.unit),
        'manufacturer_name': bool(fields.manufacturer_name),
        'manufacturer_address': bool(fields.manufacturer_address),
        'consumer_care': bool(fields.consumer_care),
        'country_of_origin': bool(fields.country_of_origin),
    }
    for k in required:
        if not present_map.get(k, False):
            issues.append(ValidationIssue(field=k, level='ERROR', message=f"Missing required field: {k}"))

    # MRP checks - Enhanced for Legal Metrology compliance
    mrp_rules = validators.get('mrp', {})
    if fields.mrp_value is not None:
        mn = mrp_rules.get('min_value')
        mx = mrp_rules.get('max_value')
        if mn is not None and fields.mrp_value < mn:
            issues.append(ValidationIssue(field='mrp', level='ERROR', message=f"MRP too low (< {mn})"))
        if mx is not None and fields.mrp_value > mx:
            issues.append(ValidationIssue(field='mrp', level='ERROR', message=f"MRP too high (> {mx})"))
        
        # Currency symbol validation
        syms = mrp_rules.get('must_include_symbol', [])
        mrp_text = fields.extra.get('mrp_full_context', '') or fields.mrp_raw or ''
        if syms and not any(s.lower() in mrp_text.lower() for s in syms):
            issues.append(ValidationIssue(field='mrp', level='ERROR', message=f"MRP must include currency symbol ({', '.join(syms)}) - Legal Metrology Rule 6"))
        
        # Tax inclusivity validation - Legal Metrology requirement
        tax_texts = mrp_rules.get('must_include_tax_text', [])
        # Check multiple sources for tax inclusivity text
        mrp_contexts = [
            fields.extra.get('mrp_tax_inclusive', ''),
            fields.extra.get('mrp_full_context', ''),
            fields.mrp_raw or ''
        ]
        
        has_tax_text = False
        for context in mrp_contexts:
            if context and any(tax_text.lower() in context.lower() for tax_text in tax_texts):
                has_tax_text = True
                break
        
        if tax_texts and not has_tax_text:
            issues.append(ValidationIssue(
                field='mrp', 
                level='ERROR', 
                message=f"MRP must explicitly state tax inclusivity (e.g., 'inclusive of all taxes') - Legal Metrology Rule 6"
            ))

    # Unit checks
    unit_rules = validators.get('unit', {})
    allowed = [u.lower() for u in unit_rules.get('allowed', [])]
    if fields.unit and allowed and fields.unit.lower() not in allowed:
        issues.append(ValidationIssue(field='unit', level='ERROR', message=f"Unit '{fields.unit}' not in allowed list: {allowed}"))

    # Quantity checks
    qty_rules = validators.get('net_quantity', {})
    if fields.net_quantity_value is not None:
        mnq = qty_rules.get('min_value')
        if mnq is not None and fields.net_quantity_value < mnq:
            issues.append(ValidationIssue(field='net_quantity', level='ERROR', message=f"Net quantity too low (< {mnq})"))

    # Dates checks
    dates_rules = validators.get('dates', {})
    must_have = dates_rules.get('must_have', [])
    if 'mfg_date' in must_have and not fields.mfg_date:
        issues.append(ValidationIssue(field='mfg_date', level='ERROR', message=f"Manufacturing date missing - Legal Metrology requirement"))
    
    # Manufacturer address validation - Legal Metrology Rule 7
    address_rules = validators.get('manufacturer_address', {})
    if address_rules.get('required', False):
        if not fields.manufacturer_address:
            issues.append(ValidationIssue(
                field='manufacturer_address', 
                level='ERROR', 
                message="Complete manufacturer address required - Legal Metrology Rule 7"
            ))
        elif fields.manufacturer_address:
            min_len = address_rules.get('min_length', 20)
            if len(fields.manufacturer_address) < min_len:
                issues.append(ValidationIssue(
                    field='manufacturer_address', 
                    level='ERROR', 
                    message=f"Manufacturer address too short (< {min_len} characters) - must include complete postal address"
                ))
            
            # PIN code validation
            if address_rules.get('must_include_pin', False):
                pin_pattern = address_rules.get('validation_pattern', r'.*[0-9]{6}.*')
                if not re.search(pin_pattern, fields.manufacturer_address):
                    issues.append(ValidationIssue(
                        field='manufacturer_address', 
                        level='ERROR', 
                        message="Manufacturer address must include valid PIN code - Legal Metrology Rule 7"
                    ))
    
    # Consumer care validation - Consumer Protection Act requirement
    care_rules = validators.get('consumer_care', {})
    if care_rules.get('required', False):
        if not fields.consumer_care:
            issues.append(ValidationIssue(
                field='consumer_care', 
                level='ERROR', 
                message="Consumer care details required - Consumer Protection Act 2019"
            ))
        elif fields.consumer_care:
            min_len = care_rules.get('min_length', 10)
            if len(fields.consumer_care) < min_len:
                issues.append(ValidationIssue(
                    field='consumer_care', 
                    level='ERROR', 
                    message=f"Consumer care details too brief (< {min_len} characters) - must include contact information"
                ))
            
            # Contact information validation
            if care_rules.get('must_include_contact', False):
                contact_patterns = care_rules.get('contact_patterns', [])
                has_contact = any(re.search(pattern, fields.consumer_care) for pattern in contact_patterns)
                if not has_contact:
                    issues.append(ValidationIssue(
                        field='consumer_care', 
                        level='ERROR', 
                        message="Consumer care must include valid contact information (phone/email)"
                    ))
    
    # PIN code format validation
    pin_rules = validators.get('pin_code', {})
    if pin_rules.get('required', False) and fields.pin_code:
        pin_pattern = pin_rules.get('pattern', r'^[0-9]{6}$')
        if not re.match(pin_pattern, fields.pin_code):
            issues.append(ValidationIssue(
                field='pin_code', 
                level='ERROR', 
                message="Invalid PIN code format - must be 6 digits"
            ))

    # Font size (heuristic) using OCR boxes
    if ocr_boxes is not None:
        # compute simple average height heuristic
        if ocr_boxes:
            avg_h = sum([b[1][3] for b in ocr_boxes]) / len(ocr_boxes)
            min_pt = validators.get('font_size', {}).get('min_pt', 1)
            if avg_h < min_pt:
                issues.append(ValidationIssue(field='font_size', level='WARN', message=f"Detected small text height (avg {avg_h:.1f}px)."))
        else:
            issues.append(ValidationIssue(field='font_size', level='INFO', message="No OCR boxes available to estimate font size."))

    # Compute a simple score (100 - 20 per ERROR - 5 per WARN; floor at 0, cap 100)
    score = 100
    for it in issues:
        if it.level == 'ERROR':
            score -= 20
        elif it.level == 'WARN':
            score -= 5
    score = max(0, min(100, score))

    is_compliant = not any(it.level == 'ERROR' for it in issues)
    return ValidationResult(is_compliant=is_compliant, issues=issues, score=score)
