import streamlit as st
from pathlib import Path
from core.auth import is_authenticated, get_current_user, is_admin, UserRole

st.set_page_config(page_title="Legal Metrology Compliance Checker", page_icon="⚖️", layout="wide")

BASE_URL = "http://localhost:2066/api/compliance"
 

# Enhanced Custom CSS for premium styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Header with Gradient */
    .main-header {
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
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.1;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 1rem 0 0 0;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Feature Cards with Enhanced Design */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
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
    
    /* Metric Cards with Glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
    }
    
    .metric-card h3 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-card p {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Navigation Cards */
    .nav-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        text-decoration: none;
        display: block;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(240, 147, 251, 0.4);
    }
    
    .nav-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(240, 147, 251, 0.6);
        text-decoration: none;
        color: white;
    }
    
    .nav-card h4 {
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0;
    }
    
    .nav-card p {
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background: #4CAF50; }
    .status-offline { background: #f44336; }
    .status-pending { background: #ff9800; }
    
    /* Button Enhancements */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Sidebar Enhancements */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4198 100%);
    }
    
    /* Alert Boxes */
    .alert-success {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2e7d32;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1565c0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #ef6c00;
    }
</style>
""", unsafe_allow_html=True)

# Check authentication status
if not is_authenticated():
    st.title("⚖️ Legal Metrology Compliance Checker")
    st.markdown("### Please log in to access the application")
    st.info("🔐 **Authentication Required**: Please log in to use the Legal Metrology Compliance Checker.")
    st.page_link("pages/0_🔐_Login.py", label="Go to Login →", icon="🔐")
    st.stop()

# User is authenticated - show main app
current_user = get_current_user()

# Sidebar with user info and navigation
with st.sidebar:
    st.success(f"Welcome, {current_user.username}!")
    st.caption(f"Role: {current_user.role.value.title()}")
    
    # Role-based navigation
    if current_user.role == UserRole.ADMIN:
        st.markdown("### 👑 Admin Navigation")
        st.page_link("pages/6_👑_Admin_Dashboard.py", label="Admin Dashboard", icon="👑")
        st.page_link("pages/15_🏛️_Regulatory_Dashboard.py", label="Regulatory Dashboard", icon="🏛️")
        st.page_link("pages/14_🌐_Web_Crawler.py", label="Web Crawler", icon="🌐")
        st.page_link("pages/9_📋_Complaint_Management.py", label="Complaint Management", icon="📋")
        st.page_link("pages/10_📦_ERP_Product_Management.py", label="ERP Product Management", icon="📦")
        st.page_link("pages/11_🔧_Physical_Systems_Integration.py", label="Physical Systems Integration", icon="🔧")
        st.page_link("pages/17_🔌_Physical_Scanner.py", label="Physical Barcode Scanner", icon="🔌")
        st.markdown("---")
    
    st.markdown("### 📊 User Navigation")
    st.page_link("pages/7_👤_User_Dashboard.py", label="My Dashboard", icon="👤")
    st.page_link("pages/8_❓_Help.py", label="Help & Documentation", icon="❓")
    st.markdown("---")
    
    st.markdown("### 🔧 Main Workflow")
    st.markdown("""1. **Ingest**: Upload images or paste product text
2. **Extraction**: See what fields were extracted
3. **Validation**: Run rule checks
4. **Dashboard**: View analytics across processed listings
5. **Reports**: Export CSV/JSON reports
""")

# Enhanced Main Header
st.markdown("""
<div class="main-header">
    <h1>⚖️ Legal Metrology Compliance Checker</h1>
    <p>Automated Compliance Validation for Legal Metrology (India)</p>
</div>
""", unsafe_allow_html=True)

# Welcome message with enhanced styling
st.markdown(f"""
<div class="feature-card">
    <h3>🎉 Welcome back, {current_user.username}!</h3>
    <p>Your comprehensive Legal Metrology compliance solution is ready. This advanced system scans product listings, extracts compliance data, validates against regulatory rules, and generates detailed reports.</p>
</div>
""", unsafe_allow_html=True)

# Enhanced Quick stats with glassmorphism
st.markdown("### 📊 Your Dashboard Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <h3>👤 {current_user.role.value.title()}</h3>
        <p>User Role</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <h3>🟢 Active</h3>
        <p>Account Status</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <h3>📅 {current_user.created_at[:10] if current_user.created_at else "N/A"}</h3>
        <p>Member Since</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
        <h3>🕒 {current_user.last_login[:16] if current_user.last_login else "Never"}</h3>
        <p>Last Login</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced workflow section
st.markdown("""
<div class="feature-card">
    <h3>🚀 Quick Start Guide</h3>
    <p><strong>💡 Tip:</strong> Start with the <strong>Ingest</strong> page to upload your sample listings and begin the compliance validation process.</p>
    <div style="display: flex; gap: 1rem; margin-top: 1rem;">
        <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">1. Upload</span>
        <span style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">2. Extract</span>
        <span style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">3. Validate</span>
        <span style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">4. Report</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced navigation section
st.markdown("### 🎯 Main Workflow Navigation")

# Create enhanced navigation cards
nav_cards = [
    {
        "title": "📥 Ingest",
        "description": "Upload images and product data",
        "link": "pages/1_📥_Ingest.py",
        "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    },
    {
        "title": "🔍 Extraction", 
        "description": "View extracted fields and data",
        "link": "pages/2_🔍_Extraction.py",
        "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
    },
    {
        "title": "✅ Validation",
        "description": "Run compliance rule checks",
        "link": "pages/3_✅_Validation.py", 
        "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
    },
    {
        "title": "📊 Analytics",
        "description": "View comprehensive dashboards",
        "link": "pages/4_📊_Dashboard.py",
        "gradient": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
    }
]

col1, col2, col3, col4 = st.columns(4)
for i, card in enumerate(nav_cards):
    with [col1, col2, col3, col4][i]:
        st.markdown(f"""
        <div class="nav-card" style="background: {card['gradient']};">
            <h4>{card['title']}</h4>
            <p>{card['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add clickable link
        if st.button(f"Go to {card['title']}", key=f"nav_{i}", type="primary"):
            st.switch_page(card['link'])

# Secondary navigation
st.markdown("### 📋 Additional Tools")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="nav-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
        <h4>📄 Reports</h4>
        <p>Export detailed compliance reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📄 Go to Reports", key="reports_btn", type="primary"):
        st.switch_page("pages/5_📄_Reports.py")

with col2:
    st.markdown(f"""
    <div class="nav-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <h4>🤖 AI Assistant</h4>
        <p>Get intelligent suggestions and guidance</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🤖 Chat with AI", key="ai_btn", type="primary"):
        st.switch_page("pages/12_🤖_AI_Assistant.py")

with col3:
    st.markdown(f"""
    <div class="nav-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
        <h4>🚪 Logout</h4>
        <p>Sign out of your account</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", key="logout_btn", type="secondary"):
        if "user" in st.session_state:
            del st.session_state.user
        st.rerun()

# System status indicator
st.markdown("""
<div class="feature-card">
    <h3>🟢 System Status</h3>
    <p>All systems operational • Legal Metrology compliance validation active • Real-time processing enabled</p>
    <div style="display: flex; gap: 1rem; margin-top: 1rem;">
        <span class="status-indicator status-online"></span><span>Authentication: Active</span>
        <span class="status-indicator status-online"></span><span>Validation Engine: Running</span>
        <span class="status-indicator status-online"></span><span>Database: Connected</span>
    </div>
</div>
""", unsafe_allow_html=True)
