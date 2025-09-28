import streamlit as st
import json, pandas as pd
from pathlib import Path
from core.auth import require_auth
from datetime import datetime
from core.json_utils import safe_json_dumps

st.set_page_config(page_title="Reports - Legal Metrology Checker", page_icon="📄", layout="wide")

# Enhanced Custom CSS for Reports Page
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Reports Header */
    .reports-header {
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
    
    .reports-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="chart" width="20" height="20" patternUnits="userSpaceOnUse"><rect x="0" y="15" width="4" height="5" fill="white" opacity="0.1"/><rect x="5" y="10" width="4" height="10" fill="white" opacity="0.1"/><rect x="10" y="5" width="4" height="15" fill="white" opacity="0.1"/><rect x="15" y="12" width="4" height="8" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23chart)"/></svg>');
        opacity: 0.1;
    }
    
    .reports-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Reports Cards */
    .reports-card {
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
    
    .reports-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .reports-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-card.success {
        border-left: 4px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    .metric-card.warning {
        border-left: 4px solid #ff9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
    }
    
    .metric-card.error {
        border-left: 4px solid #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
    }
    
    /* Filter Cards */
    .filter-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .filter-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    /* Export Buttons */
    .export-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        margin: 0.5rem;
        display: inline-block;
        text-decoration: none;
    }
    
    .export-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        color: white;
        text-decoration: none;
    }
    
    /* Data Table Enhancements */
    .dataframe {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
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

# Enhanced Reports Header
st.markdown("""
<div class="reports-header">
    <h1>📄 Reports & Analytics</h1>
    <p>Comprehensive compliance reports and data analytics</p>
</div>
""", unsafe_allow_html=True)

report_path = Path("app/data/reports/validated.jsonl")
if not report_path.exists():
    st.markdown("""
    <div class="reports-card">
        <h3>⚠️ No Validations Found</h3>
        <p>No validation reports found. Please run some validations first to generate reports.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

rows = []
for line in report_path.read_text().splitlines():
    try:
        rows.append(json.loads(line))
    except Exception:
        pass

if not rows:
    st.markdown("""
    <div class="reports-card">
        <h3>⚠️ No Valid Data</h3>
        <p>No valid validation data found in the reports.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = pd.json_normalize(rows)

# Add timestamp column if not present
if 'timestamp' not in df.columns:
    df['timestamp'] = pd.Timestamp.now()

# Enhanced Filtering options
st.markdown("""
<div class="filter-card">
    <h3>🔍 Filter & Search</h3>
    <p>Customize your report view with advanced filtering options:</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    compliance_filter = st.selectbox(
        "Compliance Status",
        ["All", "Compliant Only", "Non-Compliant Only"],
        help="Filter results by compliance status"
    )

with col2:
    min_score = st.slider(
        "Minimum Score",
        min_value=0,
        max_value=100,
        value=0,
        help="Show only results with score above this threshold"
    )

with col3:
    search_term = st.text_input(
        "Search in filename",
        placeholder="Enter filename to search...",
        help="Filter by filename containing this text"
    )

# Apply filters
filtered_df = df.copy()

if compliance_filter == "Compliant Only":
    filtered_df = filtered_df[filtered_df['is_compliant'] == True]
elif compliance_filter == "Non-Compliant Only":
    filtered_df = filtered_df[filtered_df['is_compliant'] == False]

filtered_df = filtered_df[filtered_df['score'] >= min_score]

if search_term:
    filtered_df = filtered_df[filtered_df['file'].str.contains(search_term, case=False, na=False)]

# Enhanced Summary statistics
st.markdown("""
<div class="reports-card">
    <h3>📊 Summary Statistics</h3>
    <p>Key metrics and compliance overview:</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📋 {len(df)}</h3>
        <p>Total Records</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    compliant_count = df['is_compliant'].sum()
    compliance_rate = compliant_count/len(df)*100
    metric_class = "success" if compliance_rate >= 80 else "warning" if compliance_rate >= 60 else "error"
    st.markdown(f"""
    <div class="metric-card {metric_class}">
        <h3>✅ {compliant_count}</h3>
        <p>Compliant ({compliance_rate:.1f}%)</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_score = df['score'].mean()
    score_class = "success" if avg_score >= 80 else "warning" if avg_score >= 60 else "error"
    st.markdown(f"""
    <div class="metric-card {score_class}">
        <h3>📈 {avg_score:.1f}/100</h3>
        <p>Average Score</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🔍 {len(filtered_df)}</h3>
        <p>Filtered Results</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Export options
st.markdown("""
<div class="reports-card">
    <h3>📥 Export Options</h3>
    <p>Download your compliance reports in various formats:</p>
</div>
""", unsafe_allow_html=True)

export_format = st.radio(
    "Select export format:",
    ["CSV", "JSON", "Excel", "PDF Report"],
    horizontal=True,
    label_visibility="collapsed"
)

if st.button("Generate Export", type="primary"):
    if export_format == "CSV":
        csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download CSV", 
            data=csv_bytes, 
            file_name=f"compliance_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
            mime="text/csv"
        )
    
    elif export_format == "JSON":
        json_data = filtered_df.to_dict('records')
        json_bytes = safe_json_dumps(json_data, indent=2).encode('utf-8')
        st.download_button(
            "Download JSON", 
            data=json_bytes, 
            file_name=f"compliance_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 
            mime="application/json"
        )
    
    elif export_format == "Excel":
        # Create Excel file with multiple sheets
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, sheet_name='Validation Results', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': ['Total Files', 'Compliant Files', 'Non-Compliant Files', 'Average Score', 'Highest Score', 'Lowest Score'],
                'Value': [
                    len(df),
                    df['is_compliant'].sum(),
                    (~df['is_compliant']).sum(),
                    f"{df['score'].mean():.1f}",
                    df['score'].max(),
                    df['score'].min()
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        buffer.seek(0)
        st.download_button(
            "Download Excel", 
            data=buffer.getvalue(), 
            file_name=f"compliance_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    elif export_format == "PDF Report":
        st.info("PDF export feature coming soon! Use Excel export for now.")

# Data preview with enhanced display
st.subheader("📋 Data Preview")
if len(filtered_df) > 0:
    # Select columns to display
    display_columns = ['file', 'is_compliant', 'score']
    if 'fields.mrp_value' in filtered_df.columns:
        display_columns.extend(['fields.mrp_value', 'fields.net_quantity_value', 'fields.unit'])
    
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    
    if available_columns:
        display_df = filtered_df[available_columns].copy()
        display_df.columns = [col.replace('fields.', '').replace('_', ' ').title() for col in display_df.columns]
        display_df['Compliant'] = display_df['Is Compliant'].map({True: '✅ Yes', False: '❌ No'})
        
        st.dataframe(
            display_df, 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("No data matches your current filters.")

# Issue analysis
if 'issues' in filtered_df.columns and len(filtered_df) > 0:
    st.subheader("🔍 Issue Analysis")
    
    # Count issues by type
    all_issues = []
    for issues_list in filtered_df['issues']:
        if isinstance(issues_list, list):
            all_issues.extend([issue.get('field', 'Unknown') for issue in issues_list])
    
    if all_issues:
        issue_counts = pd.Series(all_issues).value_counts()
        st.bar_chart(issue_counts.head(10))
    else:
        st.info("No issues found in the data.")
