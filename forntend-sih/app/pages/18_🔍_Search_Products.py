import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from core.auth import get_current_user
from core.erp_manager import (
    erp_manager, ProductStatus, ProductCategory, ProductData
)
from core.audit_logger import log_user_action
from core.json_utils import safe_json_dumps
import difflib
from typing import List, Dict, Any, Optional, Tuple

st.set_page_config(page_title="Product Search & Verification - Legal Metrology Checker", page_icon="🔍", layout="wide")

# Enhanced Custom CSS for Product Search
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Search Header */
    .search-header {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .search-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="search" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="2" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23search)"/></svg>');
        opacity: 0.1;
    }
    
    .search-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    /* Search Results Cards */
    .search-result-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .search-result-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .search-result-card.exact-match {
        border-left: 6px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    .search-result-card.similar-match {
        border-left: 6px solid #FF9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
    }
    
    .search-result-card.new-product {
        border-left: 6px solid #2196F3;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%);
    }
    
    /* Match Score Badges */
    .match-score {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .match-score.exact {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
    }
    
    .match-score.high {
        background: linear-gradient(135deg, #8BC34A 0%, #7CB342 100%);
        color: white;
    }
    
    .match-score.medium {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        color: white;
    }
    
    .match-score.low {
        background: linear-gradient(135deg, #FFC107 0%, #FFA000 100%);
        color: #333;
    }
    
    .match-score.new {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
    }
    
    /* Product Comparison Table */
    .comparison-table {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .comparison-table table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .comparison-table th {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
    }
    
    .comparison-table td {
        padding: 1rem;
        border-bottom: 1px solid #e0e0e0;
        vertical-align: top;
    }
    
    .comparison-table tr:nth-child(even) {
        background: rgba(76, 175, 80, 0.05);
    }
    
    /* Alert Styling */
    .alert-success {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
        border: 1px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #2E7D32;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
        border: 1px solid #FF9800;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #E65100;
    }
    
    .alert-info {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%);
        border: 1px solid #2196F3;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0D47A1;
    }
    
    /* Search Form Styling */
    .search-form-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .search-form-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    /* Statistics Cards */
    .stat-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #e0e0e0;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .stat-card h3 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
""", unsafe_allow_html=True)

# Get current user
current_user = get_current_user()

# Enhanced Search Header
st.markdown(f"""
<div class="search-header">
    <h1>🔍 Product Search & Verification</h1>
    <p>Welcome, <strong>{current_user.username}</strong>! Search existing products and detect duplicates before adding new items to ERP.</p>
</div>
""", unsafe_allow_html=True)

class ProductSearchEngine:
    """Advanced product search and matching engine"""
    
    def __init__(self):
        self.erp_manager = erp_manager
    
    def calculate_product_similarity(self, product1: Dict[str, Any], product2: ProductData) -> float:
        """Calculate similarity score between two products (0-100)"""
        score = 0.0
        total_weight = 0.0
        
        # Product name similarity (weight: 40%)
        name_similarity = difflib.SequenceMatcher(
            None, 
            product1.get('product_name', '').lower(), 
            product2.product_name.lower()
        ).ratio()
        score += name_similarity * 40
        total_weight += 40
        
        # Manufacturer similarity (weight: 25%)
        manufacturer_similarity = difflib.SequenceMatcher(
            None, 
            product1.get('manufacturer_name', '').lower(), 
            product2.manufacturer_name.lower()
        ).ratio()
        score += manufacturer_similarity * 25
        total_weight += 25
        
        # MRP similarity (weight: 15%)
        mrp1 = float(product1.get('mrp', 0))
        mrp2 = float(product2.mrp)
        if mrp1 > 0 and mrp2 > 0:
            mrp_diff = abs(mrp1 - mrp2) / max(mrp1, mrp2)
            mrp_similarity = max(0, 1 - mrp_diff)
            score += mrp_similarity * 15
            total_weight += 15
        
        # Net quantity similarity (weight: 10%)
        qty1 = float(product1.get('net_quantity', 0))
        qty2 = float(product2.net_quantity)
        if qty1 > 0 and qty2 > 0:
            qty_diff = abs(qty1 - qty2) / max(qty1, qty2)
            qty_similarity = max(0, 1 - qty_diff)
            score += qty_similarity * 10
            total_weight += 10
        
        # Unit exact match (weight: 5%)
        if product1.get('unit', '').lower() == product2.unit.lower():
            score += 5
        total_weight += 5
        
        # Category similarity (weight: 5%)
        if product1.get('category', '').upper() == product2.category.value:
            score += 5
        total_weight += 5
        
        return (score / total_weight) * 100 if total_weight > 0 else 0
    
    def search_similar_products(self, search_product: Dict[str, Any], 
                               similarity_threshold: float = 50.0) -> List[Tuple[ProductData, float]]:
        """Search for similar products in ERP system"""
        all_products = self.erp_manager.get_all_products()
        similar_products = []
        
        for existing_product in all_products:
            similarity_score = self.calculate_product_similarity(search_product, existing_product)
            
            if similarity_score >= similarity_threshold:
                similar_products.append((existing_product, similarity_score))
        
        # Sort by similarity score (highest first)
        similar_products.sort(key=lambda x: x[1], reverse=True)
        
        return similar_products
    
    def check_exact_match(self, search_product: Dict[str, Any]) -> Optional[ProductData]:
        """Check for exact product matches"""
        for existing_product in self.erp_manager.get_all_products():
            if (search_product.get('product_name', '').lower() == existing_product.product_name.lower() and
                search_product.get('manufacturer_name', '').lower() == existing_product.manufacturer_name.lower() and
                abs(float(search_product.get('mrp', 0)) - float(existing_product.mrp)) < 0.01 and
                abs(float(search_product.get('net_quantity', 0)) - float(existing_product.net_quantity)) < 0.01 and
                search_product.get('unit', '').lower() == existing_product.unit.lower()):
                return existing_product
        return None
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search and product statistics"""
        stats = self.erp_manager.get_product_statistics()
        return {
            "total_products": stats["total_products"],
            "unique_manufacturers": len(set(p.manufacturer_name for p in self.erp_manager.get_all_products())),
            "categories_covered": len([cat for cat, count in stats["by_category"].items() if count > 0]),
            "compliance_rate": round((stats["by_compliance"]["COMPLIANT"] / max(stats["total_products"], 1)) * 100, 2)
        }

# Initialize search engine
search_engine = ProductSearchEngine()

# Display statistics
stats = search_engine.get_search_statistics()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <h3>{stats['total_products']}</h3>
        <p>Total Products</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <h3>{stats['unique_manufacturers']}</h3>
        <p>Manufacturers</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <h3>{stats['categories_covered']}</h3>
        <p>Categories</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <h3>{stats['compliance_rate']}%</h3>
        <p>Compliance Rate</p>
    </div>
    """, unsafe_allow_html=True)

# Create tabs for different search functionalities
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Product Search", "📷 Image Verification", "📊 Bulk Verification", "📈 Search Analytics"])

with tab1:
    st.markdown("### 🔍 Product Search & Duplicate Detection")
    
    st.markdown("""
    <div class="search-form-card">
    """, unsafe_allow_html=True)
    
    with st.form("product_search_form"):
        st.markdown("**Enter Product Details to Search:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_product_name = st.text_input(
                "Product Name *",
                placeholder="Enter product name to search",
                help="Product name as it appears on packaging"
            )
            
            search_mrp = st.number_input(
                "MRP (Maximum Retail Price)",
                min_value=0.01,
                step=0.01,
                format="%.2f",
                help="Maximum retail price in INR (optional for broader search)"
            )
            
            search_net_quantity = st.number_input(
                "Net Quantity",
                min_value=0.01,
                step=0.01,
                format="%.2f",
                help="Net quantity of the product (optional)"
            )
        
        with col2:
            search_manufacturer_name = st.text_input(
                "Manufacturer Name",
                placeholder="Enter manufacturer name",
                help="Name of the manufacturing company (optional)"
            )
            
            search_unit = st.selectbox(
                "Unit",
                options=["", "g", "kg", "ml", "l", "L", "pcs", "piece", "pack", "gm", "mg"],
                help="Unit of measurement (optional)"
            )
            
            search_category = st.selectbox(
                "Product Category",
                options=[""] + [cat.value for cat in ProductCategory],
                format_func=lambda x: x.replace("_", " ").title() if x else "Any Category",
                help="Select the product category (optional)"
            )
        
        # Search settings
        similarity_threshold = st.slider(
            "Similarity Threshold (%)",
            min_value=30,
            max_value=100,
            value=70,
            help="Minimum similarity percentage to show matches"
        )
        
        submitted = st.form_submit_button("🔍 Search Products", type="primary")
        
        if submitted:
            if not search_product_name:
                st.error("Please enter at least a product name to search.")
            else:
                # Prepare search product data
                search_product = {
                    'product_name': search_product_name,
                    'manufacturer_name': search_manufacturer_name or '',
                    'mrp': search_mrp if search_mrp > 0 else 0,
                    'net_quantity': search_net_quantity if search_net_quantity > 0 else 0,
                    'unit': search_unit or '',
                    'category': search_category or ''
                }
                
                # Check for exact matches first
                exact_match = search_engine.check_exact_match(search_product)
                
                if exact_match:
                    st.markdown(f"""
                    <div class="alert-success">
                        <h3>✅ Exact Match Found!</h3>
                        <p><strong>Product already exists in ERP system:</strong></p>
                        <ul>
                            <li><strong>SKU:</strong> {exact_match.sku}</li>
                            <li><strong>Status:</strong> {exact_match.status.value}</li>
                            <li><strong>Created:</strong> {exact_match.created_date[:10]}</li>
                        </ul>
                        <p>This product is already in the system. No need to add again.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show detailed product information
                    with st.expander("📋 View Complete Product Details"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Product Name:** {exact_match.product_name}")
                            st.markdown(f"**Manufacturer:** {exact_match.manufacturer_name}")
                            st.markdown(f"**MRP:** ₹{exact_match.mrp}")
                            st.markdown(f"**Net Quantity:** {exact_match.net_quantity} {exact_match.unit}")
                            st.markdown(f"**Category:** {exact_match.category.value.replace('_', ' ').title()}")
                        
                        with col2:
                            st.markdown(f"**Status:** {exact_match.status.value.replace('_', ' ').title()}")
                            st.markdown(f"**Created By:** {exact_match.created_by}")
                            st.markdown(f"**Created Date:** {exact_match.created_date[:10]}")
                            if exact_match.compliance_status:
                                st.markdown(f"**Compliance Status:** {exact_match.compliance_status}")
                            if exact_match.tags:
                                st.markdown(f"**Tags:** {', '.join(exact_match.tags)}")
                
                else:
                    # Search for similar products
                    similar_products = search_engine.search_similar_products(
                        search_product, 
                        similarity_threshold
                    )
                    
                    if similar_products:
                        st.markdown(f"""
                        <div class="alert-warning">
                            <h3>⚠️ Similar Products Found!</h3>
                            <p>Found <strong>{len(similar_products)}</strong> similar product(s) in the ERP system. Please review before adding a new product.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for i, (product, similarity_score) in enumerate(similar_products):
                            # Determine match category
                            if similarity_score >= 90:
                                match_class = "exact-match"
                                score_class = "exact"
                                match_text = "Near Exact Match"
                            elif similarity_score >= 80:
                                match_class = "similar-match"
                                score_class = "high"
                                match_text = "High Similarity"
                            elif similarity_score >= 70:
                                match_class = "similar-match"
                                score_class = "medium"
                                match_text = "Medium Similarity"
                            else:
                                match_class = "similar-match"
                                score_class = "low"
                                match_text = "Low Similarity"
                            
                            st.markdown(f"""
                            <div class="search-result-card {match_class}">
                                <div class="match-score {score_class}">{match_text}: {similarity_score:.1f}%</div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.markdown(f"**SKU:** {product.sku}")
                                st.markdown(f"**Product Name:** {product.product_name}")
                                st.markdown(f"**Manufacturer:** {product.manufacturer_name}")
                                st.markdown(f"**MRP:** ₹{product.mrp}")
                                st.markdown(f"**Net Quantity:** {product.net_quantity} {product.unit}")
                                st.markdown(f"**Category:** {product.category.value.replace('_', ' ').title()}")
                                st.markdown(f"**Status:** {product.status.value.replace('_', ' ').title()}")
                            
                            with col2:
                                st.markdown(f"**Created:** {product.created_date[:10]}")
                                st.markdown(f"**Created By:** {product.created_by}")
                                if product.compliance_status:
                                    st.markdown(f"**Compliance:** {product.compliance_status}")
                                if product.tags:
                                    st.markdown(f"**Tags:** {', '.join(product.tags[:3])}{'...' if len(product.tags) > 3 else ''}")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    else:
                        st.markdown(f"""
                        <div class="alert-info">
                            <h3>🆕 New Product Detected!</h3>
                            <p>No similar products found in the ERP system with similarity above {similarity_threshold}%.</p>
                            <p><strong>This appears to be a new product that can be safely added to the ERP system.</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show what would be added
                        st.markdown("**Product Details to be Added:**")
                        
                        product_data = {
                            "Product Name": search_product_name,
                            "Manufacturer": search_manufacturer_name or "Not specified",
                            "MRP": f"₹{search_mrp}" if search_mrp > 0 else "Not specified",
                            "Net Quantity": f"{search_net_quantity} {search_unit}" if search_net_quantity > 0 and search_unit else "Not specified",
                            "Category": search_category.replace('_', ' ').title() if search_category else "Not specified"
                        }
                        
                        df = pd.DataFrame(list(product_data.items()), columns=["Field", "Value"])
                        st.table(df)
                
                # Log the search action
                log_user_action(
                    current_user.username,
                    "PRODUCT_SEARCH",
                    "product_search",
                    {
                        "search_product": search_product_name,
                        "manufacturer": search_manufacturer_name,
                        "exact_match_found": exact_match is not None,
                        "similar_products_count": len(similar_products) if 'similar_products' in locals() else 0
                    }
                )
    
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📷 Image-Based Product Verification")
    st.markdown("Upload a product image to verify if it matches existing products in the ERP system.")
    
    # Image verification options
    verification_mode = st.radio(
        "Verification Mode:",
        options=["Find Best Match", "Verify Specific Product"],
        help="Choose whether to find the best matching product or verify against a specific SKU"
    )
    
    if verification_mode == "Verify Specific Product":
        # Get list of all products for selection
        all_products = erp_manager.get_all_products()
        if all_products:
            product_options = {f"{p.sku} - {p.product_name}": p.sku for p in all_products}
            selected_product = st.selectbox(
                "Select Product to Verify Against:",
                options=list(product_options.keys()),
                help="Choose the ERP product to verify the image against"
            )
            target_sku = product_options[selected_product] if selected_product else None
        else:
            st.error("No products found in ERP system.")
            target_sku = None
    else:
        target_sku = None
    
    # Image upload
    uploaded_image = st.file_uploader(
        "Upload Product Image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of the product label/packaging"
    )
    
    if uploaded_image is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            st.markdown("**Image Analysis Options:**")
            
            # Analysis settings
            show_extracted_text = st.checkbox("Show Extracted Text", value=True)
            show_detailed_scores = st.checkbox("Show Detailed Match Scores", value=False)
            
            if st.button("🔍 Analyze Image", type="primary"):
                with st.spinner("Analyzing image and matching with ERP data..."):
                    try:
                        # Read image bytes
                        image_bytes = uploaded_image.read()
                        uploaded_image.seek(0)  # Reset file pointer
                        
                        # Perform verification
                        if verification_mode == "Verify Specific Product" and target_sku:
                            result = image_product_matcher.verify_product_with_image(image_bytes, target_sku)
                        else:
                            result = image_product_matcher.find_best_matching_product(image_bytes)
                        
                        # Display results based on verification status
                        if result.verification_status == 'POSITIVE':
                            st.success(f"✅ **POSITIVE MATCH** (Confidence: {result.confidence_score:.1f}%)")
                            
                            if result.matched_product:
                                st.markdown("**Matched Product Details:**")
                                
                                match_col1, match_col2 = st.columns(2)
                                
                                with match_col1:
                                    st.info(f"**SKU:** {result.matched_product.sku}")
                                    st.info(f"**Product Name:** {result.matched_product.product_name}")
                                    st.info(f"**Manufacturer:** {result.matched_product.manufacturer_name}")
                                    st.info(f"**MRP:** ₹{result.matched_product.mrp}")
                                
                                with match_col2:
                                    st.info(f"**Net Quantity:** {result.matched_product.net_quantity} {result.matched_product.unit}")
                                    st.info(f"**Category:** {result.matched_product.category.value.replace('_', ' ').title()}")
                                    st.info(f"**Status:** {result.matched_product.status.value.replace('_', ' ').title()}")
                                    st.info(f"**Created:** {result.matched_product.created_date[:10]}")
                        
                        elif result.verification_status == 'UNCERTAIN':
                            st.warning(f"⚠️ **UNCERTAIN MATCH** (Confidence: {result.confidence_score:.1f}%)")
                            st.warning("The image partially matches the product data, but confidence is low.")
                            
                            if result.matched_product:
                                st.markdown("**Possible Matched Product:**")
                                st.info(f"SKU: {result.matched_product.sku} - {result.matched_product.product_name}")
                        
                        else:
                            st.error(f"❌ **NEGATIVE MATCH** (Confidence: {result.confidence_score:.1f}%)")
                            st.error("The image does not match any products in the ERP system.")
                        
                        # Show extracted data if requested
                        if show_extracted_text and result.extracted_data:
                            with st.expander("📝 Extracted Text from Image"):
                                extracted_text = result.match_details.get('extracted_text', 'No text extracted')
                                st.text_area("Extracted Text:", value=extracted_text, height=100)
                                
                                # Show parsed fields
                                st.markdown("**Parsed Fields:**")
                                fields_col1, fields_col2 = st.columns(2)
                                
                                with fields_col1:
                                    if result.extracted_data.mrp_value:
                                        st.write(f"**MRP:** ₹{result.extracted_data.mrp_value}")
                                    if result.extracted_data.net_quantity_value:
                                        st.write(f"**Quantity:** {result.extracted_data.net_quantity_value} {result.extracted_data.unit or ''}")
                                    if result.extracted_data.manufacturer_name:
                                        st.write(f"**Manufacturer:** {result.extracted_data.manufacturer_name}")
                                
                                with fields_col2:
                                    if result.extracted_data.mfg_date:
                                        st.write(f"**Mfg Date:** {result.extracted_data.mfg_date}")
                                    if result.extracted_data.batch_number:
                                        st.write(f"**Batch:** {result.extracted_data.batch_number}")
                                    if result.extracted_data.fssai_number:
                                        st.write(f"**FSSAI:** {result.extracted_data.fssai_number}")
                        
                        # Show detailed match scores if requested
                        if show_detailed_scores and 'field_scores' in result.match_details:
                            with st.expander("📊 Detailed Match Scores"):
                                field_scores = result.match_details['field_scores']
                                
                                for field, score in field_scores.items():
                                    # Color code based on score
                                    if score >= 80:
                                        st.success(f"{field.replace('_', ' ').title()}: {score:.1f}%")
                                    elif score >= 60:
                                        st.warning(f"{field.replace('_', ' ').title()}: {score:.1f}%")
                                    else:
                                        st.error(f"{field.replace('_', ' ').title()}: {score:.1f}%")
                        
                        # Show issues/notes
                        if result.issues:
                            st.markdown("**Analysis Notes:**")
                            for issue in result.issues:
                                if "match" in issue.lower() and "high confidence" in issue.lower():
                                    st.success(f"✅ {issue}")
                                elif "low similarity" in issue.lower():
                                    st.warning(f"⚠️ {issue}")
                                else:
                                    st.info(f"ℹ️ {issue}")
                        
                        # Log the verification action
                        log_user_action(
                            current_user.username,
                            "IMAGE_VERIFICATION",
                            "image_product_verification",
                            {
                                "verification_mode": verification_mode,
                                "target_sku": target_sku,
                                "verification_status": result.verification_status,
                                "confidence_score": result.confidence_score,
                                "matched_product_sku": result.matched_product.sku if result.matched_product else None
                            }
                        )
                    
                    except Exception as e:
                        st.error(f"Error analyzing image: {str(e)}")
    
    # Instructions and tips
    with st.expander("📋 Image Upload Tips"):
        st.markdown("""
        **For Best Results:**
        
        ✅ **Good Image Quality:**
        - High resolution (at least 1080p)
        - Clear, well-lit product label
        - Text is sharp and readable
        - Minimal shadows or glare
        
        ✅ **Proper Framing:**
        - Product label fills most of the frame
        - Straight-on angle (not tilted)
        - All important text is visible
        - No obstructions or hands in the way
        
        ✅ **Supported Information:**
        - MRP (Maximum Retail Price)
        - Net quantity and unit
        - Manufacturer name
        - Manufacturing/Expiry dates
        - Batch numbers and FSSAI numbers
        
        ❌ **Avoid:**
        - Blurry or low-resolution images
        - Poor lighting conditions
        - Extreme angles or distortion
        - Images with multiple products
        """)

with tab3:
    st.markdown("### 📊 Bulk Product Verification")
    st.markdown("Upload a CSV file with product data to check for existing products in bulk.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=['csv'],
        help="Upload a CSV file with columns: product_name, manufacturer_name, mrp, net_quantity, unit, category"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            required_columns = ['product_name']
            optional_columns = ['manufacturer_name', 'mrp', 'net_quantity', 'unit', 'category']
            
            if not all(col in df.columns for col in required_columns):
                st.error(f"CSV file must contain at least these columns: {', '.join(required_columns)}")
            else:
                st.success(f"✅ File uploaded successfully! Found {len(df)} products to verify.")
                
                # Show preview
                with st.expander("📋 Preview Uploaded Data"):
                    st.dataframe(df.head(10))
                
                if st.button("🔍 Start Bulk Verification", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = []
                    
                    for idx, row in df.iterrows():
                        progress = (idx + 1) / len(df)
                        progress_bar.progress(progress)
                        status_text.text(f"Verifying product {idx + 1} of {len(df)}: {row['product_name']}")
                        
                        # Prepare search product
                        search_product = {
                            'product_name': str(row.get('product_name', '')),
                            'manufacturer_name': str(row.get('manufacturer_name', '')),
                            'mrp': float(row.get('mrp', 0)) if pd.notna(row.get('mrp')) else 0,
                            'net_quantity': float(row.get('net_quantity', 0)) if pd.notna(row.get('net_quantity')) else 0,
                            'unit': str(row.get('unit', '')),
                            'category': str(row.get('category', ''))
                        }
                        
                        # Check for matches
                        exact_match = search_engine.check_exact_match(search_product)
                        similar_products = search_engine.search_similar_products(search_product, 70.0)
                        
                        if exact_match:
                            result_status = "Exact Match"
                            result_details = f"SKU: {exact_match.sku}"
                            result_color = "🟢"
                        elif similar_products:
                            best_match = similar_products[0]
                            result_status = f"Similar ({best_match[1]:.1f}%)"
                            result_details = f"Similar to SKU: {best_match[0].sku}"
                            result_color = "🟡"
                        else:
                            result_status = "New Product"
                            result_details = "Can be added to ERP"
                            result_color = "🔵"
                        
                        results.append({
                            'Product Name': search_product['product_name'],
                            'Manufacturer': search_product['manufacturer_name'],
                            'Status': result_status,
                            'Details': result_details,
                            'Icon': result_color
                        })
                    
                    status_text.text("✅ Bulk verification completed!")
                    progress_bar.progress(1.0)
                    
                    # Show results
                    st.markdown("### 📊 Verification Results")
                    
                    results_df = pd.DataFrame(results)
                    
                    # Summary statistics
                    col1, col2, col3 = st.columns(3)
                    
                    exact_matches = len([r for r in results if "Exact Match" in r['Status']])
                    similar_matches = len([r for r in results if "Similar" in r['Status']])
                    new_products = len([r for r in results if "New Product" in r['Status']])
                    
                    with col1:
                        st.metric("🟢 Exact Matches", exact_matches)
                    
                    with col2:
                        st.metric("🟡 Similar Products", similar_matches)
                    
                    with col3:
                        st.metric("🔵 New Products", new_products)
                    
                    # Detailed results
                    st.markdown("**Detailed Results:**")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Download results
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Verification Results",
                        data=csv_data,
                        file_name=f"product_verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

with tab4:
    st.markdown("### 📈 Search Analytics & Insights")
    
    # Get detailed analytics
    all_products = erp_manager.get_all_products()
    
    if all_products:
        # Manufacturer analysis
        st.subheader("🏭 Manufacturer Analysis")
        
        manufacturer_counts = {}
        for product in all_products:
            manufacturer_counts[product.manufacturer_name] = manufacturer_counts.get(product.manufacturer_name, 0) + 1
        
        manufacturer_df = pd.DataFrame(
            list(manufacturer_counts.items()), 
            columns=["Manufacturer", "Product Count"]
        ).sort_values("Product Count", ascending=False).head(10)
        
        st.bar_chart(manufacturer_df.set_index("Manufacturer"))
        
        # Category distribution
        st.subheader("📂 Category Distribution")
        
        category_stats = erp_manager.get_product_statistics()["by_category"]
        category_df = pd.DataFrame(
            [(k.replace('_', ' ').title(), v) for k, v in category_stats.items() if v > 0],
            columns=["Category", "Count"]
        )
        
        if not category_df.empty:
            st.bar_chart(category_df.set_index("Category"))
        else:
            st.info("No category data available.")
        
        # Status distribution
        st.subheader("📊 Product Status Overview")
        
        status_stats = erp_manager.get_product_statistics()["by_status"]
        status_df = pd.DataFrame(
            [(k.replace('_', ' ').title(), v) for k, v in status_stats.items() if v > 0],
            columns=["Status", "Count"]
        )
        
        if not status_df.empty:
            st.bar_chart(status_df.set_index("Status"))
        else:
            st.info("No status data available.")
        
        # Recent additions
        st.subheader("🕐 Recent Product Additions")
        
        recent_products = sorted(all_products, key=lambda x: x.created_date, reverse=True)[:5]
        
        for product in recent_products:
            with st.expander(f"{product.sku} - {product.product_name}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Manufacturer:** {product.manufacturer_name}")
                    st.markdown(f"**MRP:** ₹{product.mrp}")
                    st.markdown(f"**Category:** {product.category.value.replace('_', ' ').title()}")
                
                with col2:
                    st.markdown(f"**Status:** {product.status.value.replace('_', ' ').title()}")
                    st.markdown(f"**Created:** {product.created_date[:10]}")
                    st.markdown(f"**Created By:** {product.created_by}")
    
    else:
        st.info("No products found in the ERP system. Add some products to see analytics.")

# Log page access
log_user_action(
    current_user.username,
    "PAGE_ACCESS",
    "product_search",
    {"page": "Product Search & Verification"}
)
