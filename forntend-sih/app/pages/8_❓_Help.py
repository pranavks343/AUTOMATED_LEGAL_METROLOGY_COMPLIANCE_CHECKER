import streamlit as st
from core.auth import require_auth, get_current_user
from core.error_handler import show_success_message, show_warning_message, show_error_message

st.set_page_config(page_title="Help - Legal Metrology Checker", page_icon="❓", layout="wide")

# Enhanced Custom CSS for Help Page
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Help Header */
    .help-header {
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
    
    .help-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="help" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="8" fill="none" stroke="white" opacity="0.1" stroke-width="2"/><path d="M10 6v4M10 14h.01" stroke="white" opacity="0.1" stroke-width="2"/></pattern></defs><rect width="100" height="100" fill="url(%23help)"/></svg>');
        opacity: 0.1;
    }
    
    .help-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Help Cards */
    .help-card {
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
    
    .help-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .help-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Feature Cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .feature-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Step Cards */
    .step-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .step-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .step-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    }
    
    /* Help Tab Styling */
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

# Enhanced Help Header
st.markdown(f"""
<div class="help-header">
    <h1>❓ Help & Documentation</h1>
    <p>Welcome to the help center, <strong>{current_user.username}</strong>! Find answers and guidance for using the Legal Metrology Compliance Checker.</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for different help topics
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🚀 Getting Started", 
    "📥 File Upload", 
    "🔍 Validation", 
    "📊 Reports", 
    "👑 Admin Features", 
    "🆘 Troubleshooting"
])

with tab1:
    st.markdown("""
    <div class="help-card">
        <h3>🚀 Getting Started</h3>
        <p>Welcome to the Legal Metrology Compliance Checker! This application helps you validate product listings against Indian Legal Metrology regulations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="help-card">
        <h4>📋 Quick Start Guide</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-card">
        <h4>1. 📥 Upload Your Data</h4>
        <p>Go to the Ingest page to upload product images or paste text. Multiple files are supported for bulk processing.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-card">
        <h4>2. 🔍 Review Extractions</h4>
        <p>Check the Extraction page to see what fields were identified. Verify MRP, quantities, dates, and other compliance-related information.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-card">
        <h4>3. ✅ Run Validation</h4>
        <p>Use the Validation page to check compliance. Choose single file or bulk processing based on your needs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-card">
        <h4>4. 📊 View Results</h4>
        <p>Check dashboards for analytics and export reports for documentation and regulatory compliance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="help-card">
        <h4>🌟 Key Features</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h5>🔍 OCR Processing</h5>
        <p>Extract text from product images with advanced optical character recognition technology.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h5>📦 Bulk Validation</h5>
        <p>Process multiple files at once for efficient compliance checking and batch processing.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h5>👥 Role-based Access</h5>
        <p>Different features and permissions for users and administrators with secure authentication.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-card">
        <h5>📊 Comprehensive Reporting</h5>
        <p>Export data in multiple formats including CSV, JSON, Excel, and PDF for regulatory compliance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h5>📝 Audit Logging</h5>
        <p>Track all user activities and system changes with comprehensive audit trails for compliance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="help-card">
        <h4>🎯 Workflow Overview</h4>
        <p>Understand the complete compliance validation process from data input to final reporting.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a visual workflow
    st.markdown("""
    ```
    Upload Files → Extract Fields → Validate Rules → Generate Reports
         ↓              ↓              ↓              ↓
    📥 Ingest      🔍 Extraction   ✅ Validation   📄 Reports
    ```

    **Each step builds on the previous one:**
    - **Ingest**: Prepare your data (images or text)
    - **Extraction**: AI identifies key compliance fields
    - **Validation**: Rules engine checks compliance
    - **Reports**: Export results for documentation
    """)

with tab2:
    st.subheader("📥 File Upload Guide")
    
    st.markdown("""
    ### Supported File Types
    
    **Images:**
    - PNG, JPG, JPEG formats
    - Maximum size: 10 MB per file
    - Multiple files supported
    
    **Text:**
    - Direct text input
    - Product descriptions
    - Manual data entry
    
    ### Best Practices for Image Upload
    
    ✅ **Good Image Quality:**
    - High resolution and clear text
    - Good contrast between text and background
    - Proper lighting
    - Product label clearly visible
    
    ❌ **Poor Image Quality:**
    - Blurry or low resolution
    - Poor lighting or shadows
    - Text partially obscured
    - Extreme angles or distortion
    
    ### Text Input Guidelines
    
    **Include these key fields:**
    - MRP (Maximum Retail Price)
    - Net Quantity
    - Unit of measurement
    - Manufacturer name
    - Country of origin
    - Manufacturing/Expiry dates (if applicable)
    
    **Example format:**
    ```
    MRP: ₹199
    Net Quantity: 500 g
    Manufactured by: ABC Foods Ltd.
    Country of Origin: India
    Mfg Date: 01/01/2024
    Exp Date: 31/12/2025
    ```
    """)

with tab3:
    st.subheader("🔍 Validation Process")
    
    st.markdown("""
    ### How Validation Works
    
    The system checks your product data against Legal Metrology rules:
    
    #### Required Fields Check
    - ✅ MRP (Maximum Retail Price)
    - ✅ Net Quantity
    - ✅ Unit of measurement
    - ✅ Manufacturer name
    - ✅ Country of origin
    
    #### Field Validation Rules
    
    **MRP Validation:**
    - Must include currency symbol (₹, Rs, INR)
    - Value within acceptable range
    - Proper formatting
    
    **Unit Validation:**
    - Standard units: g, kg, ml, l, cm, mm, m, pcs, piece, pack
    - Case-insensitive matching
    
    **Quantity Validation:**
    - Minimum quantity thresholds
    - Numeric value validation
    
    **Date Validation:**
    - Manufacturing date required
    - Expiry date optional
    - Proper date format
    
    ### Understanding Scores
    
    **Compliance Score (0-100):**
    - 100: Perfect compliance
    - 80-99: Minor issues (warnings)
    - 60-79: Some compliance issues
    - Below 60: Major compliance problems
    
    **Issue Levels:**
    - 🔴 **ERROR**: Critical compliance violations
    - 🟡 **WARN**: Minor issues or recommendations
    - 🔵 **INFO**: Informational messages
    """)

with tab4:
    st.subheader("📊 Reports & Analytics")
    
    st.markdown("""
    ### Report Types
    
    **📋 Validation Reports:**
    - Individual file results
    - Bulk processing summaries
    - Compliance scores and issues
    
    **📈 Analytics Dashboard:**
    - System-wide statistics
    - User activity tracking
    - Compliance trends
    
    ### Export Formats
    
    **CSV Export:**
    - Spreadsheet-compatible format
    - All validation data included
    - Easy to analyze in Excel
    
    **JSON Export:**
    - Machine-readable format
    - Complete data structure
    - API integration ready
    
    **Excel Export:**
    - Multiple sheets
    - Summary statistics
    - Formatted for presentation
    
    ### Filtering & Search
    
    **Available Filters:**
    - Compliance status (All/Compliant/Non-compliant)
    - Minimum score threshold
    - Filename search
    - Date range (if available)
    
    **Search Features:**
    - Case-insensitive text search
    - Partial filename matching
    - Real-time filtering
    """)

with tab5:
    st.subheader("👑 Admin Features")
    
    if current_user.role.value == "admin":
        st.markdown("""
        ### Admin Dashboard Features
        
        **👥 User Management:**
        - View all registered users
        - Toggle user active/inactive status
        - Create new users with specific roles
        - User activity tracking
        
        **📊 System Analytics:**
        - System-wide validation statistics
        - Compliance rate monitoring
        - Score distribution analysis
        - Recent activity overview
        
        **⚙️ System Settings:**
        - Application configuration
        - OCR settings management
        - Notification preferences
        - Session timeout settings
        
        **📝 Audit Logs:**
        - Complete user activity tracking
        - Action filtering and search
        - Export audit data
        - Log maintenance tools
        
        **🔧 Maintenance:**
        - Data cleanup utilities
        - System health checks
        - User data export
        - Diagnostic tools
        """)
        
        st.success("✅ You have admin access to all these features!")
    else:
        st.info("🔒 Admin features are only available to users with admin privileges.")
        st.markdown("""
        **Admin capabilities include:**
        - User management and monitoring
        - System-wide analytics
        - Audit log access
        - System configuration
        - Maintenance tools
        """)

with tab6:
    st.subheader("🆘 Troubleshooting")
    
    st.markdown("""
    ### Common Issues & Solutions
    
    #### 🔍 OCR Problems
    
    **Issue**: "Tesseract OCR not found"
    **Solution**: 
    - macOS: `brew install tesseract`
    - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
    - Windows: Download from official Tesseract website
    
    **Issue**: Poor OCR accuracy
    **Solutions**:
    - Use higher quality images
    - Ensure good lighting and contrast
    - Try manual text input as alternative
    - Check image format (PNG/JPG recommended)
    
    #### 📁 File Upload Issues
    
    **Issue**: "File too large"
    **Solution**: 
    - Compress images before upload
    - Maximum size: 10 MB per file
    - Use image optimization tools
    
    **Issue**: "Invalid file type"
    **Solution**:
    - Supported formats: PNG, JPG, JPEG
    - Convert other formats using image editors
    
    #### ✅ Validation Problems
    
    **Issue**: Low compliance scores
    **Solutions**:
    - Check all required fields are present
    - Verify data format and accuracy
    - Review validation rules in settings
    - Ensure proper units and formatting
    
    **Issue**: Missing field errors
    **Solutions**:
    - Double-check text extraction results
    - Manually add missing information
    - Verify image quality and OCR accuracy
    
    #### 🔐 Authentication Issues
    
    **Issue**: Login problems
    **Solutions**:
    - Verify username and password
    - Check caps lock and keyboard layout
    - Clear browser cache and cookies
    - Try different browser
    
    **Issue**: Session timeout
    **Solutions**:
    - Log in again
    - Check internet connection
    - Clear browser data if persistent
    """)
    
    st.subheader("🆘 Getting Additional Help")
    
    st.markdown("""
    ### Support Resources
    
    **📧 Contact Support:**
    - Email: support@metrology.com
    - Response time: 24-48 hours
    
    **📞 Phone Support:**
    - Number: +91-XXX-XXXX-XXXX
    - Hours: 9 AM - 6 PM IST (Monday-Friday)
    
    **💬 Live Chat:**
    - Available during business hours
    - Real-time assistance
    
    **📚 Documentation:**
    - User manual: Available in admin panel
    - API documentation: For developers
    - Video tutorials: Coming soon
    
    ### System Information
    
    **Current User**: {current_user.username}
    **Role**: {current_user.role.value.title()}
    **App Version**: 1.0.0
    **Last Updated**: 2024-01-15
    """)

# Add a feedback section
st.markdown("---")
st.subheader("💬 Feedback & Suggestions")

with st.form("feedback_form"):
    feedback_type = st.selectbox(
        "Feedback Type",
        ["Bug Report", "Feature Request", "General Feedback", "Documentation Issue"]
    )
    
    feedback_message = st.text_area(
        "Your Message",
        placeholder="Please describe your feedback, issue, or suggestion...",
        height=100
    )
    
    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High", "Critical"]
    )
    
    if st.form_submit_button("Submit Feedback", type="primary"):
        if feedback_message.strip():
            show_success_message(
                "Feedback submitted successfully!",
                "Thank you for helping us improve the application."
            )
            
            # Log the feedback (could be stored in database or file)
            import json
            from datetime import datetime
            from pathlib import Path
            
            feedback_data = {
                "timestamp": datetime.now().isoformat(),
                "user": current_user.username,
                "type": feedback_type,
                "message": feedback_message,
                "priority": priority
            }
            
            # Save feedback to file
            feedback_file = Path("app/data/feedback.jsonl")
            feedback_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(feedback_file, "a") as f:
                f.write(json.dumps(feedback_data) + "\n")
        else:
            show_error_message("Please enter your feedback message")
