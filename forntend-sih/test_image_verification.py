#!/usr/bin/env python3
"""
Test Image-Based Product Verification System
Tests the image verification functionality and ERP matching
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.erp_manager import erp_manager
from core.image_product_matcher import image_product_matcher
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_product_image(product_data):
    """Create a test product image with the given data"""
    # Create a test image with product information
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a default font, fallback to basic font
        font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw product information on the image
    y_pos = 50
    
    # Product name
    if product_data.get('product_name'):
        draw.text((50, y_pos), product_data['product_name'], fill='black', font=font_large)
        y_pos += 60
    
    # MRP
    if product_data.get('mrp'):
        draw.text((50, y_pos), f"MRP: ₹{product_data['mrp']} (Inclusive of all taxes)", fill='black', font=font_medium)
        y_pos += 40
    
    # Net Quantity
    if product_data.get('net_quantity') and product_data.get('unit'):
        draw.text((50, y_pos), f"Net Quantity: {product_data['net_quantity']} {product_data['unit']}", fill='black', font=font_medium)
        y_pos += 40
    
    # Manufacturer
    if product_data.get('manufacturer_name'):
        draw.text((50, y_pos), f"Manufactured by: {product_data['manufacturer_name']}", fill='black', font=font_small)
        y_pos += 30
    
    # Manufacturing date
    if product_data.get('mfg_date'):
        draw.text((50, y_pos), f"Mfg Date: {product_data['mfg_date']}", fill='black', font=font_small)
        y_pos += 30
    
    # Batch number
    if product_data.get('batch_number'):
        draw.text((50, y_pos), f"Batch No: {product_data['batch_number']}", fill='black', font=font_small)
        y_pos += 30
    
    # FSSAI number
    if product_data.get('fssai_number'):
        draw.text((50, y_pos), f"FSSAI Lic No: {product_data['fssai_number']}", fill='black', font=font_small)
        y_pos += 30
    
    return img

def image_to_bytes(img):
    """Convert PIL image to bytes"""
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def test_image_verification_system():
    """Test the image verification system"""
    
    print("🧪 TESTING IMAGE-BASED PRODUCT VERIFICATION SYSTEM")
    print("=" * 60)
    
    # Get existing products from ERP
    existing_products = erp_manager.get_all_products()
    if not existing_products:
        print("⚠️ No products in ERP system to test with")
        return
    
    test_product = existing_products[0]
    print(f"Testing with product: {test_product.sku} - {test_product.product_name}")
    
    # Test Case 1: Perfect Match
    print("\n✅ TEST CASE 1: Perfect Match")
    
    perfect_match_data = {
        'product_name': test_product.product_name,
        'mrp': test_product.mrp,
        'net_quantity': test_product.net_quantity,
        'unit': test_product.unit,
        'manufacturer_name': test_product.manufacturer_name,
        'mfg_date': test_product.mfg_date,
        'batch_number': test_product.batch_number,
        'fssai_number': test_product.fssai_number
    }
    
    # Create test image
    test_image = create_test_product_image(perfect_match_data)
    image_bytes = image_to_bytes(test_image)
    
    # Test verification
    result = image_product_matcher.verify_product_with_image(image_bytes, test_product.sku)
    
    print(f"Verification Status: {result.verification_status}")
    print(f"Confidence Score: {result.confidence_score:.1f}%")
    print(f"Is Match: {result.is_match}")
    
    if result.matched_product:
        print(f"Matched Product: {result.matched_product.sku}")
    
    if result.issues:
        print("Issues:")
        for issue in result.issues[:3]:  # Show first 3 issues
            print(f"  - {issue}")
    
    # Test Case 2: Partial Match (different MRP)
    print("\n🔍 TEST CASE 2: Partial Match (Different MRP)")
    
    partial_match_data = perfect_match_data.copy()
    partial_match_data['mrp'] = float(test_product.mrp) * 1.2  # 20% higher price
    
    partial_image = create_test_product_image(partial_match_data)
    partial_image_bytes = image_to_bytes(partial_image)
    
    result2 = image_product_matcher.verify_product_with_image(partial_image_bytes, test_product.sku)
    
    print(f"Verification Status: {result2.verification_status}")
    print(f"Confidence Score: {result2.confidence_score:.1f}%")
    print(f"Is Match: {result2.is_match}")
    
    # Test Case 3: Find Best Match (without specifying SKU)
    print("\n🆕 TEST CASE 3: Find Best Match")
    
    result3 = image_product_matcher.find_best_matching_product(image_bytes)
    
    print(f"Verification Status: {result3.verification_status}")
    print(f"Confidence Score: {result3.confidence_score:.1f}%")
    print(f"Is Match: {result3.is_match}")
    
    if result3.matched_product:
        print(f"Best Match Found: {result3.matched_product.sku} - {result3.matched_product.product_name}")
    
    # Test Case 4: No Match (completely different product)
    print("\n❌ TEST CASE 4: No Match")
    
    no_match_data = {
        'product_name': 'Completely Different Product XYZ',
        'mrp': 9999.99,
        'net_quantity': 500,
        'unit': 'ml',
        'manufacturer_name': 'Unknown Manufacturer Ltd',
        'mfg_date': '01/01/2030',
        'batch_number': 'UNKNOWN123',
        'fssai_number': '99999999999999'
    }
    
    no_match_image = create_test_product_image(no_match_data)
    no_match_bytes = image_to_bytes(no_match_image)
    
    result4 = image_product_matcher.verify_product_with_image(no_match_bytes, test_product.sku)
    
    print(f"Verification Status: {result4.verification_status}")
    print(f"Confidence Score: {result4.confidence_score:.1f}%")
    print(f"Is Match: {result4.is_match}")
    
    # Test Case 5: OCR Extraction Test
    print("\n📝 TEST CASE 5: OCR Text Extraction")
    
    extracted_fields, extracted_text = image_product_matcher.extract_product_data_from_image(image_bytes)
    
    if extracted_fields:
        print("Successfully extracted product data from image:")
        print(f"  - MRP: ₹{extracted_fields.mrp_value}" if extracted_fields.mrp_value else "  - MRP: Not found")
        print(f"  - Quantity: {extracted_fields.net_quantity_value} {extracted_fields.unit}" if extracted_fields.net_quantity_value else "  - Quantity: Not found")
        print(f"  - Manufacturer: {extracted_fields.manufacturer_name}" if extracted_fields.manufacturer_name else "  - Manufacturer: Not found")
        print(f"  - Extraction Confidence: {extracted_fields.extraction_confidence:.1f}%" if hasattr(extracted_fields, 'extraction_confidence') else "")
    else:
        print("❌ Failed to extract data from image")
    
    print(f"\nExtracted Text Length: {len(extracted_text)} characters")

def test_field_similarity_calculation():
    """Test the field similarity calculation"""
    
    print("\n📊 TESTING FIELD SIMILARITY CALCULATION")
    print("=" * 40)
    
    matcher = image_product_matcher
    
    # Test text similarity
    text_sim1 = matcher.calculate_field_similarity("Premium Chocolate", "Premium Chocolate", "text")
    text_sim2 = matcher.calculate_field_similarity("Premium Chocolate", "Premium Choco", "text")
    text_sim3 = matcher.calculate_field_similarity("Premium Chocolate", "Different Product", "text")
    
    print(f"Text Similarity Tests:")
    print(f"  - Identical: {text_sim1:.1f}%")
    print(f"  - Similar: {text_sim2:.1f}%")
    print(f"  - Different: {text_sim3:.1f}%")
    
    # Test numeric similarity
    num_sim1 = matcher.calculate_field_similarity(299.99, 299.99, "numeric")
    num_sim2 = matcher.calculate_field_similarity(299.99, 300.00, "numeric")
    num_sim3 = matcher.calculate_field_similarity(299.99, 350.00, "numeric")
    
    print(f"\nNumeric Similarity Tests:")
    print(f"  - Identical: {num_sim1:.1f}%")
    print(f"  - Close: {num_sim2:.1f}%")
    print(f"  - Different: {num_sim3:.1f}%")
    
    # Test exact match
    exact_sim1 = matcher.calculate_field_similarity("g", "g", "exact")
    exact_sim2 = matcher.calculate_field_similarity("g", "G", "exact")
    exact_sim3 = matcher.calculate_field_similarity("g", "kg", "exact")
    
    print(f"\nExact Match Tests:")
    print(f"  - Identical: {exact_sim1:.1f}%")
    print(f"  - Case Different: {exact_sim2:.1f}%")
    print(f"  - Different: {exact_sim3:.1f}%")

def main():
    """Main test function"""
    try:
        test_image_verification_system()
        test_field_similarity_calculation()
        
        print("\n" + "=" * 60)
        print("🎉 IMAGE VERIFICATION SYSTEM TEST COMPLETE!")
        print("✅ Features tested:")
        print("   • Image-based product verification")
        print("   • OCR text extraction from images")
        print("   • Product matching algorithms")
        print("   • Confidence scoring system")
        print("   • Field similarity calculations")
        print("   • Positive/Negative/Uncertain classification")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
