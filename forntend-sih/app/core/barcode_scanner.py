"""
Barcode Scanner Integration for Legal Metrology Compliance Checker
Supports multiple barcode APIs and formats for product information extraction
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class BarcodeData:
    """Structured barcode data"""
    barcode: str
    format: str
    product_name: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = None
    nutrition_facts: Optional[Dict] = None
    ingredients: Optional[List[str]] = None
    net_weight: Optional[str] = None
    country_of_origin: Optional[str] = None
    source_api: Optional[str] = None
    confidence: float = 0.0
    raw_data: Optional[Dict] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.ingredients is None:
            self.ingredients = []

class BarcodeScanner:
    """Comprehensive barcode scanning service with multiple API integrations"""
    
    def __init__(self):
        """Initialize barcode scanner with multiple API options"""
        self.apis = {
            'openfoodfacts': {
                'name': 'Open Food Facts',
                'url': 'https://world.openfoodfacts.org/api/v0/product/{barcode}.json',
                'free': True,
                'description': 'Comprehensive food product database'
            },
            'upcitemdb': {
                'name': 'UPC Item DB',
                'url': 'https://api.upcitemdb.com/prod/trial/lookup',
                'free': True,
                'description': 'General product database (trial version)'
            },
            'barcode_lookup': {
                'name': 'Barcode Lookup',
                'url': 'https://api.barcodelookup.com/v3/products',
                'free': False,
                'description': 'Premium barcode API (requires API key)'
            }
        }
        
        # Load API keys from environment or Streamlit secrets
        self.api_keys = self._load_api_keys()
        
        logger.info("BarcodeScanner initialized with multiple API options")
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables or Streamlit secrets"""
        keys = {}
        
        # Try to load from Streamlit secrets first
        try:
            if hasattr(st, 'secrets') and hasattr(st.secrets, 'barcode_apis'):
                keys['barcode_lookup'] = st.secrets.barcode_apis.get('BARCODE_LOOKUP_API_KEY', '')
                keys['upcitemdb'] = st.secrets.barcode_apis.get('UPCITEMDB_API_KEY', '')
        except Exception as e:
            logger.debug(f"Could not load from Streamlit secrets: {e}")
            pass
        
        # Fallback to environment variables
        import os
        keys['barcode_lookup'] = keys.get('barcode_lookup') or os.getenv('BARCODE_LOOKUP_API_KEY', '')
        keys['upcitemdb'] = keys.get('upcitemdb') or os.getenv('UPCITEMDB_API_KEY', '')
        
        return keys
    
    def scan_barcode_from_image(self, image: Image.Image) -> List[str]:
        """Extract barcode numbers from image using OpenCV and pyzbar with enhanced preprocessing"""
        try:
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Try multiple barcode detection methods with different preprocessing
            barcodes = []
            
            # Method 1: Try pyzbar on original image (most reliable)
            try:
                from pyzbar import pyzbar
                decoded_objects = pyzbar.decode(opencv_image)
                for obj in decoded_objects:
                    barcode_data = obj.data.decode('utf-8')
                    if barcode_data not in barcodes:
                        barcodes.append(barcode_data)
                        logger.info(f"Detected barcode: {barcode_data} (format: {obj.type})")
            except ImportError:
                logger.warning("pyzbar not available, trying alternative methods")
            
            # Method 2: Try with image preprocessing if no barcodes found
            if not barcodes:
                preprocessed_images = self._preprocess_image_for_barcode(opencv_image)
                
                for i, processed_img in enumerate(preprocessed_images):
                    try:
                        from pyzbar import pyzbar
                        decoded_objects = pyzbar.decode(processed_img)
                        for obj in decoded_objects:
                            barcode_data = obj.data.decode('utf-8')
                            if barcode_data not in barcodes:
                                barcodes.append(barcode_data)
                                logger.info(f"Detected barcode with preprocessing {i}: {barcode_data} (format: {obj.type})")
                    except ImportError:
                        pass
            
            # Method 3: Try OpenCV barcode detector (if pyzbar failed)
            if not barcodes:
                try:
                    detector = cv2.barcode.BarcodeDetector()
                    retval, decoded_info, decoded_type, points = detector.detectAndDecode(opencv_image)
                    if retval:
                        for info in decoded_info:
                            if info and info not in barcodes:
                                barcodes.append(info)
                                logger.info(f"OpenCV detected barcode: {info}")
                except:
                    logger.warning("OpenCV barcode detection failed")
            
            # Remove duplicates while preserving order
            unique_barcodes = []
            for barcode in barcodes:
                if barcode not in unique_barcodes:
                    unique_barcodes.append(barcode)
            
            return unique_barcodes
            
        except Exception as e:
            logger.error(f"Error scanning barcode from image: {e}")
            return []
    
    def scan_barcode_with_visualization(self, image: Image.Image) -> Tuple[List[str], Optional[Image.Image]]:
        """Extract barcodes and return annotated image showing detected regions"""
        try:
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            annotated_image = opencv_image.copy()
            
            barcodes = []
            
            # Try pyzbar with visualization
            try:
                from pyzbar import pyzbar
                decoded_objects = pyzbar.decode(opencv_image)
                
                for obj in decoded_objects:
                    barcode_data = obj.data.decode('utf-8')
                    if barcode_data not in barcodes:
                        barcodes.append(barcode_data)
                        
                        # Draw bounding box around detected barcode
                        points = obj.polygon
                        if len(points) > 4:
                            # Convert to rectangle if polygon has more than 4 points
                            rect = cv2.boundingRect(np.array(points, dtype=np.int32))
                            points = [
                                (rect[0], rect[1]),
                                (rect[0] + rect[2], rect[1]),
                                (rect[0] + rect[2], rect[1] + rect[3]),
                                (rect[0], rect[1] + rect[3])
                            ]
                        
                        # Draw the bounding box
                        pts = np.array(points, dtype=np.int32)
                        cv2.polylines(annotated_image, [pts], True, (0, 255, 0), 3)
                        
                        # Add label
                        x, y = points[0]
                        cv2.putText(annotated_image, f"{barcode_data}", (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        logger.info(f"Detected and annotated barcode: {barcode_data}")
                        
            except ImportError:
                logger.warning("pyzbar not available for visualization")
                # Fallback to basic detection
                barcodes = self.scan_barcode_from_image(image)
            
            # Convert back to PIL Image
            if len(barcodes) > 0:
                annotated_pil = Image.fromarray(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
                return barcodes, annotated_pil
            else:
                return barcodes, None
                
        except Exception as e:
            logger.error(f"Error in barcode visualization: {e}")
            # Fallback to regular detection
            return self.scan_barcode_from_image(image), None
    
    def _preprocess_image_for_barcode(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply various preprocessing techniques to improve barcode detection"""
        preprocessed_images = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 1. Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            preprocessed_images.append(blurred)
            
            # 2. Adaptive thresholding
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            preprocessed_images.append(adaptive_thresh)
            
            # 3. Otsu's thresholding
            _, otsu_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            preprocessed_images.append(otsu_thresh)
            
            # 4. Morphological operations to clean up the image
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
            preprocessed_images.append(morph)
            
            # 5. Edge detection and dilation (for damaged barcodes)
            edges = cv2.Canny(gray, 50, 150)
            dilated = cv2.dilate(edges, kernel, iterations=1)
            preprocessed_images.append(dilated)
            
            # 6. Contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            preprocessed_images.append(enhanced)
            
            # 7. Try different rotations for skewed barcodes
            for angle in [-5, 5, -10, 10]:
                rows, cols = gray.shape
                rotation_matrix = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
                rotated = cv2.warpAffine(gray, rotation_matrix, (cols, rows))
                preprocessed_images.append(rotated)
            
        except Exception as e:
            logger.warning(f"Error in image preprocessing: {e}")
        
        return preprocessed_images
    
    def lookup_barcode(self, barcode: str, preferred_api: str = 'auto') -> Optional[BarcodeData]:
        """Look up barcode information using multiple APIs"""
        
        if preferred_api == 'auto':
            # Try APIs in order of preference (free first, then paid)
            # Only include paid APIs if API keys are available
            api_order = ['openfoodfacts', 'upcitemdb']
            if self.api_keys.get('barcode_lookup'):
                api_order.append('barcode_lookup')
        else:
            api_order = [preferred_api] if preferred_api in self.apis else ['openfoodfacts']
        
        for api_name in api_order:
            try:
                # Skip paid APIs if no API key is available
                if api_name == 'barcode_lookup' and not self.api_keys.get('barcode_lookup'):
                    logger.info(f"Skipping {api_name} - no API key configured")
                    continue
                    
                result = self._lookup_single_api(barcode, api_name)
                if result and result.product_name:
                    logger.info(f"Successfully found product data using {api_name}")
                    return result
            except Exception as e:
                logger.warning(f"API {api_name} failed: {e}")
                continue
        
        logger.debug(f"No product data found for barcode: {barcode}")
        return None
    
    def _lookup_single_api(self, barcode: str, api_name: str) -> Optional[BarcodeData]:
        """Look up barcode using a single API"""
        
        if api_name == 'openfoodfacts':
            return self._lookup_openfoodfacts(barcode)
        elif api_name == 'upcitemdb':
            return self._lookup_upcitemdb(barcode)
        elif api_name == 'barcode_lookup':
            return self._lookup_barcode_lookup(barcode)
        else:
            raise ValueError(f"Unknown API: {api_name}")
    
    def _lookup_openfoodfacts(self, barcode: str) -> Optional[BarcodeData]:
        """Look up barcode using Open Food Facts API"""
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 1 and 'product' in data:
                product = data['product']
                
                # Extract nutrition facts
                nutrition = {}
                if 'nutriments' in product:
                    nutriments = product['nutriments']
                    for key, value in nutriments.items():
                        if not key.endswith('_unit') and not key.endswith('_value'):
                            nutrition[key] = value
                
                # Extract images
                images = []
                if 'images' in product:
                    for img_key, img_data in product['images'].items():
                        if isinstance(img_data, dict) and 'display' in img_data:
                            images.append(img_data['display'])
                
                return BarcodeData(
                    barcode=barcode,
                    format='EAN/UPC',
                    product_name=product.get('product_name', ''),
                    brand=product.get('brands', ''),
                    manufacturer=product.get('manufacturing_places', ''),
                    category=product.get('categories', ''),
                    description=product.get('generic_name', ''),
                    images=images,
                    nutrition_facts=nutrition,
                    ingredients=product.get('ingredients_text', '').split(', ') if product.get('ingredients_text') else [],
                    net_weight=product.get('quantity', ''),
                    country_of_origin=product.get('countries', ''),
                    source_api='Open Food Facts',
                    confidence=0.9,
                    raw_data=product
                )
            
        except Exception as e:
            logger.error(f"Open Food Facts API error: {e}")
            
        return None
    
    def _lookup_upcitemdb(self, barcode: str) -> Optional[BarcodeData]:
        """Look up barcode using UPC Item DB API"""
        url = "https://api.upcitemdb.com/prod/trial/lookup"
        
        try:
            params = {'upc': barcode}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 'OK' and 'items' in data and data['items']:
                item = data['items'][0]  # Take first result
                
                return BarcodeData(
                    barcode=barcode,
                    format='UPC',
                    product_name=item.get('title', ''),
                    brand=item.get('brand', ''),
                    manufacturer=item.get('manufacturer', ''),
                    category=item.get('category', ''),
                    description=item.get('description', ''),
                    images=[item.get('image', '')] if item.get('image') else [],
                    net_weight=item.get('size', ''),
                    source_api='UPC Item DB',
                    confidence=0.8,
                    raw_data=item
                )
                
        except Exception as e:
            logger.error(f"UPC Item DB API error: {e}")
        
        return None
    
    def _lookup_barcode_lookup(self, barcode: str) -> Optional[BarcodeData]:
        """Look up barcode using Barcode Lookup API (requires API key)"""
        api_key = self.api_keys.get('barcode_lookup')
        if not api_key:
            logger.debug("Barcode Lookup API key not configured")
            return None
        
        url = "https://api.barcodelookup.com/v3/products"
        
        try:
            params = {
                'barcode': barcode,
                'formatted': 'y',
                'key': api_key
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'products' in data and data['products']:
                product = data['products'][0]  # Take first result
                
                return BarcodeData(
                    barcode=barcode,
                    format=product.get('barcode_format', 'Unknown'),
                    product_name=product.get('product_name', ''),
                    brand=product.get('brand', ''),
                    manufacturer=product.get('manufacturer', ''),
                    category=product.get('category', ''),
                    description=product.get('description', ''),
                    images=[product.get('image_url', '')] if product.get('image_url') else [],
                    net_weight=product.get('size', ''),
                    country_of_origin=product.get('country', ''),
                    source_api='Barcode Lookup',
                    confidence=0.95,
                    raw_data=product
                )
                
        except Exception as e:
            logger.error(f"Barcode Lookup API error: {e}")
        
        return None
    
    def extract_compliance_fields(self, barcode_data: BarcodeData) -> Dict[str, Any]:
        """Extract Legal Metrology compliance fields from barcode data"""
        
        compliance_fields = {
            'product_name': barcode_data.product_name or '',
            'brand_name': barcode_data.brand or '',
            'manufacturer_name': barcode_data.manufacturer or '',
            'net_quantity_raw': barcode_data.net_weight or '',
            'country_of_origin': barcode_data.country_of_origin or '',
            'category': barcode_data.category or '',
            'ingredients': ', '.join(barcode_data.ingredients) if barcode_data.ingredients else '',
            'barcode': barcode_data.barcode,
            'data_source': f"Barcode Scan ({barcode_data.source_api})",
            'confidence_score': barcode_data.confidence * 100,
            'extraction_method': 'barcode_api'
        }
        
        # Try to extract MRP from product name or description
        mrp_patterns = [
            r'₹\s*(\d+(?:\.\d{2})?)',
            r'RS\.?\s*(\d+(?:\.\d{2})?)',
            r'INR\s*(\d+(?:\.\d{2})?)',
            r'MRP\s*₹?\s*(\d+(?:\.\d{2})?)'
        ]
        
        import re
        text_to_search = f"{barcode_data.product_name} {barcode_data.description}".lower()
        
        for pattern in mrp_patterns:
            match = re.search(pattern, text_to_search, re.IGNORECASE)
            if match:
                compliance_fields['mrp_raw'] = f"₹{match.group(1)}"
                break
        
        # Extract net quantity with units
        if barcode_data.net_weight:
            weight = barcode_data.net_weight
            # Common weight/volume patterns
            quantity_patterns = [
                r'(\d+(?:\.\d+)?)\s*(kg|g|l|ml|pieces?|pcs?|units?)',
                r'(\d+(?:\.\d+)?)\s*(kilogram|gram|liter|milliliter)'
            ]
            
            for pattern in quantity_patterns:
                match = re.search(pattern, weight.lower())
                if match:
                    value, unit = match.groups()
                    compliance_fields['net_quantity_raw'] = f"{value} {unit}"
                    break
        
        return compliance_fields
    
    def get_available_apis(self) -> Dict[str, Dict]:
        """Get information about available APIs"""
        api_info = {}
        
        for api_name, api_data in self.apis.items():
            # Free APIs are always available
            # Paid APIs are available only if API key is configured
            is_available = api_data['free'] or bool(self.api_keys.get(api_name))
            
            api_info[api_name] = {
                'name': api_data['name'],
                'description': api_data['description'],
                'free': api_data['free'],
                'available': is_available,
                'requires_key': not api_data['free'],
                'status': 'Free' if api_data['free'] else ('Available' if is_available else 'Requires API Key')
            }
        
        return api_info
    
    def validate_barcode(self, barcode: str) -> Tuple[bool, str]:
        """Validate barcode format and checksum"""
        
        # Remove any spaces or dashes
        barcode = barcode.replace(' ', '').replace('-', '')
        
        # Check if it's numeric
        if not barcode.isdigit():
            return False, "Barcode must contain only digits"
        
        # Check length for common formats
        valid_lengths = [8, 12, 13, 14]  # EAN-8, UPC-A, EAN-13, ITF-14
        
        if len(barcode) not in valid_lengths:
            return False, f"Invalid barcode length: {len(barcode)}. Expected: {valid_lengths}"
        
        # Validate EAN-13 checksum
        if len(barcode) == 13:
            check_digit = int(barcode[-1])
            calculated_check = self._calculate_ean13_checksum(barcode[:-1])
            if check_digit != calculated_check:
                return False, f"Invalid EAN-13 checksum. Expected: {calculated_check}, Got: {check_digit}"
        
        # Validate UPC-A checksum
        elif len(barcode) == 12:
            check_digit = int(barcode[-1])
            calculated_check = self._calculate_upc_checksum(barcode[:-1])
            if check_digit != calculated_check:
                return False, f"Invalid UPC-A checksum. Expected: {calculated_check}, Got: {check_digit}"
        
        return True, "Valid barcode format"
    
    def _calculate_ean13_checksum(self, barcode: str) -> int:
        """Calculate EAN-13 checksum digit"""
        odd_sum = sum(int(barcode[i]) for i in range(0, len(barcode), 2))
        even_sum = sum(int(barcode[i]) for i in range(1, len(barcode), 2))
        total = odd_sum + (even_sum * 3)
        return (10 - (total % 10)) % 10
    
    def _calculate_upc_checksum(self, barcode: str) -> int:
        """Calculate UPC-A checksum digit"""
        odd_sum = sum(int(barcode[i]) for i in range(0, len(barcode), 2))
        even_sum = sum(int(barcode[i]) for i in range(1, len(barcode), 2))
        total = (odd_sum * 3) + even_sum
        return (10 - (total % 10)) % 10


# Global barcode scanner instance
_barcode_scanner = None

def get_barcode_scanner() -> BarcodeScanner:
    """Get or create global barcode scanner instance"""
    global _barcode_scanner
    
    if _barcode_scanner is None:
        _barcode_scanner = BarcodeScanner()
    
    return _barcode_scanner
