# Sandbox E-Commerce API Testing Guide
## Legal Metrology Compliance Solutions Testing

---

## 🎯 **Overview**

This guide explains how to use the sandbox e-commerce API environment to test your legal metrology compliance solutions. The sandbox provides a safe, isolated environment where you can test product compliance checking, data extraction, and validation workflows without affecting production systems.

---

## 🏗️ **Sandbox Architecture**

### **Available APIs**

1. **Compliance Validation API** - `/api/v1/compliance/validate`
2. **Product Data Extraction API** - `/api/v1/extract`
3. **Bulk Processing API** - `/api/v1/bulk/process`
4. **Web Crawler API** - `/api/v1/crawler/search`
5. **Barcode Scanner API** - `/api/v1/barcode/scan`

### **Supported E-commerce Platforms**
- Amazon India (sandbox)
- Flipkart (sandbox)
- Myntra (sandbox)
- Nykaa (sandbox)
- Custom test platform

---

## 🚀 **Getting Started**

### **1. Environment Setup**

```bash
# Navigate to project directory
cd /Users/pranavks/Downloads/legal_metrology_checker_streamlit

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export SANDBOX_MODE=true
export API_BASE_URL=http://localhost:8501/api/v1
export OPENAI_API_KEY=your_openai_key_here
```

### **2. Start the Sandbox Server**

```bash
# Start Streamlit application in sandbox mode
streamlit run app/streamlit_app.py --server.port=8501

# The sandbox APIs will be available at:
# http://localhost:8501/api/v1/
```

---

## 🧪 **API Testing Methods**

### **Method 1: Using the Web Interface**

1. **Open the Application**
   ```
   http://localhost:8501
   ```

2. **Navigate to Testing Pages**
   - **Extraction Testing**: Go to "🔍 Extraction" page
   - **Validation Testing**: Go to "✅ Validation" page  
   - **Crawler Testing**: Go to "🌐 Web Crawler" page
   - **Barcode Testing**: Go to "📷 Barcode Scanner" page

3. **Upload Test Data**
   - Use sample images from `app/data/samples/`
   - Upload product images with labels
   - Test with different product categories

### **Method 2: Direct API Calls**

#### **A. Compliance Validation API**

```python
import requests
import json

# Test compliance validation
def test_compliance_api():
    url = "http://localhost:8501/api/v1/compliance/validate"
    
    # Sample product data
    product_data = {
        "title": "Premium Chocolate Bar",
        "brand": "Test Brand",
        "price": 299.99,
        "net_quantity": "100g",
        "manufacturer": "Test Chocolate Co.",
        "country_of_origin": "India",
        "category": "food"
    }
    
    response = requests.post(url, json=product_data)
    result = response.json()
    
    print(f"Compliance Score: {result['compliance_score']}")
    print(f"Violations: {result['violations']}")
    print(f"Recommendations: {result['recommendations']}")

# Run the test
test_compliance_api()
```

#### **B. Product Data Extraction API**

```python
import requests
import base64

def test_extraction_api():
    url = "http://localhost:8501/api/v1/extract"
    
    # Upload image for extraction
    with open("app/data/samples/sample_product.jpg", "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode()
    
    payload = {
        "image_data": image_data,
        "extraction_type": "full",
        "language": "en"
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    print(f"Extracted Data: {json.dumps(result, indent=2)}")

# Run extraction test
test_extraction_api()
```

#### **C. Web Crawler Testing**

```python
from app.core.web_crawler import EcommerceCrawler

def test_web_crawler():
    # Initialize crawler in sandbox mode
    crawler = EcommerceCrawler()
    
    # Test product search
    products = crawler.search_products(
        query="organic food products",
        platform="amazon",
        max_results=5
    )
    
    print(f"Found {len(products)} products")
    for product in products:
        print(f"- {product.title}: ₹{product.price}")
        
    # Save results for analysis
    crawler.save_products(products, "test_crawl_results.json")

# Run crawler test
test_web_crawler()
```

### **Method 3: Using Test Scripts**

#### **A. Run Comprehensive Tests**

```bash
# Test ERP integration
python app/test_erp_integration.py

# Test system configuration
python test_secrets_config.py

# Test web crawler
python -c "from app.core.web_crawler import demo_crawler; demo_crawler()"
```

#### **B. Custom Test Script**

```python
# Create: test_sandbox_api.py
import sys
sys.path.append('app')

from core.web_crawler import EcommerceCrawler
from core.barcode_scanner import BarcodeScanner
from core.rules_engine import RulesEngine
import json

def comprehensive_api_test():
    print("🧪 Starting Comprehensive Sandbox API Tests...")
    
    # Test 1: Web Crawler
    print("\n1️⃣ Testing Web Crawler API...")
    crawler = EcommerceCrawler()
    products = crawler.search_products("test product", "amazon", 3)
    print(f"✅ Crawled {len(products)} products")
    
    # Test 2: Barcode Scanner
    print("\n2️⃣ Testing Barcode Scanner API...")
    scanner = BarcodeScanner()
    apis = scanner.get_available_apis()
    print(f"✅ Available APIs: {list(apis.keys())}")
    
    # Test 3: Rules Engine
    print("\n3️⃣ Testing Compliance Rules...")
    rules_engine = RulesEngine()
    
    test_product = {
        "title": "Test Chocolate",
        "mrp": 299.99,
        "net_quantity": "100g",
        "manufacturer": "Test Co."
    }
    
    validation_result = rules_engine.validate_product(test_product)
    print(f"✅ Compliance Score: {validation_result.get('score', 0)}")
    
    print("\n🎉 All API tests completed!")

if __name__ == "__main__":
    comprehensive_api_test()
```

Run the test:
```bash
python test_sandbox_api.py
```

---

## 📊 **Testing Scenarios**

### **Scenario 1: Food Product Compliance**

```python
# Test data for food product
food_product_test = {
    "title": "Organic Basmati Rice",
    "brand": "Organic Valley",
    "price": 450.00,
    "mrp": 499.00,
    "net_quantity": "1kg",
    "manufacturer": "Organic Foods Pvt Ltd, Mumbai",
    "country_of_origin": "India",
    "mfg_date": "01/2024",
    "expiry_date": "01/2026",
    "fssai_number": "12345678901234",
    "category": "food"
}

# Expected compliance issues to test:
# - MRP format validation
# - Net quantity unit validation  
# - FSSAI number format check
# - Date format validation
```

### **Scenario 2: Electronics Compliance**

```python
# Test data for electronics
electronics_test = {
    "title": "Wireless Bluetooth Headphones",
    "brand": "TechSound",
    "price": 2999.00,
    "mrp": 3499.00,
    "manufacturer": "TechSound Electronics, Bangalore",
    "country_of_origin": "China",
    "bis_certification": "R-41012345",
    "power_consumption": "5W",
    "category": "electronics"
}

# Expected compliance checks:
# - BIS certification validation
# - Import compliance for China origin
# - Power consumption declaration
```

### **Scenario 3: Cosmetics Compliance**

```python
# Test data for cosmetics
cosmetics_test = {
    "title": "Natural Face Cream",
    "brand": "Beauty Naturals",
    "price": 899.00,
    "mrp": 999.00,
    "net_quantity": "50ml",
    "manufacturer": "Beauty Products Ltd, Delhi",
    "country_of_origin": "India",
    "mfg_date": "06/2024",
    "expiry_date": "06/2027",
    "cosmetic_license": "MH/COSM/2024/12345",
    "category": "cosmetics"
}

# Expected compliance checks:
# - Cosmetic license validation
# - Shelf life calculation
# - Ingredient list requirements
```

---

## 🔧 **Advanced Testing Features**

### **1. Bulk Testing**

```python
def bulk_compliance_test():
    # Load test dataset
    with open('app/data/sample_dataset/annotated_samples.json', 'r') as f:
        test_products = json.load(f)
    
    results = []
    for product in test_products[:10]:  # Test first 10 products
        # Test compliance validation
        response = requests.post(
            "http://localhost:8501/api/v1/compliance/validate",
            json=product
        )
        results.append({
            'product': product['title'],
            'score': response.json()['compliance_score'],
            'issues': len(response.json()['violations'])
        })
    
    # Generate test report
    avg_score = sum(r['score'] for r in results) / len(results)
    print(f"Average Compliance Score: {avg_score:.2f}")
    
    return results
```

### **2. Performance Testing**

```python
import time
import concurrent.futures

def performance_test():
    """Test API performance with concurrent requests"""
    
    def single_request():
        start_time = time.time()
        response = requests.post(
            "http://localhost:8501/api/v1/compliance/validate",
            json={"title": "Test Product", "mrp": 100}
        )
        end_time = time.time()
        return end_time - start_time
    
    # Test with 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(single_request) for _ in range(10)]
        response_times = [future.result() for future in futures]
    
    avg_response_time = sum(response_times) / len(response_times)
    print(f"Average Response Time: {avg_response_time:.3f} seconds")
    
    return response_times
```

### **3. Error Handling Testing**

```python
def error_handling_test():
    """Test API error handling with invalid data"""
    
    test_cases = [
        {"title": ""},  # Empty title
        {"mrp": -100},  # Negative price
        {"net_quantity": "invalid"},  # Invalid quantity format
        {},  # Empty payload
        {"invalid_field": "test"}  # Unknown fields
    ]
    
    for i, test_case in enumerate(test_cases):
        response = requests.post(
            "http://localhost:8501/api/v1/compliance/validate",
            json=test_case
        )
        
        print(f"Test Case {i+1}: Status {response.status_code}")
        if response.status_code != 200:
            print(f"  Error: {response.json().get('error', 'Unknown error')}")
```

---

## 📈 **Monitoring and Analytics**

### **1. Test Results Dashboard**

Access the built-in analytics at:
- **Dashboard**: `http://localhost:8501/📊_Dashboard`
- **Reports**: `http://localhost:8501/📄_Reports`
- **Admin Panel**: `http://localhost:8501/👑_Admin_Dashboard`

### **2. API Metrics**

```python
def get_api_metrics():
    """Get API usage statistics"""
    response = requests.get("http://localhost:8501/api/v1/metrics")
    metrics = response.json()
    
    print(f"Total API Calls: {metrics['total_calls']}")
    print(f"Success Rate: {metrics['success_rate']}%")
    print(f"Average Response Time: {metrics['avg_response_time']}ms")
    
    return metrics
```

---

## 🛡️ **Security Testing**

### **1. Authentication Testing**

```python
def test_api_security():
    """Test API security measures"""
    
    # Test without authentication
    response = requests.post(
        "http://localhost:8501/api/v1/compliance/validate",
        json={"title": "Test"}
    )
    
    print(f"Unauthenticated request: {response.status_code}")
    
    # Test with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.post(
        "http://localhost:8501/api/v1/compliance/validate",
        json={"title": "Test"},
        headers=headers
    )
    
    print(f"Invalid token request: {response.status_code}")
```

### **2. Rate Limiting Testing**

```python
def test_rate_limiting():
    """Test API rate limiting"""
    
    for i in range(100):  # Send 100 rapid requests
        response = requests.post(
            "http://localhost:8501/api/v1/compliance/validate",
            json={"title": f"Test Product {i}"}
        )
        
        if response.status_code == 429:  # Rate limited
            print(f"Rate limited after {i} requests")
            break
            
        time.sleep(0.1)
```

---

## 📝 **Best Practices**

### **1. Test Data Management**

- Use the provided sample data in `app/data/samples/`
- Create realistic test scenarios with actual product data
- Test edge cases and boundary conditions
- Maintain separate test datasets for different categories

### **2. API Testing Guidelines**

- Always test in sandbox mode first
- Validate response formats and status codes
- Test error handling and edge cases
- Monitor API performance and response times
- Document test results and findings

### **3. Continuous Testing**

```bash
# Set up automated testing
crontab -e

# Add this line to run tests daily at 2 AM
0 2 * * * cd /path/to/project && python test_sandbox_api.py >> test_log.txt
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **API Not Responding**
   ```bash
   # Check if Streamlit is running
   ps aux | grep streamlit
   
   # Restart if needed
   streamlit run app/streamlit_app.py
   ```

2. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

3. **Database Connection Issues**
   ```bash
   # Check data directory permissions
   ls -la app/data/
   
   # Reset database if needed
   rm app/data/*.jsonl
   python setup.py
   ```

### **Debug Mode**

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run tests with verbose output
PYTHONPATH=app python -v test_sandbox_api.py
```

---

## 📞 **Support and Resources**

### **Documentation**
- **Technical Docs**: `TECHNICAL_DOCUMENTATION.md`
- **Setup Guide**: `FINAL_SETUP_GUIDE.md`
- **API Reference**: Available in the web interface

### **Sample Data**
- **Product Images**: `app/data/samples/`
- **Test Dataset**: `app/data/sample_dataset/`
- **Configuration**: `app/data/rules/`

### **Contact**
For technical support or questions about the sandbox API testing:
- Check the logs in `app/data/audit_log.jsonl`
- Review error messages in the Streamlit interface
- Consult the built-in help system at `http://localhost:8501/❓_Help`

---

## 🎉 **Getting Started Checklist**

- [ ] Environment set up and dependencies installed
- [ ] Streamlit application running on port 8501
- [ ] Sample API calls tested successfully
- [ ] Test data uploaded and processed
- [ ] Compliance validation working
- [ ] Web crawler functionality tested
- [ ] Performance metrics collected
- [ ] Error handling verified
- [ ] Security measures tested
- [ ] Documentation reviewed

**You're now ready to test your legal metrology compliance solutions using the sandbox e-commerce API!**
