import re
from typing import Tuple, Dict, Any, Optional
from .schemas import ExtractedFields
from .utils import to_float_safe, find_first

# Enhanced MRP patterns with more variations
MRP_PATTERNS = [
    r'(?:mrp\s*[:=]?\s*₹?\s*([0-9,]+\.?[0-9]*))',
    r'(?:price\s*[:=]?\s*₹?\s*([0-9,]+\.?[0-9]*))',
    r'(?:rs\.?\s*([0-9,]+\.?[0-9]*))',
    r'(?:₹\s*([0-9,]+\.?[0-9]*))',
    r'(?:inr\s*([0-9,]+\.?[0-9]*))',
    r'(?:maximum\s*retail\s*price\s*[:=]?\s*₹?\s*([0-9,]+\.?[0-9]*))',
    r'(?:cost\s*[:=]?\s*₹?\s*([0-9,]+\.?[0-9]*))',
]

# MRP Tax inclusivity patterns - Legal Metrology Rules 2011 compliance
MRP_TAX_INCLUSIVITY_PATTERNS = [
    r'(?:inclusive\s*of\s*all\s*taxes)',
    r'(?:incl\.?\s*of\s*all\s*taxes)',
    r'(?:taxes\s*included)',
    r'(?:all\s*taxes\s*included)',
    r'(?:including\s*all\s*taxes)',
    r'(?:tax\s*inclusive)',
    r'(?:incl\.\s*all\s*taxes)',
]

QTY_PATTERNS = [
    r'net\s*quantity\s*[:=]?\s*([0-9]+\.?[0-9]*)\s*([a-zA-Z]+)',
    r'([0-9]+\.?[0-9]*)\s*(g|kg|ml|l|L|pcs|piece|pack)',
    r'weight\s*[:=]?\s*([0-9]+\.?[0-9]*)\s*([a-zA-Z]+)',
    r'volume\s*[:=]?\s*([0-9]+\.?[0-9]*)\s*([a-zA-Z]+)',
    r'contents\s*[:=]?\s*([0-9]+\.?[0-9]*)\s*([a-zA-Z]+)',
    r'pack\s*of\s*([0-9]+\.?[0-9]*)\s*([a-zA-Z]+)',
]

MFG_PATTERNS = [
    r'(?:mfg\.?\s*date\s*[:=]?\s*([0-9]{2}[\/-][0-9]{2}[\/-][0-9]{2,4}))',
    r'(?:manufacturing\s*date\s*[:=]?\s*([0-9]{2}[\/-][0-9]{2}[\/-][0-9]{2,4}))',
]

EXP_PATTERNS = [
    r'(?:best\s*before\s*[:=]?\s*(.*?)(?:months|month))',
    r'(?:expiry\s*date\s*[:=]?\s*([0-9]{2}[\/-][0-9]{2}[\/-][0-9]{2,4}))',
]

MANUFACTURER_PATTERNS = [
    r'(?:manufactured\s*by\s*[:=]?\s*([\w\s\.&,-]+))',
    r'(?:mfg\.?\s*by\s*[:=]?\s*([\w\s\.&,-]+))',
    r'(?:producer\s*[:=]?\s*([\w\s\.&,-]+))',
    r'(?:brand\s*[:=]?\s*([\w\s\.&,-]+))',
    r'(?:company\s*[:=]?\s*([\w\s\.&,-]+))',
    r'(?:made\s*by\s*[:=]?\s*([\w\s\.&,-]+))',
]

ORIGIN_PATTERNS = [
    r'(?:country\s*of\s*origin\s*[:=]?\s*([\w\s]+))'
]

# Complete manufacturer address patterns - Legal Metrology Rules 2011 compliance
MANUFACTURER_ADDRESS_PATTERNS = [
    r'(?:address\s*[:=]?\s*([^\n]+(?:[\n\r][^\n\r]+)*?)(?=\n\s*\n|$))',
    r'(?:mfg\.?\s*address\s*[:=]?\s*([^\n]+))',
    r'(?:manufacturer\s*address\s*[:=]?\s*([^\n]+))',
    r'(?:packer\s*address\s*[:=]?\s*([^\n]+))',
    r'(?:importer\s*address\s*[:=]?\s*([^\n]+))',
    # Fallback: Extract address after manufacturer name
    r'(?:manufactured\s*by\s*[:=]?\s*[^\n]+\s*address\s*[:=]?\s*([^\n]+))',
]

# PIN code/Postal code patterns for address validation
PIN_CODE_PATTERNS = [
    r'(?:pin\s*[:=]?\s*([0-9]{6}))',
    r'(?:pincode\s*[:=]?\s*([0-9]{6}))',
    r'(?:postal\s*code\s*[:=]?\s*([0-9]{6}))',
    r'(?:-\s*([0-9]{6}))',  # Common format: City - 123456
]

# Consumer care/Customer support patterns - Legal Metrology Rules 2011 compliance
CONSUMER_CARE_PATTERNS = [
    r'(?:consumer\s*care\s*[:=]?\s*([^\n]+))',
    r'(?:customer\s*care\s*[:=]?\s*([^\n]+))',
    r'(?:customer\s*support\s*[:=]?\s*([^\n]+))',
    r'(?:consumer\s*support\s*[:=]?\s*([^\n]+))',
    r'(?:helpline\s*[:=]?\s*([^\n]+))',
    r'(?:toll\s*free\s*[:=]?\s*([^\n]+))',
]

def extract_fields(text: str) -> ExtractedFields:
    """Enhanced field extraction with better pattern matching and validation"""
    # Clean and normalize text
    t = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # Remove extra spaces
    t = re.sub(r'\s+', ' ', t).strip()
    
    fields = ExtractedFields()

    # Extract MRP with enhanced patterns
    mrp_raw = find_first(MRP_PATTERNS, t)
    fields.mrp_raw = mrp_raw
    fields.mrp_value = to_float_safe(mrp_raw)
    
    # Also capture the full MRP context for tax validation
    mrp_context_patterns = [
        r'(mrp\s*[:=]?\s*[^\n]+)',
        r'(price\s*[:=]?\s*[^\n]+)',
        r'(maximum\s*retail\s*price\s*[:=]?\s*[^\n]+)',
    ]
    mrp_full_context = find_first(mrp_context_patterns, t)
    if mrp_full_context:
        fields.extra['mrp_full_context'] = mrp_full_context

    # Extract quantity and unit with improved matching
    qty = find_first(QTY_PATTERNS, t)
    if qty:
        # Try all quantity patterns
        for pattern in QTY_PATTERNS:
            m = re.search(pattern, t, re.IGNORECASE)
            if m:
                fields.net_quantity_raw = m.group(0)
                fields.net_quantity_value = to_float_safe(m.group(1))
                fields.unit = m.group(2).lower() if len(m.groups()) > 1 else None
                break

    # Extract dates with validation
    mfg_date = find_first(MFG_PATTERNS, t)
    fields.mfg_date = validate_date_format(mfg_date)
    
    expiry_date = find_first(EXP_PATTERNS, t)
    fields.expiry_date = validate_date_format(expiry_date)

    # Extract manufacturer with cleaning
    manufacturer = find_first(MANUFACTURER_PATTERNS, t)
    fields.manufacturer_name = clean_manufacturer_name(manufacturer)

    # Extract country of origin
    origin = find_first(ORIGIN_PATTERNS, t)
    fields.country_of_origin = origin.strip() if origin else None

    # Extract complete manufacturer address - Legal Metrology requirement
    manufacturer_address = find_first(MANUFACTURER_ADDRESS_PATTERNS, t)
    if manufacturer_address:
        fields.extra['manufacturer_address'] = clean_address(manufacturer_address)
    
    # Extract PIN code from address
    pin_code = find_first(PIN_CODE_PATTERNS, t)
    if pin_code:
        fields.extra['pin_code'] = pin_code.strip()
    
    # Extract consumer care details - Legal Metrology requirement
    consumer_care = find_first(CONSUMER_CARE_PATTERNS, t)
    if consumer_care:
        fields.extra['consumer_care'] = clean_consumer_care(consumer_care)
    
    # Extract MRP tax inclusivity declaration
    mrp_tax_text = find_first(MRP_TAX_INCLUSIVITY_PATTERNS, t)
    if mrp_tax_text:
        fields.extra['mrp_tax_inclusive'] = mrp_tax_text.strip()
    else:
        # Check if tax inclusivity is mentioned in MRP context
        mrp_context = fields.extra.get('mrp_full_context', '')
        if mrp_context:
            for pattern in MRP_TAX_INCLUSIVITY_PATTERNS:
                if re.search(pattern, mrp_context, re.IGNORECASE):
                    match = re.search(pattern, mrp_context, re.IGNORECASE)
                    if match:
                        fields.extra['mrp_tax_inclusive'] = match.group(0).strip()
                        break

    # Extract additional fields if available
    extract_additional_fields(t, fields)
    
    # Set additional schema fields
    fields.batch_number = fields.extra.get('batch_number')
    fields.fssai_number = fields.extra.get('fssai_number')
    fields.contact_number = fields.extra.get('contact_number')
    
    # Set Legal Metrology compliance fields
    fields.manufacturer_address = fields.extra.get('manufacturer_address')
    fields.consumer_care = fields.extra.get('consumer_care')
    fields.pin_code = fields.extra.get('pin_code')
    
    # Calculate and set confidence
    fields.extraction_confidence = fields.calculate_confidence()
    
    return fields

def validate_date_format(date_str: Optional[str]) -> Optional[str]:
    """Validate and clean date format"""
    if not date_str:
        return None
    
    # Basic date validation - should be in DD/MM/YYYY or DD-MM-YYYY format
    if re.match(r'\d{2}[/-]\d{2}[/-]\d{2,4}', date_str):
        return date_str
    return None

def clean_manufacturer_name(name: Optional[str]) -> Optional[str]:
    """Clean and validate manufacturer name"""
    if not name:
        return None
    
    # Remove common suffixes and clean up
    name = re.sub(r'\s*(ltd|limited|inc|corporation|corp|co\.|company)\s*$', '', name, flags=re.IGNORECASE)
    name = name.strip()
    
    # Basic validation - should have at least 2 characters
    if len(name) >= 2:
        return name
    return None

def clean_address(address: Optional[str]) -> Optional[str]:
    """Clean and validate manufacturer address"""
    if not address:
        return None
    
    # Remove extra whitespace and normalize
    address = re.sub(r'\s+', ' ', address.strip())
    
    # Basic validation - should have minimum length for complete address
    if len(address) >= 20:  # Minimum reasonable address length
        return address
    return None

def clean_consumer_care(care_info: Optional[str]) -> Optional[str]:
    """Clean and validate consumer care information"""
    if not care_info:
        return None
    
    # Remove extra whitespace and normalize
    care_info = re.sub(r'\s+', ' ', care_info.strip())
    
    # Basic validation - should contain contact info
    if len(care_info) >= 10:  # Minimum reasonable contact info length
        return care_info
    return None

def validate_pin_code(pin_code: Optional[str]) -> bool:
    """Validate Indian PIN code format"""
    if not pin_code:
        return False
    
    # Indian PIN codes are 6 digits
    return bool(re.match(r'^[0-9]{6}$', pin_code.strip()))

def extract_additional_fields(text: str, fields: ExtractedFields) -> None:
    """Extract additional fields that might be useful"""
    
    # Extract batch number if present
    batch_patterns = [
        r'batch\s*[:=]?\s*([A-Za-z0-9\-]+)',
        r'lot\s*[:=]?\s*([A-Za-z0-9\-]+)',
    ]
    batch = find_first(batch_patterns, text)
    if batch:
        fields.extra['batch_number'] = batch
    
    # Extract FSSAI number if present
    fssai_patterns = [
        r'fssai\s*[:=]?\s*([0-9]{14})',
        r'license\s*no\.?\s*[:=]?\s*([0-9]{14})',
    ]
    fssai = find_first(fssai_patterns, text)
    if fssai:
        fields.extra['fssai_number'] = fssai
    
    # Extract contact information (enhanced patterns)
    contact_patterns = [
        r'contact\s*[:=]?\s*([0-9+\-\(\)\s]+)',
        r'phone\s*[:=]?\s*([0-9+\-\(\)\s]+)',
        r'mobile\s*[:=]?\s*([0-9+\-\(\)\s]+)',
        r'tel\s*[:=]?\s*([0-9+\-\(\)\s]+)',
        r'([0-9]{4}[\-\s][0-9]{3}[\-\s][0-9]{4})',  # Common Indian phone format
        r'(1800[\-\s]?[0-9]{3}[\-\s]?[0-9]{4})',   # Toll-free numbers
    ]
    contact = find_first(contact_patterns, text)
    if contact:
        fields.extra['contact_number'] = contact.strip()
    
    # Extract email addresses for consumer care
    email_patterns = [
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    ]
    email = find_first(email_patterns, text)
    if email:
        fields.extra['email'] = email.strip().lower()
