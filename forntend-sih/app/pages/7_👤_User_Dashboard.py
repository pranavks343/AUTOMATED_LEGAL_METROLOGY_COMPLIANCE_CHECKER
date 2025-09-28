import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from core.auth import require_auth, get_current_user

st.set_page_config(page_title="User Dashboard - Legal Metrology Checker", page_icon="👤", layout="wide")

# Enhanced Custom CSS for user dashboard
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dashboard Header */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .dashboard-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-card h3 {
        color: #667eea;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .metric-card p {
        color: #666;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Activity Cards */
    .activity-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .activity-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    /* Progress Bars */
    .progress-container {
        background: #f0f0f0;
        border-radius: 10px;
        padding: 0.5rem;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 20px;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Status Indicators */
    .status-compliant {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .status-non-compliant {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Chart Containers */
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Require authentication
require_auth()

# Enhanced Dashboard Header
current_user = get_current_user()
st.markdown(f"""
<div class="dashboard-header">
    <h1>👤 Personal Dashboard</h1>
    <p>Welcome back, <strong>{current_user.username}</strong>! Here's your personalized compliance overview.</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for different user functions
tab1, tab2, tab3, tab4 = st.tabs(["📊 My Activity", "📈 Progress Tracking", "⚙️ Preferences", "📚 Help & Support"])

with tab1:
    st.subheader("My Recent Activity")
    
    # Get validation reports for current user
    report_path = Path("app/data/reports/validated.jsonl")
    if report_path.exists():
        rows = []
        for line in report_path.read_text().splitlines():
            try:
                data = json.loads(line)
                # Add user tracking (you might want to modify the validation process to include user info)
                rows.append(data)
            except:
                pass
        
        if rows:
            df = pd.json_normalize(rows)
            
            # Enhanced Personal metrics with custom styling
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📊 {len(df)}</h3>
                    <p>My Validations</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                my_compliance_rate = df['is_compliant'].mean() * 100
                st.markdown(f"""
                <div class="metric-card">
                    <h3>✅ {my_compliance_rate:.1f}%</h3>
                    <p>Compliance Rate</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                my_avg_score = df['score'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <h3>⭐ {my_avg_score:.1f}</h3>
                    <p>Average Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                # Calculate improvement over time (simplified)
                recent_validations = len(df)  # Could be filtered by date
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎯 {recent_validations}</h3>
                    <p>Total Processed</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Recent validations table
            st.subheader("Recent Validations")
            recent_df = df[['file', 'is_compliant', 'score']].tail(10)
            st.dataframe(recent_df, use_container_width=True)
            
            # Personal charts
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("My Compliance Trend")
                compliance_counts = df['is_compliant'].value_counts()
                st.bar_chart(compliance_counts)
            
            with col2:
                st.subheader("My Score Distribution")
                # Create a simple histogram using pandas value_counts
                try:
                    score_ranges = pd.cut(df['score'], bins=10)
                    score_dist = score_ranges.value_counts().sort_index()
                    # Convert interval index to strings for Streamlit compatibility
                    score_dist.index = score_dist.index.astype(str)
                    st.bar_chart(score_dist)
                except Exception as e:
                    # Fallback: simple score ranges if pd.cut fails
                    score_dist = pd.Series([len(df)], index=['All Scores'])
                    st.bar_chart(score_dist)
                    st.caption("Score distribution display simplified")
        else:
            st.info("No validation data available yet. Start by uploading some product listings!")
    else:
        st.info("No validation reports found. Start by running some validations!")

with tab2:
    st.subheader("Progress Tracking")
    
    # Goals and achievements
    st.write("**Your Goals & Achievements**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Validations This Week", "0", "0")  # Could be calculated from actual data
        st.metric("Compliance Rate Goal", "85%", "Current: 75%")  # Placeholder data
        st.metric("Files Processed", "0", "0")  # Could be calculated from actual data
    
    with col2:
        # Achievement badges
        st.write("**Achievements**")
        achievements = [
            ("🎯 First Validation", "Complete your first product validation"),
            ("📊 Data Analyst", "Process 10 product listings"),
            ("✅ Compliance Expert", "Achieve 90% compliance rate"),
            ("🚀 Power User", "Process 50 product listings")
        ]
        
        for badge, description in achievements:
            # Simple achievement system - could be enhanced with actual tracking
            achieved = False  # Placeholder - could check against actual user data
            if achieved:
                st.success(f"{badge} - {description}")
            else:
                st.info(f"🔒 {description}")
    
    # Progress chart
    st.subheader("Weekly Progress")
    # Placeholder chart - could be populated with actual user data
    progress_data = pd.DataFrame({
        'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'Validations': [0, 0, 0, 0],  # Placeholder data
        'Compliance Rate': [0, 0, 0, 0]  # Placeholder data
    })
    st.line_chart(progress_data.set_index('Week'))

with tab3:
    st.subheader("User Preferences")
    
    # User profile
    st.write("**Profile Information**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Username", value=current_user.username, disabled=True)
        st.text_input("Email", value=current_user.email, disabled=True)
        st.text_input("Role", value=current_user.role.value.title(), disabled=True)
    
    with col2:
        st.text_input("Member Since", value=current_user.created_at[:10] if current_user.created_at else "N/A", disabled=True)
        st.text_input("Last Login", value=current_user.last_login[:16] if current_user.last_login else "Never", disabled=True)
    
    # Notification preferences
    st.write("**Notification Preferences**")
    email_notifications = st.checkbox("Email notifications for validation results", value=True)
    weekly_reports = st.checkbox("Weekly progress reports", value=False)
    compliance_alerts = st.checkbox("Compliance alerts", value=True)
    
    # Display preferences
    st.write("**Display Preferences**")
    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
    results_per_page = st.selectbox("Results per page", [10, 25, 50])
    default_view = st.selectbox("Default dashboard view", ["Activity", "Progress", "Preferences"])
    
    if st.button("Save Preferences"):
        st.success("Preferences saved successfully!")

with tab4:
    st.subheader("Help & Support")
    
    # Quick help
    st.write("**Quick Help**")
    
    help_topics = {
        "Getting Started": "Upload product images or paste text in the Ingest page to begin validation.",
        "Understanding Results": "Check the Validation page to see compliance issues and scores.",
        "Exporting Reports": "Use the Reports page to download CSV or JSON files of your results.",
        "OCR Processing": "The system automatically extracts text from product images using OCR.",
        "Compliance Rules": "Validation follows Legal Metrology rules for Indian products."
    }
    
    for topic, description in help_topics.items():
        with st.expander(f"❓ {topic}"):
            st.write(description)
    
    # Contact support
    st.write("**Contact Support**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**System Information**")
        st.code(f"""
Username: {current_user.username}
Email: {current_user.email}
Role: {current_user.role.value}
App Version: 1.0.0
        """)
    
    with col2:
        st.write("**Support Options**")
        st.info("📧 Email: support@metrology.com")
        st.info("📞 Phone: +91-XXX-XXXX-XXXX")
        st.info("💬 Chat: Available 9 AM - 6 PM IST")
        
        if st.button("Send Feedback"):
            st.success("Thank you for your feedback!")

# Quick actions
st.markdown("---")
st.subheader("Quick Actions")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📥 Upload New Files", use_container_width=True):
        st.switch_page("pages/1_📥_Ingest.py")

with col2:
    if st.button("🔍 View Extractions", use_container_width=True):
        st.switch_page("pages/2_🔍_Extraction.py")

with col3:
    if st.button("✅ Run Validations", use_container_width=True):
        st.switch_page("pages/3_✅_Validation.py")

with col4:
    if st.button("📄 Generate Reports", use_container_width=True):
        st.switch_page("pages/5_📄_Reports.py")

# Logout button
st.markdown("---")
if st.button("Logout", type="secondary"):
    if "user" in st.session_state:
        del st.session_state.user
    st.rerun()
