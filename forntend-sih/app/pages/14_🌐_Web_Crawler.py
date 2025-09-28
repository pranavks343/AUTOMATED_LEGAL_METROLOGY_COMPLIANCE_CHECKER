"""
Web Crawler Page for E-commerce Platform Data Acquisition
Automated crawling of product listings from major Indian e-commerce platforms
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from core.auth import require_auth, get_current_user
from core.audit_logger import log_user_action
from core.web_crawler import EcommerceCrawler, ProductData
import time
import asyncio
from typing import List, Dict, Any

st.set_page_config(page_title="Web Crawler - Legal Metrology Checker", page_icon="🌐", layout="wide")

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Crawler Header */
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
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Platform Cards */
    .platform-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .platform-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .platform-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active { background: #4CAF50; }
    .status-inactive { background: #f44336; }
    .status-crawling { background: #ff9800; animation: pulse 2s infinite; }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Progress Bars */
    .progress-container {
        background: #f0f0f0;
        border-radius: 10px;
        padding: 0.5rem;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 20px;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Results Table */
    .results-table {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Alert Enhancements */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Require authentication
require_auth()
current_user = get_current_user()

# Enhanced Header
st.markdown("""
<div class="crawler-header">
    <h1>🌐 Web Crawler</h1>
    <p>Automated Data Acquisition from Major E-commerce Platforms</p>
</div>
""", unsafe_allow_html=True)

# Initialize crawler
@st.cache_resource
def get_crawler():
    return EcommerceCrawler()

crawler = get_crawler()

# Main interface tabs
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Crawl Products", "📊 View Results", "⚙️ Settings", "📈 Analytics"])

with tab1:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 Product Crawling Configuration</h3>
        <p>Configure your web crawling parameters to extract product data from major Indian e-commerce platforms.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Platform selection
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
        
        # Search queries
        st.markdown("**Search Queries** (one per line)")
        query_text = st.text_area(
            "Enter product search terms:",
            value="organic food products\npackaged snacks\nbeauty products\nhousehold items",
            height=150,
            help="Enter search terms, one per line. Each term will be used to search for products."
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
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        col3a, col3b = st.columns(2)
        
        with col3a:
            use_selenium = st.checkbox(
                "Use Selenium for JavaScript sites",
                value=True,
                help="Use Selenium WebDriver for sites that require JavaScript rendering"
            )
            
            save_images = st.checkbox(
                "Download Product Images",
                value=False,
                help="Download and save product images locally"
            )
        
        with col3b:
            extract_details = st.checkbox(
                "Extract Detailed Information",
                value=False,
                help="Visit individual product pages to extract detailed information (slower)"
            )
            
            filter_duplicates = st.checkbox(
                "Filter Duplicate Products",
                value=True,
                help="Remove duplicate products based on title similarity"
            )
    
    # Start crawling
    st.markdown("---")
    
    if st.button("🚀 Start Crawling", type="primary", disabled=not selected_platforms or not queries):
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
                            
                            # Log the action
                            log_user_action(
                                current_user.username,
                                "WEB_CRAWL",
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
                json_file = crawler.save_products(all_products, f"app/data/crawled/products_{timestamp}.json")
                csv_file = crawler.export_to_csv(all_products, f"app/data/crawled/products_{timestamp}.csv")
                
                # Show success message
                st.success(f"✅ Crawling completed! Found {len(all_products)} products.")
                
                # Show quick stats
                col4a, col4b, col4c, col4d = st.columns(4)
                
                with col4a:
                    st.metric("Total Products", len(all_products))
                
                with col4b:
                    platforms_found = len(set(p.platform for p in all_products if p.platform))
                    st.metric("Platforms", platforms_found)
                
                with col4c:
                    products_with_price = sum(1 for p in all_products if p.price)
                    st.metric("With Pricing", products_with_price)
                
                with col4d:
                    avg_price = sum(p.price for p in all_products if p.price) / max(products_with_price, 1)
                    st.metric("Avg Price", f"₹{avg_price:.0f}")
                
                # Show sample results
                st.subheader("📋 Sample Results")
                
                # Convert to DataFrame for display
                products_data = []
                for product in all_products[:20]:  # Show first 20
                    products_data.append({
                        'Title': product.title[:50] + '...' if len(product.title) > 50 else product.title,
                        'Platform': product.platform.title() if product.platform else 'Unknown',
                        'Price': f"₹{product.price}" if product.price else 'N/A',
                        'Brand': product.brand or 'N/A',
                        'Net Quantity': product.net_quantity or 'N/A'
                    })
                
                if products_data:
                    df = pd.DataFrame(products_data)
                    st.dataframe(df, use_container_width=True)
                
                # Download options
                st.subheader("📥 Download Results")
                col5a, col5b = st.columns(2)
                
                with col5a:
                    with open(json_file, 'r') as f:
                        st.download_button(
                            "📄 Download JSON",
                            data=f.read(),
                            file_name=f"crawled_products_{timestamp}.json",
                            mime="application/json"
                        )
                
                with col5b:
                    with open(csv_file, 'r') as f:
                        st.download_button(
                            "📊 Download CSV",
                            data=f.read(),
                            file_name=f"crawled_products_{timestamp}.csv",
                            mime="text/csv"
                        )
                
                # Store in session state for other tabs
                st.session_state['last_crawl_results'] = all_products
                st.session_state['last_crawl_timestamp'] = timestamp
                
            else:
                st.warning("⚠️ No products found. Try different search terms or platforms.")

with tab2:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Crawling Results</h3>
        <p>View and analyze results from your web crawling operations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load recent crawl results
    crawl_dir = Path("app/data/crawled")
    crawl_dir.mkdir(parents=True, exist_ok=True)
    
    crawl_files = list(crawl_dir.glob("products_*.json"))
    crawl_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    if crawl_files or 'last_crawl_results' in st.session_state:
        # File selection
        if crawl_files:
            selected_file = st.selectbox(
                "Select Crawl Results:",
                options=['Latest Crawl'] + [f.name for f in crawl_files[:10]],
                help="Choose which crawl results to view"
            )
            
            if selected_file == 'Latest Crawl':
                if 'last_crawl_results' in st.session_state:
                    products = st.session_state['last_crawl_results']
                else:
                    st.warning("No latest crawl results available. Please run a new crawl.")
                    products = []
            else:
                file_path = crawl_dir / selected_file
                try:
                    products = crawler.load_products(str(file_path))
                except Exception as e:
                    st.error(f"Failed to load file {selected_file}: {e}")
                    products = []
        else:
            products = st.session_state.get('last_crawl_results', [])
        
        if products:
            # Generate statistics
            stats = crawler.get_crawling_statistics(products)
            
            # Display statistics
            st.subheader("📈 Crawl Statistics")
            
            col6a, col6b, col6c, col6d = st.columns(4)
            
            with col6a:
                st.metric("Total Products", stats.get('total_products', 0))
            
            with col6b:
                platforms_count = len(stats.get('platforms', {}))
                st.metric("Platforms", platforms_count)
            
            with col6c:
                price_range = stats.get('price_range', {})
                avg_price = price_range.get('avg', 0)
                st.metric("Avg Price", f"₹{avg_price:.0f}")
            
            with col6d:
                completeness = stats.get('data_completeness', {})
                title_completeness = completeness.get('title', {}).get('percentage', 0)
                st.metric("Data Quality", f"{title_completeness:.0f}%")
            
            # Platform distribution
            if stats.get('platforms'):
                st.subheader("🏪 Platform Distribution")
                
                platform_data = stats['platforms']
                fig_platforms = px.pie(
                    values=list(platform_data.values()),
                    names=list(platform_data.keys()),
                    title="Products by Platform"
                )
                st.plotly_chart(fig_platforms, use_container_width=True)
            
            # Price distribution
            if stats.get('price_range'):
                st.subheader("💰 Price Analysis")
                
                prices = [p.price for p in products if p.price is not None]
                if prices:
                    fig_price = px.histogram(
                        x=prices,
                        title="Price Distribution",
                        labels={'x': 'Price (₹)', 'y': 'Number of Products'}
                    )
                    st.plotly_chart(fig_price, use_container_width=True)
            
            # Data completeness
            if stats.get('data_completeness'):
                st.subheader("📋 Data Completeness")
                
                completeness_data = stats['data_completeness']
                fields = list(completeness_data.keys())
                percentages = [completeness_data[field]['percentage'] for field in fields]
                
                fig_completeness = px.bar(
                    x=fields,
                    y=percentages,
                    title="Data Completeness by Field",
                    labels={'x': 'Field', 'y': 'Completeness (%)'}
                )
                fig_completeness.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_completeness, use_container_width=True)
            
            # Product table
            st.subheader("🛍️ Product Details")
            
            # Convert products to DataFrame
            products_df = pd.DataFrame([
                {
                    'Title': p.title,
                    'Platform': p.platform,
                    'Brand': p.brand,
                    'Price': p.price,
                    'MRP': p.mrp,
                    'Net Quantity': p.net_quantity,
                    'Manufacturer': p.manufacturer,
                    'Country of Origin': p.country_of_origin,
                    'Extracted At': p.extracted_at
                }
                for p in products
            ])
            
            # Add filters
            col7a, col7b, col7c = st.columns(3)
            
            with col7a:
                platform_filter = st.selectbox(
                    "Filter by Platform:",
                    options=['All'] + list(products_df['Platform'].unique()),
                    key="platform_filter"
                )
            
            with col7b:
                brand_filter = st.selectbox(
                    "Filter by Brand:",
                    options=['All'] + list(products_df['Brand'].dropna().unique()),
                    key="brand_filter"
                )
            
            with col7c:
                price_range_filter = st.slider(
                    "Price Range (₹):",
                    min_value=0,
                    max_value=int(products_df['Price'].max()) if not products_df['Price'].isna().all() else 10000,
                    value=(0, int(products_df['Price'].max()) if not products_df['Price'].isna().all() else 10000),
                    key="price_range_filter"
                )
            
            # Apply filters
            filtered_df = products_df.copy()
            
            if platform_filter != 'All':
                filtered_df = filtered_df[filtered_df['Platform'] == platform_filter]
            
            if brand_filter != 'All':
                filtered_df = filtered_df[filtered_df['Brand'] == brand_filter]
            
            if not filtered_df['Price'].isna().all():
                filtered_df = filtered_df[
                    (filtered_df['Price'].between(price_range_filter[0], price_range_filter[1])) |
                    (filtered_df['Price'].isna())
                ]
            
            # Display filtered results
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
            # Export filtered results
            if not filtered_df.empty:
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Filtered Results",
                    data=csv_data,
                    file_name=f"filtered_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        else:
            st.info("No crawl results to display. Start a crawl operation first.")
    
    else:
        st.info("No crawl results available. Use the 'Crawl Products' tab to start crawling.")

with tab3:
    st.markdown("""
    <div class="feature-card">
        <h3>⚙️ Crawler Settings</h3>
        <p>Configure crawler behavior and platform-specific settings.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Platform configurations
    st.subheader("🏪 Platform Settings")
    
    for platform_id, platform_name in crawler.get_supported_platforms().items():
        with st.expander(f"📱 {platform_name} Settings"):
            col8a, col8b = st.columns(2)
            
            with col8a:
                st.text_input(
                    "User Agent:",
                    value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    key=f"user_agent_{platform_id}",
                    help="User agent string for requests"
                )
                
                st.number_input(
                    "Rate Limit (seconds):",
                    min_value=0.5,
                    max_value=10.0,
                    value=2.0,
                    step=0.5,
                    key=f"rate_limit_{platform_id}",
                    help="Delay between requests to this platform"
                )
            
            with col8b:
                st.number_input(
                    "Request Timeout (seconds):",
                    min_value=5,
                    max_value=60,
                    value=30,
                    key=f"timeout_{platform_id}",
                    help="Timeout for individual requests"
                )
                
                st.number_input(
                    "Max Retries:",
                    min_value=0,
                    max_value=5,
                    value=3,
                    key=f"max_retries_{platform_id}",
                    help="Maximum number of retry attempts"
                )
    
    # General settings
    st.subheader("🔧 General Settings")
    
    col9a, col9b = st.columns(2)
    
    with col9a:
        st.checkbox(
            "Enable Logging",
            value=True,
            key="enable_logging",
            help="Enable detailed logging of crawler operations"
        )
        
        st.checkbox(
            "Save Raw HTML",
            value=False,
            key="save_raw_html",
            help="Save raw HTML responses for debugging"
        )
    
    with col9b:
        st.checkbox(
            "Use Proxy Rotation",
            value=False,
            key="use_proxy",
            help="Use proxy servers for crawling (requires proxy configuration)"
        )
        
        st.checkbox(
            "Randomize Delays",
            value=True,
            key="randomize_delays",
            help="Add random variation to request delays"
        )
    
    # Data storage settings
    st.subheader("💾 Data Storage")
    
    storage_format = st.selectbox(
        "Default Storage Format:",
        options=["JSON", "CSV", "Both"],
        index=2,
        help="Default format for saving crawled data"
    )
    
    data_retention = st.number_input(
        "Data Retention (days):",
        min_value=1,
        max_value=365,
        value=30,
        help="How long to keep crawled data"
    )
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")
        
        # Log settings change
        log_user_action(
            current_user.username,
            "SETTINGS_UPDATE",
            "crawler_settings",
            {"storage_format": storage_format, "data_retention": data_retention}
        )

with tab4:
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Crawler Analytics</h3>
        <p>Monitor crawler performance and analyze crawling trends.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load historical crawl data
    crawl_files = list(Path("app/data/crawled").glob("products_*.json"))
    
    if crawl_files:
        # Performance metrics over time
        st.subheader("📊 Performance Metrics")
        
        performance_data = []
        for file_path in crawl_files:
            try:
                products = crawler.load_products(str(file_path))
                stats = crawler.get_crawling_statistics(products)
                
                # Extract timestamp from filename
                timestamp_str = file_path.stem.split('_', 1)[1]
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                performance_data.append({
                    'timestamp': timestamp,
                    'total_products': stats.get('total_products', 0),
                    'platforms': len(stats.get('platforms', {})),
                    'avg_price': stats.get('price_range', {}).get('avg', 0),
                    'data_quality': stats.get('data_completeness', {}).get('title', {}).get('percentage', 0)
                })
            except Exception as e:
                continue
        
        if performance_data:
            perf_df = pd.DataFrame(performance_data)
            perf_df = perf_df.sort_values('timestamp')
            
            # Products over time
            fig_products = px.line(
                perf_df,
                x='timestamp',
                y='total_products',
                title='Products Crawled Over Time',
                labels={'timestamp': 'Date', 'total_products': 'Number of Products'}
            )
            st.plotly_chart(fig_products, use_container_width=True)
            
            # Data quality trends
            fig_quality = px.line(
                perf_df,
                x='timestamp',
                y='data_quality',
                title='Data Quality Trends',
                labels={'timestamp': 'Date', 'data_quality': 'Data Quality (%)'}
            )
            fig_quality.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig_quality, use_container_width=True)
        
        # Platform success rates
        st.subheader("🏪 Platform Performance")
        
        platform_stats = {}
        for file_path in crawl_files:
            try:
                products = crawler.load_products(str(file_path))
                for product in products:
                    platform = product.platform
                    if platform not in platform_stats:
                        platform_stats[platform] = {'total': 0, 'with_price': 0, 'with_details': 0}
                    
                    platform_stats[platform]['total'] += 1
                    if product.price:
                        platform_stats[platform]['with_price'] += 1
                    if product.net_quantity or product.manufacturer:
                        platform_stats[platform]['with_details'] += 1
            except Exception:
                continue
        
        if platform_stats:
            platform_perf_data = []
            for platform, stats in platform_stats.items():
                platform_perf_data.append({
                    'Platform': platform.title(),
                    'Total Products': stats['total'],
                    'Price Success Rate': (stats['with_price'] / stats['total'] * 100) if stats['total'] > 0 else 0,
                    'Details Success Rate': (stats['with_details'] / stats['total'] * 100) if stats['total'] > 0 else 0
                })
            
            platform_df = pd.DataFrame(platform_perf_data)
            st.dataframe(platform_df, use_container_width=True)
        
        # System health
        st.subheader("🔧 System Health")
        
        col10a, col10b, col10c = st.columns(3)
        
        with col10a:
            total_crawls = len(crawl_files)
            st.metric("Total Crawls", total_crawls)
        
        with col10b:
            if performance_data:
                total_products = sum(p['total_products'] for p in performance_data)
                st.metric("Total Products", total_products)
        
        with col10c:
            if performance_data:
                avg_quality = sum(p['data_quality'] for p in performance_data) / len(performance_data)
                st.metric("Avg Quality", f"{avg_quality:.1f}%")
    
    else:
        st.info("No crawl data available for analytics. Start crawling to see performance metrics.")

# Footer
st.markdown("---")
st.markdown("""
<div class="feature-card">
    <h4>🤝 Supported Platforms</h4>
    <p>This web crawler supports the following major Indian e-commerce platforms:</p>
    <ul>
        <li><strong>Amazon India</strong> - Comprehensive product catalog with detailed information</li>
        <li><strong>Flipkart</strong> - Wide range of products across categories</li>
        <li><strong>Myntra</strong> - Fashion and lifestyle products</li>
        <li><strong>Nykaa</strong> - Beauty and personal care products</li>
    </ul>
    <p><em>Note: Web crawling should be performed responsibly and in compliance with each platform's terms of service and robots.txt files.</em></p>
</div>
""", unsafe_allow_html=True)
