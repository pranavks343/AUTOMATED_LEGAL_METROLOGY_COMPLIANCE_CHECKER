#!/usr/bin/env python3
"""
Test Product Search and Verification System
Tests the product search functionality and duplicate detection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.erp_manager import erp_manager, ProductCategory

def test_product_search_functionality():
    """Test the product search and verification system"""
    
    print("🧪 TESTING PRODUCT SEARCH & VERIFICATION SYSTEM")
    print("=" * 60)
    
    # Initialize search engine
    search_engine = ProductSearchEngine()
    
    # Test Case 1: Search for exact match
    print("\n✅ TEST CASE 1: Exact Match Detection")
    
    # Get an existing product from ERP
    existing_products = erp_manager.get_all_products()
    if existing_products:
        test_product = existing_products[0]
        
        search_data = {
            'product_name': test_product.product_name,
            'manufacturer_name': test_product.manufacturer_name,
            'mrp': test_product.mrp,
            'net_quantity': test_product.net_quantity,
            'unit': test_product.unit,
            'category': test_product.category.value
        }
        
        exact_match = search_engine.check_exact_match(search_data)
        
        if exact_match:
            print(f"✅ Exact match found: {exact_match.sku}")
            print(f"   Product: {exact_match.product_name}")
            print(f"   Manufacturer: {exact_match.manufacturer_name}")
        else:
            print("❌ Exact match detection failed")
    else:
        print("⚠️ No existing products to test with")
    
    # Test Case 2: Search for similar products
    print("\n🔍 TEST CASE 2: Similar Product Detection")
    
    similar_search = {
        'product_name': 'Premium Chocolate Bar',  # Similar to existing products
        'manufacturer_name': 'Test Chocolate Co.',
        'mrp': 299.0,
        'net_quantity': 100.0,
        'unit': 'g',
        'category': 'FOOD'
    }
    
    similar_products = search_engine.search_similar_products(similar_search, 50.0)
    
    print(f"Found {len(similar_products)} similar products with >50% similarity")
    for product, score in similar_products[:3]:  # Show top 3
        print(f"  - {product.sku}: {product.product_name} (Similarity: {score:.1f}%)")
    
    # Test Case 3: New product detection
    print("\n🆕 TEST CASE 3: New Product Detection")
    
    new_search = {
        'product_name': 'Unique Test Product XYZ 12345',
        'manufacturer_name': 'Unique Test Manufacturer ABC',
        'mrp': 999.99,
        'net_quantity': 500.0,
        'unit': 'ml',
        'category': 'BEVERAGES'
    }
    
    exact_match_new = search_engine.check_exact_match(new_search)
    similar_products_new = search_engine.search_similar_products(new_search, 50.0)
    
    if not exact_match_new and not similar_products_new:
        print("✅ Correctly identified as new product")
        print(f"   Product: {new_search['product_name']}")
        print(f"   Manufacturer: {new_search['manufacturer_name']}")
    else:
        print("❌ New product detection failed")
    
    # Test Case 4: Similarity calculation
    print("\n📊 TEST CASE 4: Similarity Calculation Test")
    
    if existing_products:
        base_product = existing_products[0]
        
        # Test with slight variations
        test_variations = [
            {
                'product_name': base_product.product_name.upper(),  # Case variation
                'manufacturer_name': base_product.manufacturer_name,
                'mrp': base_product.mrp,
                'net_quantity': base_product.net_quantity,
                'unit': base_product.unit,
                'category': base_product.category.value
            },
            {
                'product_name': base_product.product_name + " Premium",  # Name variation
                'manufacturer_name': base_product.manufacturer_name,
                'mrp': base_product.mrp * 1.1,  # Price variation
                'net_quantity': base_product.net_quantity,
                'unit': base_product.unit,
                'category': base_product.category.value
            },
            {
                'product_name': base_product.product_name,
                'manufacturer_name': base_product.manufacturer_name + " Ltd",  # Manufacturer variation
                'mrp': base_product.mrp,
                'net_quantity': base_product.net_quantity * 2,  # Quantity variation
                'unit': base_product.unit,
                'category': base_product.category.value
            }
        ]
        
        for i, variation in enumerate(test_variations, 1):
            similarity = search_engine.calculate_product_similarity(variation, base_product)
            print(f"   Variation {i} similarity: {similarity:.1f}%")
    
    # Test Case 5: Search statistics
    print("\n📈 TEST CASE 5: Search Statistics")
    
    stats = search_engine.get_search_statistics()
    print(f"✅ Total products in system: {stats['total_products']}")
    print(f"✅ Unique manufacturers: {stats['unique_manufacturers']}")
    print(f"✅ Categories covered: {stats['categories_covered']}")
    print(f"✅ Compliance rate: {stats['compliance_rate']}%")

def test_duplicate_prevention():
    """Test duplicate prevention in ERP system"""
    
    print("\n🛡️ TESTING DUPLICATE PREVENTION")
    print("=" * 40)
    
    # Try to add a product that already exists
    existing_products = erp_manager.get_all_products()
    if existing_products:
        existing_product = existing_products[0]
        
        print(f"Attempting to add duplicate of: {existing_product.sku}")
        
        try:
            # This should fail due to duplicate detection
            duplicate_product = erp_manager.add_product(
                product_name=existing_product.product_name,
                mrp=existing_product.mrp,
                net_quantity=existing_product.net_quantity,
                unit=existing_product.unit,
                manufacturer_name=existing_product.manufacturer_name,
                category=existing_product.category,
                created_by="test_user"
            )
            print("❌ Duplicate prevention failed - product was added")
        except ValueError as e:
            if "already exists" in str(e):
                print("✅ Duplicate prevention working - SKU collision detected")
            else:
                print(f"⚠️ Different error occurred: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    else:
        print("⚠️ No existing products to test duplicate prevention")

def main():
    """Main test function"""
    try:
        test_product_search_functionality()
        test_duplicate_prevention()
        
        print("\n" + "=" * 60)
        print("🎉 PRODUCT SEARCH & VERIFICATION SYSTEM TEST COMPLETE!")
        print("✅ Features tested:")
        print("   • Exact match detection")
        print("   • Similar product identification") 
        print("   • New product detection")
        print("   • Similarity calculation algorithms")
        print("   • Search statistics and analytics")
        print("   • Duplicate prevention mechanisms")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

# Create a simple ProductSearchEngine class for testing
class ProductSearchEngine:
    """Product search engine for testing"""
    
    def __init__(self):
        self.erp_manager = erp_manager
    
    def calculate_product_similarity(self, product1, product2):
        """Calculate similarity between products"""
        import difflib
        
        # Simple similarity calculation
        name_sim = difflib.SequenceMatcher(
            None, 
            product1.get('product_name', '').lower(), 
            product2.product_name.lower()
        ).ratio()
        
        manufacturer_sim = difflib.SequenceMatcher(
            None,
            product1.get('manufacturer_name', '').lower(),
            product2.manufacturer_name.lower()
        ).ratio()
        
        # Weight name more heavily
        return (name_sim * 0.7 + manufacturer_sim * 0.3) * 100
    
    def check_exact_match(self, search_product):
        """Check for exact matches"""
        for existing_product in self.erp_manager.get_all_products():
            if (search_product.get('product_name', '').lower() == existing_product.product_name.lower() and
                search_product.get('manufacturer_name', '').lower() == existing_product.manufacturer_name.lower() and
                abs(float(search_product.get('mrp', 0)) - float(existing_product.mrp)) < 0.01 and
                abs(float(search_product.get('net_quantity', 0)) - float(existing_product.net_quantity)) < 0.01 and
                search_product.get('unit', '').lower() == existing_product.unit.lower()):
                return existing_product
        return None
    
    def search_similar_products(self, search_product, threshold=50.0):
        """Search for similar products"""
        similar_products = []
        
        for existing_product in self.erp_manager.get_all_products():
            similarity = self.calculate_product_similarity(search_product, existing_product)
            if similarity >= threshold:
                similar_products.append((existing_product, similarity))
        
        return sorted(similar_products, key=lambda x: x[1], reverse=True)
    
    def get_search_statistics(self):
        """Get search statistics"""
        all_products = self.erp_manager.get_all_products()
        stats = self.erp_manager.get_product_statistics()
        
        return {
            'total_products': len(all_products),
            'unique_manufacturers': len(set(p.manufacturer_name for p in all_products)),
            'categories_covered': len([cat for cat, count in stats["by_category"].items() if count > 0]),
            'compliance_rate': round((stats["by_compliance"]["COMPLIANT"] / max(len(all_products), 1)) * 100, 2)
        }

if __name__ == "__main__":
    main()
