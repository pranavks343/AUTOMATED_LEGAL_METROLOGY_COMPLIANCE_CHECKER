"""
Image-Based Product Verification System
Matches uploaded product images with ERP product data using OCR and AI analysis
"""

import io
import re
import difflib
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
from dataclasses import dataclass
from .ocr import image_to_text
from .nlp_extract import extract_fields
from .erp_manager import erp_manager, ProductData
from .schemas import ExtractedFields
import logging

logger = logging.getLogger(__name__)

@dataclass
class ImageMatchResult:
    """Result of image-product matching"""
    is_match: bool
    confidence_score: float
    matched_product: Optional[ProductData]
    extracted_data: Optional[ExtractedFields]
    match_details: Dict[str, Any]
    verification_status: str  # 'POSITIVE', 'NEGATIVE', 'UNCERTAIN'
    issues: List[str]

class ImageProductMatcher:
    """Advanced image-based product verification system"""
    
    def __init__(self):
        self.erp_manager = erp_manager
        self.minimum_match_threshold = 70.0  # Minimum confidence for positive match
        self.high_confidence_threshold = 85.0  # High confidence threshold
    
    def extract_product_data_from_image(self, image_bytes: bytes) -> Tuple[ExtractedFields, str]:
        """Extract product information from image using OCR"""
        try:
            # Use OCR to extract text from image
            extracted_text, word_boxes = image_to_text(image_bytes)
            
            if not extracted_text.strip():
                logger.warning("No text extracted from image")
                return None, "No text could be extracted from the image"
            
            # Use NLP extraction to parse the text
            extracted_fields = extract_fields(extracted_text)
            
            # Calculate extraction confidence
            if hasattr(extracted_fields, 'calculate_confidence'):
                extracted_fields.extraction_confidence = extracted_fields.calculate_confidence()
            
            logger.info(f"Successfully extracted data from image: {len(extracted_text)} characters")
            return extracted_fields, extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting data from image: {e}")
            return None, f"Error processing image: {str(e)}"
    
    def calculate_field_similarity(self, image_value: Any, erp_value: Any, field_type: str) -> float:
        """Calculate similarity between extracted field and ERP field"""
        if not image_value or not erp_value:
            return 0.0
        
        try:
            if field_type == 'text':
                # Text similarity using difflib
                return difflib.SequenceMatcher(
                    None, 
                    str(image_value).lower().strip(), 
                    str(erp_value).lower().strip()
                ).ratio() * 100
            
            elif field_type == 'numeric':
                # Numeric similarity with tolerance
                img_val = float(image_value)
                erp_val = float(erp_value)
                
                if img_val == erp_val:
                    return 100.0
                
                # Allow small differences (up to 5%)
                tolerance = 0.05
                diff = abs(img_val - erp_val) / max(img_val, erp_val)
                
                if diff <= tolerance:
                    return max(0, 100 - (diff * 100))
                else:
                    return max(0, 100 - (diff * 200))  # Penalize larger differences more
            
            elif field_type == 'exact':
                # Exact match required
                return 100.0 if str(image_value).lower() == str(erp_value).lower() else 0.0
        
        except Exception as e:
            logger.error(f"Error calculating similarity for {field_type}: {e}")
            return 0.0
        
        return 0.0
    
    def match_with_erp_product(self, extracted_fields: ExtractedFields, target_product: ProductData) -> Dict[str, float]:
        """Match extracted fields with specific ERP product"""
        match_scores = {}
        
        # Product name matching (if available in image)
        if hasattr(extracted_fields, 'product_name') and extracted_fields.product_name:
            match_scores['product_name'] = self.calculate_field_similarity(
                extracted_fields.product_name, target_product.product_name, 'text'
            )
        
        # MRP matching
        if extracted_fields.mrp_value and target_product.mrp:
            match_scores['mrp'] = self.calculate_field_similarity(
                extracted_fields.mrp_value, target_product.mrp, 'numeric'
            )
        
        # Net quantity matching
        if extracted_fields.net_quantity_value and target_product.net_quantity:
            match_scores['net_quantity'] = self.calculate_field_similarity(
                extracted_fields.net_quantity_value, target_product.net_quantity, 'numeric'
            )
        
        # Unit matching
        if extracted_fields.unit and target_product.unit:
            match_scores['unit'] = self.calculate_field_similarity(
                extracted_fields.unit, target_product.unit, 'exact'
            )
        
        # Manufacturer matching
        if extracted_fields.manufacturer_name and target_product.manufacturer_name:
            match_scores['manufacturer'] = self.calculate_field_similarity(
                extracted_fields.manufacturer_name, target_product.manufacturer_name, 'text'
            )
        
        # Manufacturing date matching (if available)
        if extracted_fields.mfg_date and target_product.mfg_date:
            match_scores['mfg_date'] = self.calculate_field_similarity(
                extracted_fields.mfg_date, target_product.mfg_date, 'text'
            )
        
        # Batch number matching (if available)
        if extracted_fields.batch_number and target_product.batch_number:
            match_scores['batch_number'] = self.calculate_field_similarity(
                extracted_fields.batch_number, target_product.batch_number, 'exact'
            )
        
        # FSSAI number matching (if available)
        if extracted_fields.fssai_number and target_product.fssai_number:
            match_scores['fssai_number'] = self.calculate_field_similarity(
                extracted_fields.fssai_number, target_product.fssai_number, 'exact'
            )
        
        return match_scores
    
    def calculate_overall_match_confidence(self, match_scores: Dict[str, float]) -> float:
        """Calculate overall confidence score with weighted fields"""
        if not match_scores:
            return 0.0
        
        # Field weights based on importance for product identification
        field_weights = {
            'mrp': 0.25,           # High importance for price matching
            'net_quantity': 0.20,  # High importance for quantity
            'unit': 0.15,          # Medium importance for unit
            'manufacturer': 0.20,  # High importance for manufacturer
            'product_name': 0.10,  # Lower weight as names can vary
            'mfg_date': 0.05,      # Lower importance
            'batch_number': 0.03,  # Lower importance
            'fssai_number': 0.02   # Lower importance
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for field, score in match_scores.items():
            weight = field_weights.get(field, 0.1)  # Default weight for unknown fields
            weighted_score += score * weight
            total_weight += weight
        
        # Normalize by total weight
        if total_weight > 0:
            return weighted_score / total_weight
        
        return 0.0
    
    def verify_product_with_image(self, image_bytes: bytes, target_sku: str) -> ImageMatchResult:
        """Verify if uploaded image matches the specified ERP product"""
        try:
            # Get target product from ERP
            target_product = self.erp_manager.get_product_by_sku(target_sku)
            if not target_product:
                return ImageMatchResult(
                    is_match=False,
                    confidence_score=0.0,
                    matched_product=None,
                    extracted_data=None,
                    match_details={'error': f'Product with SKU {target_sku} not found in ERP'},
                    verification_status='NEGATIVE',
                    issues=[f'Product SKU {target_sku} not found in ERP system']
                )
            
            # Extract data from image
            extracted_fields, extracted_text = self.extract_product_data_from_image(image_bytes)
            if not extracted_fields:
                return ImageMatchResult(
                    is_match=False,
                    confidence_score=0.0,
                    matched_product=target_product,
                    extracted_data=None,
                    match_details={'error': 'Failed to extract data from image'},
                    verification_status='NEGATIVE',
                    issues=['Could not extract readable text from image']
                )
            
            # Calculate match scores
            match_scores = self.match_with_erp_product(extracted_fields, target_product)
            overall_confidence = self.calculate_overall_match_confidence(match_scores)
            
            # Determine verification status
            if overall_confidence >= self.high_confidence_threshold:
                verification_status = 'POSITIVE'
                is_match = True
            elif overall_confidence >= self.minimum_match_threshold:
                verification_status = 'UNCERTAIN'
                is_match = True  # Consider as match but with lower confidence
            else:
                verification_status = 'NEGATIVE'
                is_match = False
            
            # Identify specific issues
            issues = []
            for field, score in match_scores.items():
                if score < 50.0:  # Low similarity threshold
                    issues.append(f"Low similarity in {field}: {score:.1f}%")
            
            if not issues and verification_status == 'POSITIVE':
                issues.append("All fields match with high confidence")
            elif not issues:
                issues.append("Insufficient data extracted from image for reliable verification")
            
            return ImageMatchResult(
                is_match=is_match,
                confidence_score=overall_confidence,
                matched_product=target_product,
                extracted_data=extracted_fields,
                match_details={
                    'field_scores': match_scores,
                    'extracted_text': extracted_text[:200] + '...' if len(extracted_text) > 200 else extracted_text,
                    'total_fields_matched': len(match_scores)
                },
                verification_status=verification_status,
                issues=issues
            )
        
        except Exception as e:
            logger.error(f"Error in product verification: {e}")
            return ImageMatchResult(
                is_match=False,
                confidence_score=0.0,
                matched_product=None,
                extracted_data=None,
                match_details={'error': str(e)},
                verification_status='NEGATIVE',
                issues=[f'System error: {str(e)}']
            )
    
    def find_best_matching_product(self, image_bytes: bytes) -> ImageMatchResult:
        """Find the best matching product in ERP for the uploaded image"""
        try:
            # Extract data from image
            extracted_fields, extracted_text = self.extract_product_data_from_image(image_bytes)
            if not extracted_fields:
                return ImageMatchResult(
                    is_match=False,
                    confidence_score=0.0,
                    matched_product=None,
                    extracted_data=None,
                    match_details={'error': 'Failed to extract data from image'},
                    verification_status='NEGATIVE',
                    issues=['Could not extract readable text from image']
                )
            
            # Get all products from ERP
            all_products = self.erp_manager.get_all_products()
            if not all_products:
                return ImageMatchResult(
                    is_match=False,
                    confidence_score=0.0,
                    matched_product=None,
                    extracted_data=extracted_fields,
                    match_details={'error': 'No products found in ERP system'},
                    verification_status='NEGATIVE',
                    issues=['ERP system contains no products to match against']
                )
            
            best_match = None
            best_score = 0.0
            best_match_details = {}
            
            # Test against all products
            for product in all_products:
                match_scores = self.match_with_erp_product(extracted_fields, product)
                overall_confidence = self.calculate_overall_match_confidence(match_scores)
                
                if overall_confidence > best_score:
                    best_score = overall_confidence
                    best_match = product
                    best_match_details = match_scores
            
            # Determine verification status
            if best_score >= self.high_confidence_threshold:
                verification_status = 'POSITIVE'
                is_match = True
                issues = [f"Strong match found with {best_match.sku}"]
            elif best_score >= self.minimum_match_threshold:
                verification_status = 'UNCERTAIN'
                is_match = True
                issues = [f"Possible match with {best_match.sku} but low confidence"]
            else:
                verification_status = 'NEGATIVE'
                is_match = False
                issues = ["No matching product found in ERP system"]
            
            return ImageMatchResult(
                is_match=is_match,
                confidence_score=best_score,
                matched_product=best_match,
                extracted_data=extracted_fields,
                match_details={
                    'field_scores': best_match_details,
                    'extracted_text': extracted_text[:200] + '...' if len(extracted_text) > 200 else extracted_text,
                    'total_products_tested': len(all_products)
                },
                verification_status=verification_status,
                issues=issues
            )
        
        except Exception as e:
            logger.error(f"Error finding best matching product: {e}")
            return ImageMatchResult(
                is_match=False,
                confidence_score=0.0,
                matched_product=None,
                extracted_data=None,
                match_details={'error': str(e)},
                verification_status='NEGATIVE',
                issues=[f'System error: {str(e)}']
            )

# Global instance
image_product_matcher = ImageProductMatcher()
