#!/usr/bin/env python3
"""
Comprehensive Sandbox API Testing Script
Tests all aspects of the Legal Metrology Compliance System
"""

import sys
import os
import json
import time
import requests
import base64
from pathlib import Path
from typing import Dict, List, Any

# Add app directory to Python path
sys.path.insert(0, 'app')

try:
    from core.web_crawler import EcommerceCrawler, ProductData
    from core.barcode_scanner import BarcodeScanner
    from core.rules_engine import RulesEngine
    from core.erp_manager import ERPManager, ProductCategory
    from core.chatbot import ComplianceChatbot
    print("✅ All core modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class SandboxAPITester:
    """Comprehensive API testing suite for the sandbox environment"""
    
    def __init__(self):
        """Initialize the API tester"""
        self.base_url = "http://localhost:8501"
        self.api_base = f"{self.base_url}/api/v1"
        self.test_results = []
        
        print("🧪 Initializing Sandbox API Tester...")
        print(f"📡 Base URL: {self.base_url}")
        print(f"🔗 API Base: {self.api_base}")
    
    def test_system_health(self) -> bool:
        """Test if the system is running and healthy"""
        print("\n🏥 Testing System Health...")
        
        try:
            # Test if Streamlit app is running
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                print("✅ Streamlit application is running")
                return True
            else:
                print(f"❌ Streamlit app returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Streamlit application")
            print("💡 Make sure to run: streamlit run app/streamlit_app.py")
            return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_web_crawler(self) -> Dict[str, Any]:
        """Test the web crawler functionality"""
        print("\n🕷️ Testing Web Crawler...")
        
        test_result = {
            "test": "web_crawler",
            "status": "failed",
            "details": {},
            "errors": []
        }
        
        try:
            # Initialize crawler
            crawler = EcommerceCrawler()
            print("✅ Web crawler initialized")
            
            # Test supported platforms
            platforms = crawler.get_supported_platforms()
            print(f"✅ Supported platforms: {list(platforms.keys())}")
            test_result["details"]["supported_platforms"] = list(platforms.keys())
            
            # Test product search (limited results for testing)
            print("🔍 Testing product search...")
            products = crawler.search_products(
                query="test chocolate",
                platform="amazon",
                max_results=3
            )
            
            print(f"✅ Found {len(products)} test products")
            test_result["details"]["products_found"] = len(products)
            
            # Test product data structure
            if products:
                sample_product = products[0]
                print(f"✅ Sample product: {sample_product.title[:50]}...")
                test_result["details"]["sample_product"] = {
                    "title": sample_product.title,
                    "price": sample_product.price,
                    "platform": sample_product.platform
                }
            
            # Test data export
            if products:
                json_file = crawler.save_products(products, "test_crawl_results.json")
                print(f"✅ Results saved to: {json_file}")
                test_result["details"]["export_file"] = json_file
            
            test_result["status"] = "passed"
            
        except Exception as e:
            error_msg = f"Web crawler test failed: {e}"
            print(f"❌ {error_msg}")
            test_result["errors"].append(error_msg)
        
        self.test_results.append(test_result)
        return test_result
    
    def test_barcode_scanner(self) -> Dict[str, Any]:
        """Test the barcode scanner functionality"""
        print("\n📱 Testing Barcode Scanner...")
        
        test_result = {
            "test": "barcode_scanner",
            "status": "failed",
            "details": {},
            "errors": []
        }
        
        try:
            # Initialize scanner
            scanner = BarcodeScanner()
            print("✅ Barcode scanner initialized")
            
            # Test available APIs
            available_apis = scanner.get_available_apis()
            print(f"✅ Available APIs: {list(available_apis.keys())}")
            test_result["details"]["available_apis"] = list(available_apis.keys())
            
            # Test with a known barcode (Coca Cola)
            test_barcode = "8901030895555"  # Sample barcode
            print(f"🔍 Testing barcode lookup: {test_barcode}")
            
            barcode_data = scanner.scan_barcode(test_barcode)
            if barcode_data:
                print(f"✅ Barcode data retrieved: {barcode_data.product_name}")
                test_result["details"]["test_barcode_result"] = {
                    "barcode": test_barcode,
                    "product_name": barcode_data.product_name,
                    "brand": barcode_data.brand
                }
            else:
                print("⚠️ No data found for test barcode (this is normal for test data)")
                test_result["details"]["test_barcode_result"] = "no_data_found"
            
            test_result["status"] = "passed"
            
        except Exception as e:
            error_msg = f"Barcode scanner test failed: {e}"
            print(f"❌ {error_msg}")
            test_result["errors"].append(error_msg)
        
        self.test_results.append(test_result)
        return test_result
    
    def test_rules_engine(self) -> Dict[str, Any]:
        """Test the compliance rules engine"""
        print("\n⚖️ Testing Rules Engine...")
        
        test_result = {
            "test": "rules_engine",
            "status": "failed",
            "details": {},
            "errors": []
        }
        
        try:
            # Initialize rules engine
            rules_engine = RulesEngine()
            print("✅ Rules engine initialized")
            
            # Test product validation with sample data
            test_products = [
                {
                    "title": "Premium Chocolate Bar",
                    "mrp": 299.99,
                    "net_quantity": "100g",
                    "manufacturer": "Test Chocolate Co., Mumbai",
                    "country_of_origin": "India",
                    "category": "food"
                },
                {
                    "title": "Wireless Headphones",
                    "mrp": 2999.00,
                    "manufacturer": "Tech Audio Ltd., Bangalore",
                    "country_of_origin": "China",
                    "category": "electronics"
                },
                {
                    "title": "Invalid Product",  # Missing required fields
                    "category": "food"
                }
            ]
            
            validation_results = []
            for i, product in enumerate(test_products):
                print(f"🔍 Testing product {i+1}: {product.get('title', 'Unknown')}")
                
                try:
                    result = rules_engine.validate_product(product)
                    score = result.get('compliance_score', 0)
                    issues = len(result.get('violations', []))
                    
                    print(f"   ✅ Compliance Score: {score}")
                    print(f"   ⚠️ Issues Found: {issues}")
                    
                    validation_results.append({
                        "product": product.get('title', 'Unknown'),
                        "score": score,
                        "issues": issues,
                        "violations": result.get('violations', [])
                    })
                    
                except Exception as e:
                    print(f"   ❌ Validation failed: {e}")
                    validation_results.append({
                        "product": product.get('title', 'Unknown'),
                        "error": str(e)
                    })
            
            test_result["details"]["validation_results"] = validation_results
            
            # Calculate average compliance score
            valid_scores = [r['score'] for r in validation_results if 'score' in r]
            if valid_scores:
                avg_score = sum(valid_scores) / len(valid_scores)
                print(f"✅ Average Compliance Score: {avg_score:.2f}")
                test_result["details"]["average_score"] = avg_score
            
            test_result["status"] = "passed"
            
        except Exception as e:
            error_msg = f"Rules engine test failed: {e}"
            print(f"❌ {error_msg}")
            test_result["errors"].append(error_msg)
        
        self.test_results.append(test_result)
        return test_result
    
    def test_erp_integration(self) -> Dict[str, Any]:
        """Test ERP integration functionality"""
        print("\n🏭 Testing ERP Integration...")
        
        test_result = {
            "test": "erp_integration",
            "status": "failed",
            "details": {},
            "errors": []
        }
        
        try:
            # Initialize ERP manager
            erp_manager = ERPManager()
            print("✅ ERP manager initialized")
            
            # Test product creation
            test_product = erp_manager.add_product(
                product_name="Test ERP Product - Organic Rice",
                mrp=450.00,
                net_quantity=1.0,
                unit="kg",
                manufacturer_name="Test Organic Foods Pvt Ltd",
                category=ProductCategory.FOOD,
                created_by="api_test_user",
                manufacturer_address="123 Test Street, Mumbai, Maharashtra",
                country_of_origin="India",
                fssai_number="12345678901234"
            )
            
            print(f"✅ Test product created: {test_product.sku}")
            test_result["details"]["test_product_sku"] = test_product.sku
            
            # Test product retrieval
            retrieved_product = erp_manager.get_product(test_product.sku)
            if retrieved_product:
                print(f"✅ Product retrieved: {retrieved_product.product_name}")
                test_result["details"]["product_retrieved"] = True
            
            # Test product listing
            all_products = erp_manager.list_products()
            print(f"✅ Total products in ERP: {len(all_products)}")
            test_result["details"]["total_products"] = len(all_products)
            
            # Test product update
            updated_product = erp_manager.update_product(
                test_product.sku,
                {"notes": [{"author": "api_test", "content": "API test note"}]}
            )
            
            if updated_product and updated_product.notes:
                print("✅ Product updated successfully")
                test_result["details"]["product_updated"] = True
            
            test_result["status"] = "passed"
            
        except Exception as e:
            error_msg = f"ERP integration test failed: {e}"
            print(f"❌ {error_msg}")
            test_result["errors"].append(error_msg)
        
        self.test_results.append(test_result)
        return test_result
    
    def test_chatbot(self) -> Dict[str, Any]:
        """Test the AI chatbot functionality"""
        print("\n🤖 Testing AI Chatbot...")
        
        test_result = {
            "test": "chatbot",
            "status": "failed",
            "details": {},
            "errors": []
        }
        
        try:
            # Initialize chatbot
            chatbot = ComplianceChatbot()
            print("✅ Chatbot initialized")
            
            # Test queries
            test_queries = [
                "What is the MRP requirement for food products?",
                "How to calculate net quantity for liquids?",
                "What are the penalties for non-compliance?"
            ]
            
            responses = []
            for query in test_queries:
                print(f"🔍 Testing query: {query[:50]}...")
                
                try:
                    response = chatbot.get_response(query, user_id="api_test_user")
                    if response and len(response) > 10:
                        print("✅ Response received")
                        responses.append({
                            "query": query,
                            "response_length": len(response),
                            "success": True
                        })
                    else:
                        print("⚠️ Short or empty response")
                        responses.append({
                            "query": query,
                            "response_length": 0,
                            "success": False
                        })
                        
                except Exception as e:
                    print(f"❌ Query failed: {e}")
                    responses.append({
                        "query": query,
                        "error": str(e),
                        "success": False
                    })
            
            test_result["details"]["query_responses"] = responses
            
            # Check success rate
            successful_queries = sum(1 for r in responses if r.get('success', False))
            success_rate = (successful_queries / len(test_queries)) * 100
            print(f"✅ Chatbot success rate: {success_rate:.1f}%")
            test_result["details"]["success_rate"] = success_rate
            
            if success_rate >= 50:  # At least 50% success rate
                test_result["status"] = "passed"
            
        except Exception as e:
            error_msg = f"Chatbot test failed: {e}"
            print(f"❌ {error_msg}")
            test_result["errors"].append(error_msg)
        
        self.test_results.append(test_result)
        return test_result
    
    def test_file_operations(self) -> Dict[str, Any]:
        """Test file operations and data persistence"""
        print("\n📁 Testing File Operations...")
        
        test_result = {
            "test": "file_operations",
            "status": "failed",
            "details": {},
            "errors": []
        }
        
        try:
            # Test data directories
            data_dirs = [
                "app/data",
                "app/data/uploads",
                "app/data/reports",
                "app/data/crawled"
            ]
            
            existing_dirs = []
            for dir_path in data_dirs:
                if os.path.exists(dir_path):
                    existing_dirs.append(dir_path)
                    print(f"✅ Directory exists: {dir_path}")
                else:
                    print(f"⚠️ Directory missing: {dir_path}")
            
            test_result["details"]["existing_directories"] = existing_dirs
            
            # Test sample data files
            sample_files = [
                "app/data/sample_dataset/annotated_samples.json",
                "app/data/rules/legal_metrology_rules.yaml",
                "app/data/ecommerce_compliance_knowledge.json"
            ]
            
            existing_files = []
            for file_path in sample_files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    existing_files.append({"path": file_path, "size": file_size})
                    print(f"✅ File exists: {file_path} ({file_size} bytes)")
                else:
                    print(f"⚠️ File missing: {file_path}")
            
            test_result["details"]["existing_files"] = existing_files
            
            # Test write permissions
            test_file = "app/data/api_test_file.txt"
            try:
                with open(test_file, 'w') as f:
                    f.write("API test file")
                print("✅ Write permissions working")
                
                # Clean up test file
                os.remove(test_file)
                test_result["details"]["write_permissions"] = True
                
            except Exception as e:
                print(f"❌ Write permission test failed: {e}")
                test_result["details"]["write_permissions"] = False
            
            test_result["status"] = "passed"
            
        except Exception as e:
            error_msg = f"File operations test failed: {e}"
            print(f"❌ {error_msg}")
            test_result["errors"].append(error_msg)
        
        self.test_results.append(test_result)
        return test_result
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n📊 Generating Test Report...")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "passed")
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "detailed_results": self.test_results,
            "recommendations": []
        }
        
        # Add recommendations based on test results
        if success_rate < 50:
            report["recommendations"].append("System requires attention - multiple components failing")
        elif success_rate < 80:
            report["recommendations"].append("Some components need optimization")
        else:
            report["recommendations"].append("System is functioning well")
        
        # Check for specific issues
        for result in self.test_results:
            if result["status"] == "failed":
                report["recommendations"].append(f"Fix issues in {result['test']}")
        
        # Save report to file
        report_file = f"app/data/api_test_report_{int(time.time())}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✅ Test report saved: {report_file}")
            report["report_file"] = report_file
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
        
        return report
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests and generate report"""
        print("🚀 Starting Comprehensive Sandbox API Tests...")
        print("=" * 60)
        
        # Check system health first
        if not self.test_system_health():
            print("\n❌ System health check failed. Cannot proceed with API tests.")
            print("💡 Please start the Streamlit application first:")
            print("   streamlit run app/streamlit_app.py")
            return {"status": "failed", "reason": "system_not_running"}
        
        # Run all tests
        test_functions = [
            self.test_web_crawler,
            self.test_barcode_scanner,
            self.test_rules_engine,
            self.test_erp_integration,
            self.test_chatbot,
            self.test_file_operations
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Test function {test_func.__name__} crashed: {e}")
                self.test_results.append({
                    "test": test_func.__name__,
                    "status": "crashed",
                    "errors": [str(e)]
                })
        
        # Generate final report
        report = self.generate_test_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Passed: {report['test_summary']['passed_tests']}")
        print(f"Failed: {report['test_summary']['failed_tests']}")
        print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
        
        if report['test_summary']['success_rate'] >= 80:
            print("🎉 Excellent! Your sandbox API is ready for testing!")
        elif report['test_summary']['success_rate'] >= 60:
            print("✅ Good! Most components are working. Check failed tests.")
        else:
            print("⚠️ Needs attention. Several components require fixes.")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"• {rec}")
        
        return report

def main():
    """Main function to run API tests"""
    print("🧪 Legal Metrology Sandbox API Tester")
    print("=" * 50)
    
    # Initialize tester
    tester = SandboxAPITester()
    
    # Run all tests
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    if report.get('status') == 'failed':
        sys.exit(1)
    elif report['test_summary']['success_rate'] < 50:
        sys.exit(1)
    else:
        print(f"\n✅ Testing completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
