import streamlit as st
import pandas as pd
from pathlib import Path
from core.rules_engine import load_rules, validate
from core.schemas import ValidationIssue
from core.nlp_extract import extract_fields
from core.auth import require_auth, get_current_user
from core.audit_logger import log_user_action
from core.json_utils import safe_json_dumps
from core.chatbot import chatbot
import json, os
from datetime import datetime

st.set_page_config(page_title="Validation - Legal Metrology Checker", page_icon="✅", layout="wide")

# Enhanced Custom CSS for Validation Page
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Validation Header */
    .validation-header {
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
    
    .validation-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="check" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M6 10l3 3 6-6" stroke="white" opacity="0.1" stroke-width="2" fill="none"/></pattern></defs><rect width="100" height="100" fill="url(%23check)"/></svg>');
        opacity: 0.1;
    }
    
    .validation-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Validation Cards */
    .validation-card {
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
    
    .validation-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .validation-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    }
    
    /* Compliance Status Cards */
    .compliance-card {
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
    
    .compliance-card.compliant {
        border-left: 4px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    .compliance-card.non-compliant {
        border-left: 4px solid #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
    }
    
    .compliance-card.warning {
        border-left: 4px solid #ff9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
    }
    
    /* Issue Cards */
    .issue-card {
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
    
    .issue-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .issue-card.critical {
        border-left: 4px solid #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.05) 0%, rgba(244, 67, 54, 0.02) 100%);
    }
    
    .issue-card.warning {
        border-left: 4px solid #ff9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.05) 0%, rgba(255, 152, 0, 0.02) 100%);
    }
    
    .issue-card.info {
        border-left: 4px solid #2196F3;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.05) 0%, rgba(33, 150, 243, 0.02) 100%);
    }
    
    /* Score Display */
    .score-display {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .score-display::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    }
    
    /* Progress Bars */
    .progress-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        height: 8px;
        border-radius: 4px;
        transition: width 0.3s ease;
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

# Enhanced Validation Header
st.markdown(f"""
<div class="validation-header">
    <h1>✅ Compliance Validation</h1>
    <p>Welcome, <strong>{current_user.username}</strong>! Validate your product data against Legal Metrology regulations.</p>
</div>
""", unsafe_allow_html=True)

rules_path = Path("app/data/rules/legal_metrology_rules.yaml")
rules = load_rules(str(rules_path))

uploads_dir = Path("app/data/uploads")
uploads = sorted(list(uploads_dir.glob("*.txt")))

if not uploads:
    st.markdown("""
    <div class="validation-card">
        <h3>⚠️ No Files Found</h3>
        <p>No uploaded files found. Please go to the <strong>Ingest</strong> page first to upload your product data.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Enhanced Validation mode selection
st.markdown("""
<div class="validation-card">
    <h3>🔧 Validation Mode</h3>
    <p>Choose how you want to validate your product data:</p>
</div>
""", unsafe_allow_html=True)

validation_mode = st.radio(
    "Select validation mode:",
    ["Single File", "Bulk Process All Files"],
    help="Choose to validate one file at a time or process all uploaded files in bulk",
    label_visibility="collapsed"
)

if validation_mode == "Single File":
    target = st.selectbox("Select a file to validate", uploads, index=0)
    text = Path(target).read_text()
    fields = extract_fields(text)

    # OCR boxes (not persisted from ingest to keep simple); we pass None here
    result = validate(fields, rules, ocr_boxes=None)

    # Enhanced Results Display
    st.markdown("""
    <div class="validation-card">
        <h3>📊 Validation Results</h3>
        <p>Compliance analysis for the selected file:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Compliance Score Display
    score_class = "compliant" if result.is_compliant else "non-compliant"
    st.markdown(f"""
    <div class="score-display">
        <h2>📈 Compliance Score</h2>
        <h1 style="color: {'#4CAF50' if result.is_compliant else '#f44336'}; margin: 1rem 0;">{result.score}/100</h1>
        <p style="font-size: 1.2rem; margin: 0;">{'✅ Compliant' if result.is_compliant else '❌ Non-compliant'}</p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced Issues Display
    st.markdown("""
    <div class="validation-card">
        <h3>🔍 Issues Analysis</h3>
        <p>Detailed breakdown of compliance issues found:</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not result.issues:
        st.markdown("""
        <div class="compliance-card compliant">
            <h3>🎉 Perfect Compliance!</h3>
            <p>No issues found. Your product data meets all Legal Metrology requirements.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for it in result.issues:
            issue_class = "critical" if it.level == "error" else "warning" if it.level == "warning" else "info"
            st.markdown(f"""
            <div class="issue-card {issue_class}">
                <h4>{'🚨' if it.level == 'error' else '⚠️' if it.level == 'warning' else 'ℹ️'} {it.level.title()} - {it.field}</h4>
                <p>{it.message}</p>
            </div>
            """, unsafe_allow_html=True)

    # Save a JSON line to reports
    os.makedirs("app/data/reports", exist_ok=True)
    report_line = {
        "timestamp": datetime.now().isoformat(),
        "file": str(target),
        "fields": fields.model_dump(),
        "is_compliant": result.is_compliant,
        "score": result.score,
        "issues": [i.model_dump() for i in result.issues],
        "user": current_user.username
    }
    with open("app/data/reports/validated.jsonl", "a") as f:
        f.write(safe_json_dumps(report_line) + "\n")
    st.info("Saved this validation to app/data/reports/validated.jsonl")
    
    # Log the validation action
    log_user_action(
        current_user.username,
        "VALIDATION_RUN",
        f"file:{target.name}",
        {
            "is_compliant": result.is_compliant,
            "score": result.score,
            "issues_count": len(result.issues)
        }
    )
    
    # AI Assistant Suggestions
    st.markdown("""
    <div class="validation-card">
        <h3>🤖 AI Assistant Suggestions</h3>
        <p>Get intelligent recommendations based on your validation results:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate AI suggestions
    ai_suggestions = chatbot.analyze_validation_result(result, fields)
    
    for suggestion in ai_suggestions:
        if "🎉" in suggestion:
            st.markdown(f"""
            <div class="compliance-card compliant">
                <h4>{suggestion}</h4>
            </div>
            """, unsafe_allow_html=True)
        elif "🚨" in suggestion or "🔴" in suggestion:
            st.markdown(f"""
            <div class="compliance-card non-compliant">
                <h4>{suggestion}</h4>
            </div>
            """, unsafe_allow_html=True)
        elif "⚠️" in suggestion or "🟡" in suggestion:
            st.markdown(f"""
            <div class="compliance-card warning">
                <h4>{suggestion}</h4>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="compliance-card">
                <h4>{suggestion}</h4>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick action to chat with AI
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Ask AI Assistant", use_container_width=True):
            st.switch_page("pages/12_🤖_AI_Assistant.py")
    
    with col2:
        # Copy validation result to clipboard for AI analysis
        result_json = {
            "is_compliant": result.is_compliant,
            "score": result.score,
            "issues": [{"level": issue.level, "field": issue.field, "message": issue.message} for issue in result.issues],
            "fields": fields.model_dump()
        }
        st.download_button(
            "📋 Copy Results",
            data=safe_json_dumps(result_json, indent=2),
            file_name="validation_result.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        if st.button("📊 View Reports", use_container_width=True):
            st.switch_page("pages/5_📄_Reports.py")

else:  # Bulk Process All Files
    st.subheader("🔄 Bulk Validation")
    st.info(f"Processing {len(uploads)} files...")
    
    if st.button("Start Bulk Validation", type="primary"):
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, upload_file in enumerate(uploads):
            status_text.text(f"Processing {upload_file.name}...")
            progress_bar.progress((i + 1) / len(uploads))
            
            try:
                text = upload_file.read_text()
                fields = extract_fields(text)
                result = validate(fields, rules, ocr_boxes=None)
                
                # Save result
                report_line = {
                    "timestamp": datetime.now().isoformat(),
                    "file": str(upload_file),
                    "fields": fields.model_dump(),
                    "is_compliant": result.is_compliant,
                    "score": result.score,
                    "issues": [i.model_dump() for i in result.issues],
                    "user": current_user.username
                }
                results.append(report_line)
                
                # Save to file
                os.makedirs("app/data/reports", exist_ok=True)
                with open("app/data/reports/validated.jsonl", "a") as f:
                    f.write(safe_json_dumps(report_line) + "\n")
                    
            except Exception as e:
                st.error(f"Error processing {upload_file.name}: {str(e)}")
        
        status_text.text("Bulk validation completed!")
        progress_bar.progress(1.0)
        
        # Calculate summary statistics
        compliant_count = sum(1 for r in results if r['is_compliant'])
        avg_score = sum(r['score'] for r in results) / len(results) if results else 0
        
        # Log bulk validation action
        log_user_action(
            current_user.username,
            "BULK_VALIDATION",
            f"files:{len(uploads)}",
            {
                "total_files": len(uploads),
                "compliant_count": compliant_count,
                "avg_score": avg_score
            }
        )
        
        st.subheader("📊 Bulk Validation Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", len(results))
        with col2:
            st.metric("Compliant Files", compliant_count)
        with col3:
            st.metric("Average Score", f"{avg_score:.1f}/100")
        
        # Detailed results table
        if results:
            st.subheader("Detailed Results")
            results_df = pd.DataFrame([
                {
                    'File': Path(r['file']).name,
                    'Compliant': '✅' if r['is_compliant'] else '❌',
                    'Score': r['score'],
                    'Issues': len(r['issues'])
                }
                for r in results
            ])
            st.dataframe(results_df, use_container_width=True)
