"""
Enhanced Web Crawler Page with Automatic Compliance Checking
Automated crawling of product listings with Legal Metrology compliance validation
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.auth import require_auth, get_current_user
from core.audit_logger import log_user_action
from core.web_crawler import EcommerceCrawler, ProductData
import time
from typing import List, Dict, Any

st.set_page_config(page_title="Enhanced Web Crawler - Legal Metrology Checker", page_icon="🌐", layout="wide")

# Enhanced Custom CSS with Compliance Theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Enhanced Header with Compliance Theme */
    .crawler-header {
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
    
    .crawler-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="web" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="2" fill="white" opacity="0.1"/><line x1="10" y1="10" x2="30" y2="10" stroke="white" opacity="0.05"/><line x1="10" y1="10" x2="10" y2="30" stroke="white" opacity="0.05"/></pattern></defs><rect width="100" height="100" fill="url(%23web)"/></svg>');
        opacity: 0.1;
    }
    
    .crawler-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Compliance Status Cards */
    .compliance-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 5px solid;
        transition: transform 0.3s ease;
    }
    
    .compliance-card:hover {
        transform: translateY(-2px);
    }
    
    .compliance-compliant {
        border-left-color: #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.05) 0%, rgba(76, 175, 80, 0.02) 100%);
    }
    
    .compliance-partial {
        border-left-color: #FF9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.05) 0%, rgba(255, 152, 0, 0.02) 100%);
    }
    
    .compliance-non-compliant {
        border-left-color: #F44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.05) 0%, rgba(244, 67, 54, 0.02) 100%);
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-compliant { background: #4CAF50; }
    .status-partial { background: #FF9800; }
    .status-non-compliant { background: #F44336; }
    .status-error { background: #9E9E9E; }
    
    /* Issue Tags */
    .issue-tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        margin: 0.125rem;
        background: #f5f5f5;
        border: 1px solid #e0e0e0;
    }
    
    .issue-error {
        background: #ffebee;
        border-color: #f44336;
        color: #c62828;
    }
    
    .issue-warning {
        background: #fff3e0;
        border-color: #ff9800;
        color: #ef6c00;
    }
    
    .issue-info {
        background: #e3f2fd;
        border-color: #2196f3;
        color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

# Require authentication
require_auth()
current_user = get_current_user()

# Enhanced Header
st.markdown("""
<div class="crawler-header">
    <h1>🌐 Enhanced Web Crawler</h1>
    <p>Automated Product Crawling with Legal Metrology Compliance Checking</p>
</div>
""", unsafe_allow_html=True)

# Initialize crawler
@st.cache_resource
def get_crawler():
    return EcommerceCrawler()

crawler = get_crawler()

# Main interface tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Crawl & Check", 
    "📊 Compliance Dashboard", 
    "🔍 Product Analysis", 
    "📈 Platform Comparison", 
    "⚙️ Settings"
])

with tab1:
    st.markdown("### 🎯 Automated Product Crawling with Compliance Checking")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📱 Select Platforms")
        
        supported_platforms = crawler.get_supported_platforms()
        selected_platforms = []
        
        for platform_id, platform_name in supported_platforms.items():
            selected = st.checkbox(
                f"{platform_name}",
                key=f"platform_{platform_id}",
                help=f"Crawl products from {platform_name}"
            )
            if selected:
                selected_platforms.append(platform_id)
        
        if not selected_platforms:
            st.warning("Please select at least one platform to crawl.")
    
    with col2:
        st.subheader("🔍 Search Configuration")
        
        # Search queries focused on compliance testing
        st.markdown("**Search Queries** (focus on products requiring compliance)")
        query_text = st.text_area(
            "Enter product search terms:",
            value="organic food products\npackaged snacks\nbeauty products\nhousehold items\npharmaceuticals\ncosmetics",
            height=150,
            help="Enter search terms for products that need Legal Metrology compliance"
        )
        
        queries = [q.strip() for q in query_text.split('\n') if q.strip()]
        
        # Crawling parameters
        col2a, col2b = st.columns(2)
        
        with col2a:
            max_results = st.slider(
                "Max Results per Query",
                min_value=5,
                max_value=100,
                value=20,
                help="Maximum number of products to crawl per search query"
            )
        
        with col2b:
            delay_between = st.slider(
                "Delay Between Requests (seconds)",
                min_value=1.0,
                max_value=10.0,
                value=2.0,
                step=0.5,
                help="Delay between requests to respect rate limits"
            )
    
    # Compliance checking options
    with st.expander("⚖️ Compliance Checking Options"):
        col3a, col3b = st.columns(2)
        
        with col3a:
            enable_compliance = st.checkbox(
                "Enable Automatic Compliance Checking",
                value=True,
                help="Automatically check each product for Legal Metrology compliance"
            )
            
            show_detailed_issues = st.checkbox(
                "Show Detailed Compliance Issues",
                value=True,
                help="Display detailed compliance issues for each product"
            )
        
        with col3b:
            compliance_threshold = st.slider(
                "Compliance Score Threshold",
                min_value=0,
                max_value=100,
                value=80,
                help="Minimum compliance score to mark as compliant"
            )
            
            include_partial = st.checkbox(
                "Include Partial Compliance",
                value=True,
                help="Include products with partial compliance in results"
            )
    
    # Start crawling
    st.markdown("---")
    
    if st.button("🚀 Start Crawling with Compliance Check", type="primary", disabled=not selected_platforms or not queries):
        if selected_platforms and queries:
            # Show crawling progress
            progress_placeholder = st.empty()
            results_placeholder = st.empty()
            
            with progress_placeholder.container():
                st.info(f"🕷️ Starting crawl for {len(queries)} queries across {len(selected_platforms)} platforms...")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_operations = len(queries) * len(selected_platforms)
                current_operation = 0
                
                all_products = []
                
                # Create a container for real-time product display
                products_display = st.empty()
                
                for query in queries:
                    for platform in selected_platforms:
                        try:
                            current_operation += 1
                            progress = current_operation / total_operations
                            progress_bar.progress(progress)
                            status_text.text(f"Crawling '{query}' on {supported_platforms[platform]}...")
                            
                            # Perform crawling
                            products = crawler.search_products(query, platform, max_results)
                            all_products.extend(products)
                            
                            # Show real-time product results with images
                            with products_display.container():
                                st.markdown("### 📦 Products Found So Far:")
                                if all_products:
                                    # Show last 10 products found
                                    recent_products = all_products[-10:]
                                    
                                    # Display products in a grid layout
                                    cols = st.columns(2)  # 2 columns for better layout
                                    
                                    for i, product in enumerate(recent_products):
                                        col_idx = i % 2
                                        
                                        with cols[col_idx]:
                                            # Product card
                                            with st.container():
                                                # Status emoji and basic info
                                                status_emoji = {
                                                    'COMPLIANT': '✅',
                                                    'PARTIAL': '⚠️', 
                                                    'NON_COMPLIANT': '❌',
                                                    'ERROR': '🔧'
                                                }.get(product.compliance_status, '❓')
                                                
                                                score_display = f"{product.compliance_score:.1f}" if product.compliance_score else "N/A"
                                                
                                                # Product image
                                                if product.image_urls and len(product.image_urls) > 0:
                                                    try:
                                                        st.image(product.image_urls[0], width=150, caption=f"{product.platform.title()}")
                                                    except Exception as e:
                                                        st.write("🖼️ Image unavailable")
                                                else:
                                                    st.write("🖼️ No image available")
                                                
                                                # Product details
                                                st.write(f"{status_emoji} **{product.title[:50]}{'...' if len(product.title) > 50 else ''}**")
                                                st.write(f"**Platform:** {product.platform.title()}")
                                                st.write(f"**Price:** ₹{product.price}" if product.price else "**Price:** N/A")
                                                st.write(f"**Score:** {score_display}")
                                                
                                                st.markdown("---")
                                
                                st.write(f"**Total Products Crawled:** {len(all_products)}")
                            
                            # Log the action
                            log_user_action(
                                current_user.username,
                                "WEB_CRAWL_COMPLIANCE",
                                f"query:{query},platform:{platform}",
                                {"products_found": len(products), "max_results": max_results}
                            )
                            
                            # Respect rate limiting
                            time.sleep(delay_between)
                            
                        except Exception as e:
                            st.error(f"Error crawling {platform} for '{query}': {str(e)}")
                            continue
                
                # Complete progress
                progress_bar.progress(1.0)
                status_text.text("Crawling completed!")
            
            # Clear progress and show results
            progress_placeholder.empty()
            
            if all_products:
                # Save results
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                json_file = crawler.save_products(all_products, f"app/data/crawled/products_compliance_{timestamp}.json")
                csv_file = crawler.export_to_csv(all_products, f"app/data/crawled/products_compliance_{timestamp}.csv")
                
                # Generate compliance summary
                compliance_summary = crawler.get_compliance_summary(all_products)
                
                # Show compliance overview
                st.success(f"✅ Crawling completed! Found {len(all_products)} products.")
                
                # Compliance metrics
                col4a, col4b, col4c, col4d = st.columns(4)
                
                with col4a:
                    st.metric("Total Products", len(all_products))
                
                with col4b:
                    compliant_count = compliance_summary.get('compliant_products', 0)
                    st.metric("Compliant", compliant_count)
                
                with col4c:
                    compliance_rate = compliance_summary.get('compliance_rate', 0)
                    st.metric("Compliance Rate", f"{compliance_rate:.1f}%")
                
                with col4d:
                    avg_score = compliance_summary.get('average_score', 0)
                    st.metric("Avg Score", f"{avg_score:.1f}/100")
                
                # Show sample of crawled products with names
                st.markdown("### 📋 Sample of Crawled Products:")
                
                # Display first 10 products with full details and images
                sample_products = all_products[:10]
                for i, product in enumerate(sample_products, 1):
                    with st.expander(f"Product {i}: {product.title[:80]}{'...' if len(product.title) > 80 else ''}"):
                        col_product = st.columns([1, 2, 1])  # Image, Details, Compliance
                        
                        with col_product[0]:
                            # Product image
                            st.markdown("### 🖼️ Product Image")
                            if product.image_urls and len(product.image_urls) > 0:
                                try:
                                    st.image(product.image_urls[0], width=200, caption=f"{product.platform.title()}")
                                    
                                    # Show additional images if available
                                    if len(product.image_urls) > 1:
                                        st.markdown("**Additional Images:**")
                                        for j, img_url in enumerate(product.image_urls[1:4], 1):  # Show up to 3 additional images
                                            try:
                                                st.image(img_url, width=100, caption=f"Image {j+1}")
                                            except:
                                                pass
                                except Exception as e:
                                    st.write("🖼️ Image unavailable")
                                    st.write(f"*Error: {str(e)}*")
                            else:
                                st.write("🖼️ No image available")
                        
                        with col_product[1]:
                            # Product details
                            st.markdown("### 📋 Product Details")
                            st.write(f"**Full Title:** {product.title}")
                            st.write(f"**Platform:** {product.platform.title()}")
                            st.write(f"**Brand:** {product.brand or 'N/A'}")
                            st.write(f"**Price:** ₹{product.price}" if product.price else "**Price:** N/A")
                            st.write(f"**MRP:** ₹{product.mrp}" if product.mrp else "**MRP:** N/A")
                            st.write(f"**Rating:** {product.rating}/5" if product.rating else "**Rating:** N/A")
                            st.write(f"**Category:** {product.category or 'N/A'}")
                            st.write(f"**Extracted At:** {product.extracted_at}")
                            
                            # Product URL
                            if product.product_url:
                                st.write(f"**Product URL:** [View Product]({product.product_url})")
                        
                        with col_product[2]:
                            # Compliance status
                            status_emoji = {
                                'COMPLIANT': '✅',
                                'PARTIAL': '⚠️', 
                                'NON_COMPLIANT': '❌',
                                'ERROR': '🔧'
                            }.get(product.compliance_status, '❓')
                            
                            st.markdown(f"""
                            <div class="compliance-card compliance-{product.compliance_status.lower() if product.compliance_status else 'error'}">
                                <h4>{status_emoji} Compliance Status</h4>
                                <p><strong>Status:</strong> {product.compliance_status or 'UNKNOWN'}</p>
                                <p><strong>Score:</strong> {product.compliance_score:.1f}/100</p>
                                <p><strong>Issues:</strong> {len(product.issues_found) if product.issues_found else 0}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show compliance issues if any
                            if product.issues_found:
                                st.markdown("### ⚠️ Compliance Issues")
                                for issue in product.issues_found[:5]:  # Show first 5 issues
                                    st.write(f"• {issue}")
                                if len(product.issues_found) > 5:
                                    st.write(f"... and {len(product.issues_found) - 5} more issues")
                
                # Store in session state for other tabs
                st.session_state['last_crawl_results'] = all_products
                st.session_state['last_compliance_summary'] = compliance_summary
                st.session_state['last_crawl_timestamp'] = timestamp
                
            else:
                st.warning("⚠️ No products found. Try different search terms or platforms.")

with tab2:
    st.markdown("### 📊 Compliance Dashboard")
    
    if 'last_crawl_results' in st.session_state and 'last_compliance_summary' in st.session_state:
        products = st.session_state['last_crawl_results']
        summary = st.session_state['last_compliance_summary']
        
        # Compliance overview charts
        col5a, col5b = st.columns(2)
        
        with col5a:
            # Compliance status pie chart
            status_data = {
                'Compliant': summary.get('compliant_products', 0),
                'Partial': summary.get('partial_products', 0),
                'Non-Compliant': summary.get('non_compliant_products', 0)
            }
            
            fig_status = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title="Compliance Status Distribution",
                color_discrete_map={
                    'Compliant': '#4CAF50',
                    'Partial': '#FF9800',
                    'Non-Compliant': '#F44336'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col5b:
            # Platform compliance comparison
            platform_data = summary.get('platform_compliance', {})
            if platform_data:
                platforms = list(platform_data.keys())
                compliance_rates = []
                
                for platform in platforms:
                    total = platform_data[platform]['total']
                    compliant = platform_data[platform]['compliant']
                    rate = (compliant / total * 100) if total > 0 else 0
                    compliance_rates.append(rate)
                
                fig_platform = px.bar(
                    x=platforms,
                    y=compliance_rates,
                    title="Platform Compliance Rates",
                    labels={'x': 'Platform', 'y': 'Compliance Rate (%)'}
                )
                fig_platform.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_platform, use_container_width=True)
        
        # Issue analysis
        st.subheader("🔍 Compliance Issues Analysis")
        
        issue_counts = summary.get('issue_counts', {})
        if issue_counts:
            issues_df = pd.DataFrame([
                {'Issue Type': issue, 'Count': count}
                for issue, count in issue_counts.items()
            ]).sort_values('Count', ascending=False)
            
            fig_issues = px.bar(
                issues_df,
                x='Issue Type',
                y='Count',
                title="Most Common Compliance Issues"
            )
            st.plotly_chart(fig_issues, use_container_width=True)
        
        # Detailed compliance table
        st.subheader("📋 Detailed Compliance Results")
        
        # Filter options
        col6a, col6b, col6c = st.columns(3)
        
        with col6a:
            status_filter = st.selectbox(
                "Filter by Compliance Status:",
                options=['All', 'COMPLIANT', 'PARTIAL', 'NON_COMPLIANT'],
                key="status_filter"
            )
        
        with col6b:
            platform_filter = st.selectbox(
                "Filter by Platform:",
                options=['All'] + list(set(p.platform for p in products if p.platform)),
                key="platform_filter_compliance"
            )
        
        with col6c:
            score_threshold = st.slider(
                "Minimum Compliance Score:",
                min_value=0,
                max_value=100,
                value=0,
                key="score_threshold"
            )
        
        # Filter products
        filtered_products = products.copy()
        
        if status_filter != 'All':
            filtered_products = [p for p in filtered_products if p.compliance_status == status_filter]
        
        if platform_filter != 'All':
            filtered_products = [p for p in filtered_products if p.platform == platform_filter]
        
        filtered_products = [p for p in filtered_products if (p.compliance_score or 0) >= score_threshold]
        
        # Display filtered results with images
        if filtered_products:
            st.markdown("### 📊 Product Results with Images")
            
            # Display products in a grid with images
            products_per_row = 3
            for i in range(0, len(filtered_products), products_per_row):
                row_products = filtered_products[i:i+products_per_row]
                cols = st.columns(products_per_row)
                
                for j, product in enumerate(row_products):
                    with cols[j]:
                        # Product card with image
                        with st.container():
                            # Status emoji
                            status_emoji = {
                                'COMPLIANT': '✅',
                                'PARTIAL': '⚠️', 
                                'NON_COMPLIANT': '❌',
                                'ERROR': '🔧'
                            }.get(product.compliance_status, '❓')
                            
                            # Product image
                            if product.image_urls and len(product.image_urls) > 0:
                                try:
                                    st.image(product.image_urls[0], width=150, caption=f"{product.platform.title()}")
                                except Exception as e:
                                    st.write("🖼️ Image unavailable")
                            else:
                                st.write("🖼️ No image")
                            
                            # Product details
                            st.write(f"{status_emoji} **{product.title[:40]}{'...' if len(product.title) > 40 else ''}**")
                            st.write(f"**Platform:** {product.platform.title()}")
                            st.write(f"**Price:** ₹{product.price}" if product.price else "**Price:** N/A")
                            st.write(f"**Brand:** {product.brand or 'N/A'}")
                            st.write(f"**Status:** {product.compliance_status}")
                            st.write(f"**Score:** {product.compliance_score:.1f}" if product.compliance_score else "**Score:** N/A")
                            
                            # Show issues count
                            issues_count = len(product.issues_found) if product.issues_found else 0
                            if issues_count > 0:
                                st.write(f"**Issues:** {issues_count}")
                            
                            st.markdown("---")
            
            # Also show traditional table view
            st.markdown("### 📋 Traditional Table View")
            compliance_data = []
            for product in filtered_products:
                compliance_data.append({
                    'Title': product.title[:50] + '...' if len(product.title) > 50 else product.title,
                    'Platform': product.platform.title() if product.platform else 'Unknown',
                    'Price': f"₹{product.price}" if product.price else 'N/A',
                    'Compliance Status': product.compliance_status or 'UNKNOWN',
                    'Compliance Score': f"{product.compliance_score:.1f}" if product.compliance_score else 'N/A',
                    'Issues Count': len(product.issues_found) if product.issues_found else 0,
                    'Brand': product.brand or 'N/A'
                })
            
            compliance_df = pd.DataFrame(compliance_data)
            st.dataframe(compliance_df, use_container_width=True)
            
            # Download filtered results
            csv_data = compliance_df.to_csv(index=False)
            st.download_button(
                "📥 Download Compliance Results",
                data=csv_data,
                file_name=f"compliance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        else:
            st.info("No products match the current filters.")
    
    else:
        st.info("No compliance data available. Run a crawl operation first.")

with tab3:
    st.markdown("### 🔍 Individual Product Analysis")
    
    if 'last_crawl_results' in st.session_state:
        products = st.session_state['last_crawl_results']
        
        # Product selection
        product_options = {f"{p.title[:50]}... ({p.platform})": i for i, p in enumerate(products)}
        selected_product_key = st.selectbox(
            "Select a product for detailed analysis:",
            options=list(product_options.keys()),
            key="product_selector"
        )
        
        if selected_product_key:
            product_index = product_options[selected_product_key]
            product = products[product_index]
            
            # Product details with image
            col7a, col7b, col7c = st.columns([1, 2, 1])
            
            with col7a:
                # Product image
                st.markdown("### 🖼️ Product Image")
                if product.image_urls and len(product.image_urls) > 0:
                    try:
                        st.image(product.image_urls[0], width=250, caption=f"{product.platform.title()}")
                        
                        # Show additional images if available
                        if len(product.image_urls) > 1:
                            st.markdown("**Additional Images:**")
                            for j, img_url in enumerate(product.image_urls[1:6], 1):  # Show up to 5 additional images
                                try:
                                    st.image(img_url, width=120, caption=f"Image {j+1}")
                                except:
                                    pass
                    except Exception as e:
                        st.write("🖼️ Image unavailable")
                        st.write(f"*Error: {str(e)}*")
                else:
                    st.write("🖼️ No image available")
            
            with col7b:
                st.subheader(f"📦 {product.title}")
                
                # Basic product info
                product_info = {
                    'Platform': product.platform,
                    'Brand': product.brand,
                    'Price': f"₹{product.price}" if product.price else 'N/A',
                    'MRP': f"₹{product.mrp}" if product.mrp else 'N/A',
                    'Rating': f"{product.rating}/5" if product.rating else 'N/A',
                    'Category': product.category or 'N/A',
                    'Extracted At': product.extracted_at
                }
                
                for key, value in product_info.items():
                    st.write(f"**{key}:** {value}")
                
                # Product URL
                if product.product_url:
                    st.write(f"**Product URL:** [View Product]({product.product_url})")
            
            with col7c:
                # Compliance status card
                status_class = f"compliance-{product.compliance_status.lower()}" if product.compliance_status else "compliance-error"
                status_color = {
                    'COMPLIANT': '#4CAF50',
                    'PARTIAL': '#FF9800',
                    'NON_COMPLIANT': '#F44336',
                    'ERROR': '#9E9E9E'
                }.get(product.compliance_status, '#9E9E9E')
                
                st.markdown(f"""
                <div class="compliance-card {status_class}">
                    <h4>⚖️ Compliance Status</h4>
                    <p><span class="status-indicator status-{product.compliance_status.lower() if product.compliance_status else 'error'}"></span>
                    <strong>{product.compliance_status or 'UNKNOWN'}</strong></p>
                    <p><strong>Score:</strong> {product.compliance_score:.1f}/100</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Compliance details
            if product.compliance_details:
                st.subheader("🔍 Compliance Analysis Details")
                
                extracted_fields = product.compliance_details.get('extracted_fields', {})
                validation_issues = product.compliance_details.get('validation_issues', [])
                
                col8a, col8b = st.columns(2)
                
                with col8a:
                    st.markdown("**📋 Extracted Fields:**")
                    for field, value in extracted_fields.items():
                        if value:
                            st.write(f"• **{field.replace('_', ' ').title()}:** {value}")
                
                with col8b:
                    st.markdown("**⚠️ Validation Issues:**")
                    if validation_issues:
                        for issue in validation_issues:
                            level_class = f"issue-{issue['level'].lower()}"
                            st.markdown(f"""
                            <div class="issue-tag {level_class}">
                                <strong>{issue['level']}</strong>: {issue['message']}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("✅ No compliance issues found!")
            
            # Raw compliance data
            with st.expander("🔧 Raw Compliance Data"):
                st.json(product.compliance_details)
    
    else:
        st.info("No products available for analysis. Run a crawl operation first.")

with tab4:
    st.markdown("### 📈 Platform Comparison")
    
    if 'last_crawl_results' in st.session_state:
        products = st.session_state['last_crawl_results']
        
        # Platform statistics
        platform_stats = {}
        for product in products:
            platform = product.platform or 'unknown'
            if platform not in platform_stats:
                platform_stats[platform] = {
                    'total': 0,
                    'compliant': 0,
                    'partial': 0,
                    'non_compliant': 0,
                    'scores': [],
                    'issues': []
                }
            
            platform_stats[platform]['total'] += 1
            
            if product.compliance_status == 'COMPLIANT':
                platform_stats[platform]['compliant'] += 1
            elif product.compliance_status == 'PARTIAL':
                platform_stats[platform]['partial'] += 1
            elif product.compliance_status == 'NON_COMPLIANT':
                platform_stats[platform]['non_compliant'] += 1
            
            if product.compliance_score:
                platform_stats[platform]['scores'].append(product.compliance_score)
            
            if product.issues_found:
                platform_stats[platform]['issues'].extend(product.issues_found)
        
        # Platform comparison metrics
        comparison_data = []
        for platform, stats in platform_stats.items():
            avg_score = sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0
            compliance_rate = (stats['compliant'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            comparison_data.append({
                'Platform': platform.title(),
                'Total Products': stats['total'],
                'Compliant': stats['compliant'],
                'Partial': stats['partial'],
                'Non-Compliant': stats['non_compliant'],
                'Compliance Rate (%)': compliance_rate,
                'Avg Score': avg_score,
                'Total Issues': len(stats['issues'])
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Display comparison table
        st.dataframe(comparison_df, use_container_width=True)
        
        # Platform comparison charts
        col9a, col9b = st.columns(2)
        
        with col9a:
            # Compliance rates comparison
            fig_comparison = px.bar(
                comparison_df,
                x='Platform',
                y='Compliance Rate (%)',
                title="Platform Compliance Rates Comparison"
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        with col9b:
            # Average scores comparison
            fig_scores = px.bar(
                comparison_df,
                x='Platform',
                y='Avg Score',
                title="Platform Average Compliance Scores"
            )
            st.plotly_chart(fig_scores, use_container_width=True)
        
        # Issue distribution by platform
        st.subheader("📊 Issue Distribution by Platform")
        
        issue_data = []
        for platform, stats in platform_stats.items():
            issue_counts = {}
            for issue in stats['issues']:
                issue_type = issue.split(':')[0] if ':' in issue else issue
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
            
            for issue_type, count in issue_counts.items():
                issue_data.append({
                    'Platform': platform.title(),
                    'Issue Type': issue_type,
                    'Count': count
                })
        
        if issue_data:
            issue_df = pd.DataFrame(issue_data)
            fig_issues = px.bar(
                issue_df,
                x='Platform',
                y='Count',
                color='Issue Type',
                title="Compliance Issues by Platform"
            )
            st.plotly_chart(fig_issues, use_container_width=True)
    
    else:
        st.info("No data available for platform comparison. Run a crawl operation first.")

with tab5:
    st.markdown("### ⚙️ Crawler Settings")
    
    # Compliance settings
    st.subheader("⚖️ Compliance Settings")
    
    col10a, col10b = st.columns(2)
    
    with col10a:
        st.checkbox(
            "Enable Compliance Checking",
            value=True,
            key="enable_compliance_setting",
            help="Automatically check products for Legal Metrology compliance"
        )
        
        st.checkbox(
            "Include Partial Compliance",
            value=True,
            key="include_partial_setting",
            help="Include products with partial compliance in results"
        )
    
    with col10b:
        st.number_input(
            "Compliance Score Threshold",
            min_value=0,
            max_value=100,
            value=80,
            key="compliance_threshold_setting",
            help="Minimum score to consider as compliant"
        )
        
        st.selectbox(
            "Compliance Report Format",
            options=["Detailed", "Summary", "Issues Only"],
            index=0,
            key="report_format_setting"
        )
    
    # Platform settings
    st.subheader("🏪 Platform Settings")
    
    for platform_id, platform_name in crawler.get_supported_platforms().items():
        with st.expander(f"📱 {platform_name} Settings"):
            col11a, col11b = st.columns(2)
            
            with col11a:
                st.number_input(
                    "Rate Limit (seconds):",
                    min_value=0.5,
                    max_value=10.0,
                    value=2.0,
                    step=0.5,
                    key=f"rate_limit_{platform_id}_setting",
                    help="Delay between requests to this platform"
                )
            
            with col11b:
                st.number_input(
                    "Request Timeout (seconds):",
                    min_value=5,
                    max_value=60,
                    value=30,
                    key=f"timeout_{platform_id}_setting",
                    help="Timeout for individual requests"
                )
    
    # Data export settings
    st.subheader("💾 Data Export Settings")
    
    export_format = st.selectbox(
        "Default Export Format:",
        options=["JSON + CSV", "JSON Only", "CSV Only"],
        index=0,
        help="Default format for saving crawled data"
    )
    
    include_compliance_details = st.checkbox(
        "Include Detailed Compliance Data",
        value=True,
        help="Include full compliance analysis in export"
    )
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")
        
        # Log settings change
        log_user_action(
            current_user.username,
            "SETTINGS_UPDATE",
            "enhanced_crawler_settings",
            {"export_format": export_format, "include_compliance": include_compliance_details}
        )

# Footer
st.markdown("---")
st.markdown("""
<div class="compliance-card">
    <h4>🤝 Enhanced Web Crawler Features</h4>
    <ul>
        <li><strong>Automatic Compliance Checking</strong> - Every crawled product is automatically validated against Legal Metrology Rules 2011</li>
        <li><strong>Multi-Platform Support</strong> - Amazon India, Flipkart, Myntra, and Nykaa</li>
        <li><strong>Real-time Compliance Scoring</strong> - Instant compliance scores and detailed issue analysis</li>
        <li><strong>Comprehensive Reporting</strong> - Platform-wise compliance comparisons and trend analysis</li>
        <li><strong>Issue Tracking</strong> - Detailed tracking of compliance violations and recommendations</li>
    </ul>
    <p><em>Note: All crawling is performed responsibly with rate limiting and compliance with platform terms of service.</em></p>
</div>
""", unsafe_allow_html=True)
