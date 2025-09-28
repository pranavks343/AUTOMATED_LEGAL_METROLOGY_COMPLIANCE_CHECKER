import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from core.auth import require_admin, get_current_user
from core.erp_manager import (
    erp_manager, ProductStatus, ProductCategory, ProductData
)
from core.workflow_manager import workflow_manager, WorkflowType
from core.label_generator import label_generator, LabelFormat
from core.audit_logger import log_user_action
from core.json_utils import safe_json_dumps

st.set_page_config(page_title="ERP Product Management - Legal Metrology Checker", page_icon="📦", layout="wide")

# Enhanced Custom CSS for ERP Management
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* ERP Header */
    .erp-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .erp-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="boxes" width="20" height="20" patternUnits="userSpaceOnUse"><rect width="18" height="18" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23boxes)"/></svg>');
        opacity: 0.1;
    }
    
    .erp-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* ERP Form Cards */
    .erp-form-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .erp-form-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .erp-form-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Product Status Cards */
    .product-status-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
    }
    
    .product-status-card.draft {
        border-left: 4px solid #ff9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
    }
    
    .product-status-card.compliant {
        border-left: 4px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    .product-status-card.non-compliant {
        border-left: 4px solid #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
    }
    
    .product-status-card.pending {
        border-left: 4px solid #2196F3;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%);
    }
    
    /* ERP Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        border: 1px solid #e0e0e0;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Enhanced Input Styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Product Grid */
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 1rem 0;
    }
    
    .product-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .product-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .product-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metrics Cards */
    .erp-metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    
    .erp-metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .erp-metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Alert Enhancements */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Require admin access
require_admin()
current_user = get_current_user()

# Enhanced ERP Header
st.markdown(f"""
<div class="erp-header">
    <h1>📦 ERP Product Management</h1>
    <p>Welcome, <strong>{current_user.username}</strong>! Manage product data entry and Legal Metrology compliance workflow.</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for different ERP functions
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Product Data Entry", 
    "📊 Product Dashboard", 
    "🔄 Workflow Management", 
    "🏷️ Label Generation",
    "📈 Analytics & Reports"
])

with tab1:
    st.markdown("### 📝 ERP Product Data Entry")
    st.markdown("Enter new product data for Legal Metrology compliance processing.")
    
    st.markdown("""
    <div class="erp-form-card">
    """, unsafe_allow_html=True)
    
    with st.form("product_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input(
                "Product Name *",
                placeholder="Enter product name",
                help="Full product name as it appears on packaging"
            )
            
            mrp = st.number_input(
                "MRP (Maximum Retail Price) *",
                min_value=0.01,
                step=0.01,
                format="%.2f",
                help="Maximum retail price in INR"
            )
            
            net_quantity = st.number_input(
                "Net Quantity *",
                min_value=0.01,
                step=0.01,
                format="%.2f",
                help="Net quantity of the product"
            )
            
            unit = st.selectbox(
                "Unit *",
                options=["g", "kg", "ml", "l", "L", "pcs", "piece", "pack", "gm", "mg"],
                help="Unit of measurement"
            )
            
            manufacturer_name = st.text_input(
                "Manufacturer Name *",
                placeholder="Enter manufacturer name",
                help="Name of the manufacturing company"
            )
        
        with col2:
            category = st.selectbox(
                "Product Category *",
                options=[cat.value for cat in ProductCategory],
                format_func=lambda x: x.replace("_", " ").title(),
                help="Select the product category"
            )
            
            manufacturer_address = st.text_area(
                "Manufacturer Address",
                placeholder="Enter manufacturer address (optional)",
                help="Complete manufacturer address"
            )
            
            mfg_date = st.text_input(
                "Manufacturing Date",
                placeholder="DD/MM/YYYY",
                help="Manufacturing date (optional)"
            )
            
            expiry_date = st.text_input(
                "Expiry Date",
                placeholder="DD/MM/YYYY",
                help="Expiry date (optional)"
            )
            
            batch_number = st.text_input(
                "Batch Number",
                placeholder="Enter batch number (optional)",
                help="Product batch number"
            )
            
            fssai_number = st.text_input(
                "FSSAI Number",
                placeholder="Enter FSSAI number (optional)",
                help="FSSAI license number for food products"
            )
            
            country_of_origin = st.text_input(
                "Country of Origin",
                placeholder="Enter country (optional)",
                help="Country where the product was manufactured"
            )
        
        tags = st.text_input(
            "Tags (Optional)",
            placeholder="Enter tags separated by commas",
            help="Add relevant tags for categorization"
        )
        
        submitted = st.form_submit_button("📝 Add Product to ERP", type="primary")
        
        if submitted:
            if not all([product_name, mrp, net_quantity, unit, manufacturer_name]):
                st.error("Please fill in all required fields (marked with *).")
            else:
                # Check for existing products before adding
                search_product = {
                    'product_name': product_name,
                    'manufacturer_name': manufacturer_name,
                    'mrp': mrp,
                    'net_quantity': net_quantity,
                    'unit': unit,
                    'category': category
                }
                
                # Check for exact match
                exact_match = None
                for existing_product in erp_manager.get_all_products():
                    if (product_name.lower() == existing_product.product_name.lower() and
                        manufacturer_name.lower() == existing_product.manufacturer_name.lower() and
                        abs(float(mrp) - float(existing_product.mrp)) < 0.01 and
                        abs(float(net_quantity) - float(existing_product.net_quantity)) < 0.01 and
                        unit.lower() == existing_product.unit.lower()):
                        exact_match = existing_product
                        break
                
                if exact_match:
                    st.error(f"⚠️ **Duplicate Product Detected!**")
                    st.warning(f"A product with identical details already exists:")
                    st.info(f"**Existing Product:**")
                    st.info(f"• **SKU:** {exact_match.sku}")
                    st.info(f"• **Status:** {exact_match.status.value}")
                    st.info(f"• **Created:** {exact_match.created_date[:10]} by {exact_match.created_by}")
                    st.info(f"Please use the 🔍 **Search Products** page to verify before adding new products.")
                else:
                    # Check for similar products
                    similar_products = []
                    for existing_product in erp_manager.get_all_products():
                        # Calculate similarity based on name and manufacturer
                        import difflib
                        name_similarity = difflib.SequenceMatcher(
                            None, product_name.lower(), existing_product.product_name.lower()
                        ).ratio()
                        manufacturer_similarity = difflib.SequenceMatcher(
                            None, manufacturer_name.lower(), existing_product.manufacturer_name.lower()
                        ).ratio()
                        
                        # Consider it similar if name similarity > 80% and manufacturer similarity > 70%
                        if name_similarity > 0.8 and manufacturer_similarity > 0.7:
                            similarity_score = (name_similarity * 0.6 + manufacturer_similarity * 0.4) * 100
                            similar_products.append((existing_product, similarity_score))
                    
                    if similar_products:
                        st.warning(f"⚠️ **Similar Products Found!**")
                        st.warning(f"Found {len(similar_products)} similar product(s). Please review before proceeding:")
                        
                        for similar_product, score in similar_products[:3]:  # Show top 3 similar products
                            st.info(f"**Similar Product (Similarity: {score:.1f}%):**")
                            st.info(f"• **SKU:** {similar_product.sku} - {similar_product.product_name}")
                            st.info(f"• **Manufacturer:** {similar_product.manufacturer_name}")
                            st.info(f"• **MRP:** ₹{similar_product.mrp} | **Quantity:** {similar_product.net_quantity} {similar_product.unit}")
                        
                        # Ask for confirmation
                        if st.button("⚠️ Add Anyway (I've verified this is a different product)", type="secondary"):
                            st.session_state.confirmed_add = True
                        
                        if not st.session_state.get('confirmed_add', False):
                            st.info("💡 **Recommendation:** Use the 🔍 **Search Products** page to thoroughly check for duplicates before adding.")
                        else:
                            # Proceed with adding the product
                            st.session_state.confirmed_add = False  # Reset confirmation
                    
                    # Add the product if no exact match and either no similar products or confirmed
                    if not similar_products or st.session_state.get('confirmed_add', False):
                        try:
                            # Process tags
                            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
                            
                            # Add product to ERP
                            product = erp_manager.add_product(
                                product_name=product_name,
                                mrp=mrp,
                                net_quantity=net_quantity,
                                unit=unit,
                                manufacturer_name=manufacturer_name,
                                category=ProductCategory(category),
                                created_by=current_user.username,
                                manufacturer_address=manufacturer_address if manufacturer_address else None,
                                mfg_date=mfg_date if mfg_date else None,
                                expiry_date=expiry_date if expiry_date else None,
                                batch_number=batch_number if batch_number else None,
                                fssai_number=fssai_number if fssai_number else None,
                                country_of_origin=country_of_origin if country_of_origin else None,
                                tags=tag_list
                            )
                            
                            st.success(f"✅ Product added successfully!")
                            st.info(f"**SKU:** {product.sku}")
                            st.info(f"**Status:** {product.status.value}")
                            st.info(f"**Category:** {product.category.value.replace('_', ' ').title()}")
                            
                            # Log the action
                            log_user_action(
                                current_user.username,
                                "PRODUCT_ADDED",
                                f"product:{product.sku}",
                                {
                                    "product_name": product_name,
                                    "category": category,
                                    "mrp": mrp
                                }
                            )
                            
                            # Reset confirmation state after successful add
                            if 'confirmed_add' in st.session_state:
                                del st.session_state.confirmed_add
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error adding product: {str(e)}")
    
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📊 Product Dashboard")
    
    # Get product statistics
    stats = erp_manager.get_product_statistics()
    
    # Enhanced Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="erp-metric-card">
            <h3>📦 {stats["total_products"]}</h3>
            <p>Total Products</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="erp-metric-card">
            <h3>📝 {stats["draft_products"]}</h3>
            <p>Draft Products</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="erp-metric-card">
            <h3>✅ {stats["approved_products"]}</h3>
            <p>Approved Products</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="erp-metric-card">
            <h3>🚚 {stats["dispatched_products"]}</h3>
            <p>Dispatched Products</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Status and category distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Status Distribution")
        if stats["by_status"]:
            status_df = pd.DataFrame(list(stats["by_status"].items()), columns=["Status", "Count"])
            st.bar_chart(status_df.set_index("Status"))
        else:
            st.info("No products found.")
    
    with col2:
        st.subheader("📂 Category Distribution")
        if stats["by_category"]:
            category_df = pd.DataFrame(list(stats["by_category"].items()), columns=["Category", "Count"])
            st.bar_chart(category_df.set_index("Category"))
        else:
            st.info("No products found.")
    
    # Product search and management
    st.subheader("🔍 Product Management")
    
    # Search and filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("🔍 Search Products", placeholder="Search by name, SKU, or manufacturer")
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All"] + [status.value for status in ProductStatus],
            format_func=lambda x: x.replace("_", " ").title()
        )
    
    with col3:
        category_filter = st.selectbox(
            "Filter by Category",
            options=["All"] + [category.value for category in ProductCategory],
            format_func=lambda x: x.replace("_", " ").title()
        )
    
    # Get filtered products
    all_products = erp_manager.get_all_products()
    
    if search_query:
        all_products = erp_manager.search_products(search_query)
    
    if status_filter != "All":
        all_products = [p for p in all_products if p.status.value == status_filter]
    
    if category_filter != "All":
        all_products = [p for p in all_products if p.category.value == category_filter]
    
    # Display products
    if all_products:
        st.markdown(f"**Found {len(all_products)} product(s)**")
        
        for product in all_products:
            with st.expander(f"{product.sku} - {product.product_name}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Product Name:** {product.product_name}")
                    st.markdown(f"**Manufacturer:** {product.manufacturer_name}")
                    st.markdown(f"**MRP:** ₹{product.mrp}")
                    st.markdown(f"**Net Quantity:** {product.net_quantity} {product.unit}")
                    st.markdown(f"**Category:** {product.category.value.replace('_', ' ').title()}")
                    st.markdown(f"**Status:** {product.status.value.replace('_', ' ').title()}")
                    st.markdown(f"**Created:** {product.created_date[:10]}")
                    
                    if product.compliance_status:
                        st.markdown(f"**Compliance Status:** {product.compliance_status}")
                    
                    if product.compliance_issues:
                        st.markdown(f"**Compliance Issues:** {', '.join(product.compliance_issues)}")
                
                with col2:
                    # Status update
                    st.markdown("**Update Status:**")
                    new_status = st.selectbox(
                        "Status",
                        options=[status.value for status in ProductStatus],
                        index=list(ProductStatus).index(product.status),
                        key=f"status_{product.sku}"
                    )
                    
                    if st.button("Update Status", key=f"update_status_{product.sku}"):
                        if erp_manager.update_product_status(
                            product.sku, 
                            ProductStatus(new_status), 
                            current_user.username
                        ):
                            st.success("Status updated successfully!")
                            st.rerun()
                    
                    # Workflow actions
                    if product.status == ProductStatus.DRAFT:
                        if st.button("Start Approval Workflow", key=f"workflow_{product.sku}"):
                            try:
                                workflow = workflow_manager.initiate_workflow(
                                    WorkflowType.PRODUCT_APPROVAL,
                                    product.sku,
                                    "PRODUCT",
                                    current_user.username,
                                    {"product_name": product.product_name}
                                )
                                st.success(f"Workflow initiated: {workflow.workflow_id}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error starting workflow: {str(e)}")
                    
                    # Label generation
                    if product.status == ProductStatus.APPROVED:
                        if st.button("Generate Label", key=f"label_{product.sku}"):
                            try:
                                product_data = {
                                    "sku": product.sku,
                                    "product_name": product.product_name,
                                    "mrp": product.mrp,
                                    "net_quantity": product.net_quantity,
                                    "unit": product.unit,
                                    "manufacturer_name": product.manufacturer_name,
                                    "mfg_date": product.mfg_date,
                                    "expiry_date": product.expiry_date,
                                    "batch_number": product.batch_number,
                                    "fssai_number": product.fssai_number,
                                    "country_of_origin": product.country_of_origin
                                }
                                
                                label = label_generator.create_label_from_product(
                                    product_data,
                                    LabelFormat.STANDARD,
                                    current_user.username
                                )
                                st.success(f"Label generated: {label.label_id}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error generating label: {str(e)}")
    else:
        st.info("No products found matching the criteria.")

with tab3:
    st.subheader("🔄 Workflow Management")
    
    # Get workflow statistics
    workflow_stats = workflow_manager.get_workflow_statistics()
    
    # Workflow overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Workflows", workflow_stats["total_workflows"])
    
    with col2:
        st.metric("Pending Workflows", workflow_stats["pending_workflows"])
    
    with col3:
        st.metric("Completed Workflows", workflow_stats["completed_workflows"])
    
    # Pending workflows
    st.subheader("⏳ Pending Workflows")
    
    # Get pending workflows for current user role (simplified as ADMIN for demo)
    pending_workflows = workflow_manager.get_pending_workflows("ADMIN")
    
    if pending_workflows:
        for workflow in pending_workflows:
            with st.expander(f"{workflow.workflow_id} - {workflow.workflow_type.value}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Entity:** {workflow.entity_id}")
                    st.markdown(f"**Type:** {workflow.workflow_type.value}")
                    st.markdown(f"**Status:** {workflow.status.value}")
                    st.markdown(f"**Initiated By:** {workflow.initiated_by}")
                    st.markdown(f"**Initiated Date:** {workflow.initiated_date[:10]}")
                    
                    if workflow.current_step:
                        current_step = next((s for s in workflow.steps if s.step_id == workflow.current_step), None)
                        if current_step:
                            st.markdown(f"**Current Step:** {current_step.step_name}")
                            st.markdown(f"**Required Role:** {current_step.required_role}")
                
                with col2:
                    if workflow.current_step:
                        current_step = next((s for s in workflow.steps if s.step_id == workflow.current_step), None)
                        if current_step:
                            comments = st.text_area(
                                "Comments",
                                placeholder="Add approval comments...",
                                key=f"comments_{workflow.workflow_id}",
                                height=100
                            )
                            
                            col_approve, col_reject = st.columns(2)
                            
                            with col_approve:
                                if st.button("Approve", key=f"approve_{workflow.workflow_id}"):
                                    if workflow_manager.approve_step(
                                        workflow.workflow_id,
                                        workflow.current_step,
                                        current_user.username,
                                        comments
                                    ):
                                        st.success("Step approved!")
                                        st.rerun()
                            
                            with col_reject:
                                if st.button("Reject", key=f"reject_{workflow.workflow_id}"):
                                    reason = st.text_input(
                                        "Rejection Reason",
                                        key=f"reason_{workflow.workflow_id}"
                                    )
                                    if reason:
                                        if workflow_manager.reject_step(
                                            workflow.workflow_id,
                                            workflow.current_step,
                                            current_user.username,
                                            reason
                                        ):
                                            st.success("Step rejected!")
                                            st.rerun()
    else:
        st.info("No pending workflows found.")

with tab4:
    st.subheader("🏷️ Label Generation & Management")
    
    # Get label statistics
    label_stats = label_generator.get_label_statistics()
    
    # Label overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Labels", label_stats["total_labels"])
    
    with col2:
        st.metric("Approved Labels", label_stats["approved_labels"])
    
    with col3:
        st.metric("Compliance Pass Rate", f"{label_stats['compliance_pass_rate']}%")
    
    # Label management
    st.subheader("📋 Label Management")
    
    # Get all labels
    all_labels = label_generator.labels
    
    if all_labels:
        for label in all_labels:
            with st.expander(f"{label.label_id} - {label.product_sku}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Product SKU:** {label.product_sku}")
                    st.markdown(f"**Format:** {label.label_format.value}")
                    st.markdown(f"**Status:** {label.status.value}")
                    st.markdown(f"**Created By:** {label.created_by}")
                    st.markdown(f"**Created Date:** {label.created_date[:10]}")
                    st.markdown(f"**Compliance Gate:** {label.compliance_gate_status.value}")
                    
                    if label.compliance_issues:
                        st.warning(f"**Compliance Issues:** {', '.join(label.compliance_issues)}")
                    
                    # Display label elements
                    st.markdown("**Label Elements:**")
                    for element in label.elements:
                        status_icon = "✅" if element.compliance_checked else "❌"
                        st.write(f"{status_icon} {element.element_id}: {element.content}")
                
                with col2:
                    # Generate label image
                    if st.button("Generate Preview", key=f"preview_{label.label_id}"):
                        image_data = label_generator.generate_label_image(label.label_id)
                        if image_data:
                            st.image(image_data, caption=f"Label Preview - {label.label_id}")
                        else:
                            st.error("Failed to generate label preview")
                    
                    # Label actions
                    if label.compliance_gate_status.value == "PASSED" and label.status.value == "DRAFT":
                        if st.button("Approve Label", key=f"approve_label_{label.label_id}"):
                            if label_generator.approve_label(
                                label.label_id,
                                current_user.username,
                                "Approved for printing"
                            ):
                                st.success("Label approved!")
                                st.rerun()
                    
                    if label.compliance_gate_status.value == "FAILED":
                        if st.button("Reject Label", key=f"reject_label_{label.label_id}"):
                            reason = st.text_input(
                                "Rejection Reason",
                                key=f"reject_reason_{label.label_id}",
                                placeholder="Enter rejection reason..."
                            )
                            if reason:
                                if label_generator.reject_label(
                                    label.label_id,
                                    current_user.username,
                                    reason
                                ):
                                    st.success("Label rejected!")
                                    st.rerun()
    else:
        st.info("No labels generated yet.")

with tab5:
    st.subheader("📈 Analytics & Reports")
    
    # Export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Product Summary"):
            summary_data = {
                "export_timestamp": datetime.now().isoformat(),
                "exported_by": current_user.username,
                "product_statistics": stats,
                "workflow_statistics": workflow_stats,
                "label_statistics": label_stats
            }
            
            st.download_button(
                label="Download Summary Report",
                data=safe_json_dumps(summary_data, indent=2),
                file_name=f"erp_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📋 Export All Products"):
            products_data = []
            for product in erp_manager.get_all_products():
                product_dict = {
                    "sku": product.sku,
                    "product_name": product.product_name,
                    "mrp": product.mrp,
                    "net_quantity": product.net_quantity,
                    "unit": product.unit,
                    "manufacturer_name": product.manufacturer_name,
                    "category": product.category.value,
                    "status": product.status.value,
                    "compliance_status": product.compliance_status,
                    "created_date": product.created_date,
                    "tags": product.tags
                }
                products_data.append(product_dict)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "exported_by": current_user.username,
                "products": products_data
            }
            
            st.download_button(
                label="Download Products Data",
                data=safe_json_dumps(export_data, indent=2),
                file_name=f"erp_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("🔄 Export Workflows"):
            workflows_data = []
            for workflow in workflow_manager.workflows:
                workflow_dict = {
                    "workflow_id": workflow.workflow_id,
                    "workflow_type": workflow.workflow_type.value,
                    "entity_id": workflow.entity_id,
                    "status": workflow.status.value,
                    "initiated_by": workflow.initiated_by,
                    "initiated_date": workflow.initiated_date,
                    "completed_date": workflow.completed_date,
                    "steps": [
                        {
                            "step_name": step.step_name,
                            "required_role": step.required_role,
                            "status": step.status.value,
                            "completed_date": step.completed_date
                        } for step in workflow.steps
                    ]
                }
                workflows_data.append(workflow_dict)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "exported_by": current_user.username,
                "workflows": workflows_data
            }
            
            st.download_button(
                label="Download Workflows Data",
                data=safe_json_dumps(export_data, indent=2),
                file_name=f"workflows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Analytics charts
    st.subheader("📊 System Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Product Status Distribution**")
        if stats["by_status"]:
            status_df = pd.DataFrame(list(stats["by_status"].items()), columns=["Status", "Count"])
            st.bar_chart(status_df.set_index("Status"))
        else:
            st.info("No product data available.")
    
    with col2:
        st.markdown("**Workflow Status Distribution**")
        if workflow_stats["by_status"]:
            workflow_status_df = pd.DataFrame(list(workflow_stats["by_status"].items()), columns=["Status", "Count"])
            st.bar_chart(workflow_status_df.set_index("Status"))
        else:
            st.info("No workflow data available.")

# Log page access
log_user_action(
    current_user.username,
    "PAGE_ACCESS",
    "erp_product_management",
    {"page": "ERP Product Management"}
)
