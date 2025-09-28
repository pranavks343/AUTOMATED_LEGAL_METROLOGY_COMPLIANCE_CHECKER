import streamlit as st
from datetime import datetime
import json
from PIL import Image
import io

from core.auth import require_auth, get_current_user
from core.barcode_scanner import get_barcode_scanner, BarcodeData
from core.schemas import ExtractedFields
from core.rules_engine import load_rules, validate
from core.json_utils import safe_json_dumps

st.set_page_config(page_title="Barcode Scanner - Legal Metrology Checker", page_icon="📷", layout="wide")

# Enhanced Custom CSS for Barcode Scanner Page
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Scanner Header */
    .scanner-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .scanner-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Scanner Container */
    .scanner-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Product Info Card */
    .product-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Compliance Status */
    .compliance-status {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 600;
        text-align: center;
    }
    
    .compliance-status.compliant {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
    }
    
    .compliance-status.non-compliant {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
    }
    
    /* API Status */
    .api-status {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .api-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .api-badge.available {
        background: #28a745;
        color: white;
    }
    
    .api-badge.unavailable {
        background: #6c757d;
        color: white;
    }
    
    .api-badge.premium {
        background: #ffc107;
        color: #212529;
    }
</style>
""", unsafe_allow_html=True)

# Require authentication
require_auth()
current_user = get_current_user()

# Enhanced Scanner Header
st.markdown(f"""
<div class="scanner-header">
    <h1>📷 Barcode Scanner</h1>
    <p>Welcome, <strong>{current_user.username}</strong>! Scan product barcodes for instant compliance checking.</p>
    <p><small>Supports EAN-13, UPC-A, and other standard barcode formats</small></p>
</div>
""", unsafe_allow_html=True)

# Initialize barcode scanner
scanner = get_barcode_scanner()

# Initialize session state
if "scanned_products" not in st.session_state:
    st.session_state.scanned_products = []
if "current_barcode_data" not in st.session_state:
    st.session_state.current_barcode_data = None

# Main scanner interface
st.markdown('<div class="scanner-container">', unsafe_allow_html=True)

# Display API status
st.markdown("### 🔌 Available Barcode APIs")
api_info = scanner.get_available_apis()

api_badges = []
for api_name, info in api_info.items():
    if info['available']:
        if info['free']:
            badge_class = "available"
            status = "✅ Free"
        else:
            badge_class = "premium"
            status = "🔑 Premium (API Key Configured)"
    else:
        badge_class = "unavailable"
        status = "❌ Requires API Key"
    
    api_badges.append(f'<span class="api-badge {badge_class}">{info["name"]}: {status}</span>')

st.markdown(f'<div class="api-status">{"".join(api_badges)}</div>', unsafe_allow_html=True)

# Show configuration help if premium APIs are not configured
premium_apis_missing = any(not info['available'] and not info['free'] for info in api_info.values())
if premium_apis_missing:
    st.info("""
    **🔧 API Configuration**: Some premium APIs require API keys. 
    Free APIs (Open Food Facts, UPC Item DB) are working and will be used automatically.
    
    To enable premium APIs, add your API keys to `.streamlit/secrets.toml`:
    ```toml
    [barcode_apis]
    BARCODE_LOOKUP_API_KEY = "your_api_key_here"
    ```
    """)

# Scanning options
st.markdown("### 📱 Scan Barcode")

tab1, tab2, tab3 = st.tabs(["📷 Upload Image", "🔢 Manual Entry", "📋 Recent Scans"])

with tab1:
    st.markdown("**Upload an image containing a barcode:**")
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image with a visible barcode - detection will start automatically!"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            # Automatically start scanning when image is uploaded
            with st.spinner("🔍 Automatically detecting barcodes..."):
                # Extract barcodes with visualization
                barcodes, annotated_image = scanner.scan_barcode_with_visualization(image)
                
                if barcodes:
                    st.success(f"🎯 Automatically detected {len(barcodes)} barcode(s)!")
                    
                    # Show annotated image if available
                    if annotated_image:
                        st.image(annotated_image, caption="🎯 Detected Barcodes", use_column_width=True)
                    
                    # Process each detected barcode
                    for i, barcode in enumerate(barcodes):
                        st.write(f"**Barcode {i+1}:** `{barcode}`")
                        
                        # Validate barcode
                        is_valid, validation_msg = scanner.validate_barcode(barcode)
                        
                        if is_valid:
                            st.success(f"✅ {validation_msg}")
                            
                            # Automatically look up product data for the first valid barcode
                            if i == 0:  # Process first barcode automatically
                                with st.spinner(f"🔍 Auto-looking up product data for {barcode}..."):
                                    barcode_data = scanner.lookup_barcode(barcode)
                                    
                                    if barcode_data:
                                        st.session_state.current_barcode_data = barcode_data
                                        st.success(f"✅ Product found via {barcode_data.source_api}!")
                                        # Auto-scroll to results
                                        st.balloons()
                                    else:
                                        st.warning("⚠️ Product not found in any database")
                            else:
                                # For additional barcodes, show lookup button
                                if st.button(f"🔍 Look up Barcode {i+1}", key=f"lookup_{i}"):
                                    with st.spinner(f"Looking up product data for {barcode}..."):
                                        barcode_data = scanner.lookup_barcode(barcode)
                                        
                                        if barcode_data:
                                            st.session_state.current_barcode_data = barcode_data
                                            st.success(f"✅ Product found via {barcode_data.source_api}!")
                                            st.rerun()
                                        else:
                                            st.warning("⚠️ Product not found in any database")
                        else:
                            st.error(f"❌ {validation_msg}")
                else:
                    st.warning("⚠️ No barcodes automatically detected in the image.")
                    st.info("💡 **Tips for better detection:**")
                    st.markdown("""
                    - Ensure good lighting and contrast
                    - Keep the barcode straight and unobstructed  
                    - Try cropping the image to focus on the barcode
                    - Make sure the barcode is not blurry or damaged
                    """)
                    
                    # Enhanced manual scan button as fallback
                    if st.button("🔄 Try Enhanced Detection", type="secondary"):
                        with st.spinner("Trying enhanced barcode detection with preprocessing..."):
                            # Try with enhanced image preprocessing
                            barcodes_manual = scanner.scan_barcode_from_image(image)
                            
                            if barcodes_manual:
                                st.success(f"🎉 Found {len(barcodes_manual)} barcode(s) with enhanced detection!")
                                for j, barcode in enumerate(barcodes_manual):
                                    st.write(f"**Enhanced Detection {j+1}:** `{barcode}`")
                                    
                                    # Auto-lookup for first detected barcode
                                    if j == 0:
                                        with st.spinner(f"Looking up product data for {barcode}..."):
                                            barcode_data = scanner.lookup_barcode(barcode)
                                            if barcode_data:
                                                st.session_state.current_barcode_data = barcode_data
                                                st.success(f"✅ Product found via {barcode_data.source_api}!")
                                                st.rerun()
                            else:
                                st.error("❌ Still no barcodes detected. Please try:")
                                st.markdown("""
                                - A different angle or lighting
                                - Cropping the image closer to the barcode
                                - A higher resolution image
                                - Manual entry if you can read the numbers
                                """)

with tab2:
    st.markdown("**Enter barcode manually:**")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        manual_barcode = st.text_input(
            "Barcode Number",
            placeholder="Enter 8, 12, or 13 digit barcode",
            help="Common formats: EAN-13 (13 digits), UPC-A (12 digits), EAN-8 (8 digits)"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("🔍 Look Up", type="primary", disabled=not manual_barcode):
            if manual_barcode:
                # Validate barcode
                is_valid, validation_msg = scanner.validate_barcode(manual_barcode)
                
                if is_valid:
                    st.success(f"✅ {validation_msg}")
                    
                    # Look up product data
                    with st.spinner(f"Looking up product data for {manual_barcode}..."):
                        barcode_data = scanner.lookup_barcode(manual_barcode)
                        
                        if barcode_data:
                            st.session_state.current_barcode_data = barcode_data
                            st.success(f"✅ Product found via {barcode_data.source_api}!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Product not found in any database")
                else:
                    st.error(f"❌ {validation_msg}")

with tab3:
    st.markdown("**Recently Scanned Products:**")
    
    if st.session_state.scanned_products:
        for i, product in enumerate(reversed(st.session_state.scanned_products[-10:])):  # Show last 10
            with st.expander(f"📦 {product['product_name']} - {product['barcode']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Brand:** {product['brand']}")
                    st.write(f"**Category:** {product['category']}")
                    st.write(f"**Source:** {product['source_api']}")
                    st.write(f"**Scanned:** {product['scan_time']}")
                
                with col2:
                    if st.button(f"🔄 Re-analyze", key=f"reanalyze_{i}"):
                        # Recreate BarcodeData object and set as current
                        barcode_data = BarcodeData(
                            barcode=product['barcode'],
                            format=product.get('format', 'Unknown'),
                            product_name=product['product_name'],
                            brand=product['brand'],
                            manufacturer=product.get('manufacturer', ''),
                            category=product['category'],
                            source_api=product['source_api']
                        )
                        st.session_state.current_barcode_data = barcode_data
                        st.rerun()
    else:
        st.info("No recent scans available. Scan your first barcode above!")

st.markdown('</div>', unsafe_allow_html=True)

# Display current barcode data and compliance analysis
if st.session_state.current_barcode_data:
    barcode_data = st.session_state.current_barcode_data
    
    st.markdown("---")
    st.markdown("### 📦 Product Information")
    
    # Product info card
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### {barcode_data.product_name}")
        st.write(f"**Barcode:** `{barcode_data.barcode}`")
        st.write(f"**Brand:** {barcode_data.brand}")
        st.write(f"**Category:** {barcode_data.category}")
        if barcode_data.description:
            st.write(f"**Description:** {barcode_data.description}")
    
    with col2:
        st.write(f"**Source:** {barcode_data.source_api}")
        st.write(f"**Confidence:** {barcode_data.confidence*100:.1f}%")
        if barcode_data.net_weight:
            st.write(f"**Net Weight:** {barcode_data.net_weight}")
        if barcode_data.country_of_origin:
            st.write(f"**Origin:** {barcode_data.country_of_origin}")
    
    with col3:
        # Display product image if available
        if barcode_data.images:
            try:
                st.image(barcode_data.images[0], caption="Product Image", width=150)
            except:
                st.write("📷 Image not available")
        else:
            st.write("📷 No image available")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Extract compliance fields
    compliance_fields = scanner.extract_compliance_fields(barcode_data)
    
    # Convert to ExtractedFields for validation
    extracted_fields = ExtractedFields(
        manufacturer_name=compliance_fields.get('manufacturer_name', ''),
        mrp_raw=compliance_fields.get('mrp_raw', ''),
        net_quantity_raw=compliance_fields.get('net_quantity_raw', ''),
        country_of_origin=compliance_fields.get('country_of_origin', ''),
        extra={
            'barcode': barcode_data.barcode,
            'category': barcode_data.category,
            'ingredients': compliance_fields.get('ingredients', ''),
            'data_source': compliance_fields.get('data_source', ''),
            'confidence_score': compliance_fields.get('confidence_score', 0)
        }
    )
    
    # Perform compliance validation
    st.markdown("### ⚖️ Legal Metrology Compliance Analysis")
    
    with st.spinner("Validating compliance..."):
        # Load rules and validate
        rules = load_rules("app/data/rules/legal_metrology_rules.yaml")
        validation_result = validate(extracted_fields, rules)
    
    # Display compliance status
    status_class = "compliant" if validation_result.is_compliant else "non-compliant"
    status_text = "✅ COMPLIANT" if validation_result.is_compliant else "❌ NON-COMPLIANT"
    
    st.markdown(f'''
    <div class="compliance-status {status_class}">
        <h3>{status_text}</h3>
        <p>Compliance Score: {validation_result.score}/100</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Display detailed compliance results
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📊 Extracted Fields")
        st.json({
            "Manufacturer": extracted_fields.manufacturer_name,
            "MRP": extracted_fields.mrp_raw,
            "Net Quantity": extracted_fields.net_quantity_raw,
            "Unit": extracted_fields.unit,
            "Country of Origin": extracted_fields.country_of_origin,
            "Manufacturing Date": extracted_fields.mfg_date,
            "Expiry Date": extracted_fields.expiry_date,
            "Batch Number": extracted_fields.batch_number,
            "FSSAI Number": extracted_fields.fssai_number,
            "Barcode": barcode_data.barcode
        })
    
    with col2:
        st.markdown("#### 🚨 Compliance Issues")
        if validation_result.issues:
            for issue in validation_result.issues:
                level_icon = "🔴" if issue.level == "error" else "🟡"
                st.write(f"{level_icon} **{issue.field}**: {issue.message}")
        else:
            st.success("🎉 No compliance issues found!")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("💾 Save Product", type="primary"):
            # Add to scanned products history
            product_record = {
                'barcode': barcode_data.barcode,
                'product_name': barcode_data.product_name or 'Unknown Product',
                'brand': barcode_data.brand,
                'category': barcode_data.category,
                'manufacturer': barcode_data.manufacturer,
                'source_api': barcode_data.source_api,
                'compliance_score': validation_result.score,
                'is_compliant': validation_result.is_compliant,
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.session_state.scanned_products.append(product_record)
            st.success("✅ Product saved to history!")
    
    with col2:
        if st.button("📄 Generate Report"):
            # Generate compliance report
            report_data = {
                'product_info': {
                    'barcode': barcode_data.barcode,
                    'name': barcode_data.product_name,
                    'brand': barcode_data.brand,
                    'manufacturer': barcode_data.manufacturer
                },
                'compliance': {
                    'score': validation_result.score,
                    'is_compliant': validation_result.is_compliant,
                    'issues': [{'field': i.field, 'level': i.level, 'message': i.message} for i in validation_result.issues]
                },
                'scan_details': {
                    'source': barcode_data.source_api,
                    'confidence': barcode_data.confidence,
                    'scan_time': datetime.now().isoformat()
                }
            }
            
            st.download_button(
                label="📥 Download Report",
                data=safe_json_dumps(report_data, indent=2),
                file_name=f"compliance_report_{barcode_data.barcode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("🔄 Scan Another"):
            st.session_state.current_barcode_data = None
            st.rerun()
    
    with col4:
        if st.button("📊 View Dashboard"):
            st.switch_page("pages/4_📊_Dashboard.py")

# Physical Scanner Integration
st.markdown("---")
st.markdown("### 🔌 Physical Scanner Integration")

col1, col2 = st.columns([2, 1])

with col1:
    st.info("""
    **🚀 New Feature: Physical Barcode Scanner Support!**
    
    Connect external USB, Serial, or Bluetooth barcode scanners for:
    - ⚡ Real-time barcode scanning
    - 🎯 Higher accuracy and speed
    - 🔄 Continuous scanning mode
    - 📊 Professional-grade scanning
    """)

with col2:
    if st.button("🔌 Open Physical Scanner", type="primary"):
        st.switch_page("pages/17_🔌_Physical_Scanner.py")

# Help section
st.markdown("---")
st.markdown("### ❓ Help & Tips")

with st.expander("📋 How to use the Barcode Scanner"):
    st.markdown("""
    **🚀 Automatic Detection Features:**
    - **Instant Scanning**: Barcodes are automatically detected when you upload an image
    - **Visual Feedback**: Green boxes highlight detected barcode regions
    - **Auto-Lookup**: Product information is automatically retrieved for the first detected barcode
    - **Enhanced Processing**: Multiple detection algorithms with image preprocessing
    
    **📱 Scanning Methods:**
    1. **Image Upload**: Upload a clear photo - detection starts automatically!
    2. **Manual Entry**: Type the barcode number directly
    3. **Recent Scans**: Review and re-analyze previously scanned products
    
    **💡 Best Practices for Image Upload:**
    - Ensure good lighting and high contrast
    - Keep the barcode straight and unobstructed
    - Make sure the entire barcode is visible and in focus
    - Crop the image to focus on the barcode area
    - Avoid shadows, reflections, or glare
    
    **🔧 If Auto-Detection Fails:**
    - Try the "Enhanced Detection" button for advanced preprocessing
    - Adjust lighting or take a new photo
    - Crop the image closer to the barcode
    - Use manual entry as a fallback
    
    **📊 Supported Formats:**
    - EAN-13 (13 digits) - Most common international format
    - UPC-A (12 digits) - Common in North America
    - EAN-8 (8 digits) - Short format for small products
    - ITF-14 (14 digits) - Used for shipping containers
    
    **🔌 API Information:**
    - **Open Food Facts**: Free, comprehensive food database
    - **UPC Item DB**: Free general product database
    - **Barcode Lookup**: Premium service (requires API key)
    """)

with st.expander("⚖️ Legal Metrology Compliance"):
    st.markdown("""
    **Required Information for E-commerce:**
    - **Product Name**: Generic/common name of the product
    - **MRP**: Maximum Retail Price in Indian Rupees (₹)
    - **Net Quantity**: Weight/volume with proper units (g, kg, ml, l)
    - **Manufacturer Details**: Name and complete address
    - **Country of Origin**: Manufacturing country (mandatory for imports)
    
    **Compliance Scoring:**
    - **90-100**: Excellent compliance, ready for listing
    - **80-89**: Good compliance, minor issues to address
    - **60-79**: Moderate issues, requires attention
    - **Below 60**: Significant issues, cannot list until resolved
    
    **Common Issues:**
    - Missing MRP declaration
    - Incomplete manufacturer information
    - Incorrect or missing net quantity units
    - Missing country of origin for imported products
    """)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Barcode Scanner | User: {current_user.username} | 
    Session: {datetime.now().strftime('%Y-%m-%d %H:%M')} |
    Products Scanned: {len(st.session_state.scanned_products)}
</div>
""", unsafe_allow_html=True)
