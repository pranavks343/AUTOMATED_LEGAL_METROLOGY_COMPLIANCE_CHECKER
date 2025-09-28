import streamlit as st
from pathlib import Path
from core.nlp_extract import extract_fields
from core.auth import require_auth
from core.chatbot import chatbot
from core.json_utils import safe_json_dumps
import json

st.set_page_config(page_title="Extraction - Legal Metrology Checker", page_icon="🔍", layout="wide")

# Enhanced Custom CSS for Extraction Page
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Extraction Header */
    .extraction-header {
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
    
    .extraction-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="search" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="6" fill="none" stroke="white" opacity="0.1" stroke-width="2"/><path d="M15 15l5 5" stroke="white" opacity="0.1" stroke-width="2" fill="none"/></pattern></defs><rect width="100" height="100" fill="url(%23search)"/></svg>');
        opacity: 0.1;
    }
    
    .extraction-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Extraction Cards */
    .extraction-card {
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
    
    .extraction-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .extraction-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Field Display Cards */
    .field-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .field-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .field-card.high-confidence {
        border-left-color: #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    .field-card.medium-confidence {
        border-left-color: #ff9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
    }
    
    .field-card.low-confidence {
        border-left-color: #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
    }
    
    /* Suggestion Cards */
    .suggestion-card {
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
    
    .suggestion-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .suggestion-card.success {
        border-left: 4px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.05) 0%, rgba(76, 175, 80, 0.02) 100%);
    }
    
    .suggestion-card.warning {
        border-left: 4px solid #ff9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.05) 0%, rgba(255, 152, 0, 0.02) 100%);
    }
    
    .suggestion-card.info {
        border-left: 4px solid #2196F3;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.05) 0%, rgba(33, 150, 243, 0.02) 100%);
    }
    
    /* Progress Indicator */
    .progress-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 8px;
        border-radius: 4px;
        transition: width 0.3s ease;
        margin: 1rem 0;
    }
    
    /* Confidence Score */
    .confidence-score {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .confidence-score::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Quick Actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        text-decoration: none;
        display: inline-block;
        text-align: center;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        color: white;
        text-decoration: none;
    }
    
    /* Alert Enhancements */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

def generate_suggestions(fields, confidence_score, extracted_count):
    """Generate intelligent suggestions based on extraction results"""
    suggestions = []
    
    # High confidence suggestions
    if confidence_score >= 80:
        suggestions.append({
            "type": "success",
            "message": "Excellent extraction quality! All major fields were successfully extracted.",
            "action_button": "Run Validation",
            "page_link": "pages/3_✅_Validation.py"
        })
        
        suggestions.append({
            "type": "action",
            "message": "Your data is ready for Legal Metrology compliance validation.",
            "action_button": "View Dashboard",
            "page_link": "pages/7_👤_User_Dashboard.py"
        })
    
    # Medium confidence suggestions
    elif confidence_score >= 60:
        suggestions.append({
            "type": "warning",
            "message": "Good extraction, but some fields are missing. Consider running validation to identify specific issues.",
            "action_button": "Validate Anyway",
            "page_link": "pages/3_✅_Validation.py"
        })
        
        suggestions.append({
            "type": "info",
            "message": "You can also try uploading a clearer image or manually editing the extracted text.",
            "action_button": "Upload New File",
            "page_link": "pages/1_📥_Ingest.py"
        })
    
    # Low confidence suggestions
    else:
        suggestions.append({
            "type": "warning",
            "message": "Low extraction quality detected. Only a few fields were found.",
            "action_button": "Upload Better Image",
            "page_link": "pages/1_📥_Ingest.py"
        })
        
        suggestions.append({
            "type": "info",
            "message": "Consider using a higher resolution image or better lighting for better OCR results.",
            "action_button": "View Help",
            "page_link": "pages/8_❓_Help.py"
        })
    
    # Field-specific suggestions
    if not fields.mrp_raw:
        suggestions.append({
            "type": "warning",
            "message": "MRP (Maximum Retail Price) not found. This is a critical field for Legal Metrology compliance.",
            "action_button": "Check Image Quality",
            "page_link": "pages/1_📥_Ingest.py"
        })
    
    if not fields.net_quantity_raw:
        suggestions.append({
            "type": "warning",
            "message": "Net quantity information missing. This is required for Legal Metrology compliance.",
            "action_button": "Upload New Image",
            "page_link": "pages/1_📥_Ingest.py"
        })
    
    if not fields.manufacturer_name:
        suggestions.append({
            "type": "info",
            "message": "Manufacturer name not detected. This field is important for product identification.",
            "action_button": "Try Different Image",
            "page_link": "pages/1_📥_Ingest.py"
        })
    
    if not fields.country_of_origin:
        suggestions.append({
            "type": "info",
            "message": "Country of origin not found. This information is often required for compliance.",
            "action_button": "Manual Review",
            "page_link": "pages/3_✅_Validation.py"
        })
    
    # Additional field suggestions
    if fields.extra:
        if 'batch_number' in fields.extra:
            suggestions.append({
                "type": "success",
                "message": f"Great! Batch number found: {fields.extra['batch_number']}. This helps with product traceability.",
                "action_button": None
            })
        
        if 'fssai_number' in fields.extra:
            suggestions.append({
                "type": "success",
                "message": f"Excellent! FSSAI number detected: {fields.extra['fssai_number']}. This is important for food safety compliance.",
                "action_button": None
            })
    
    # Process multiple files suggestion
    uploads_dir = Path("app/data/uploads")
    files = sorted(list(uploads_dir.glob("*.txt")))
    if len(files) > 1:
        suggestions.append({
            "type": "action",
            "message": f"You have {len(files)} files uploaded. Consider running bulk validation for efficiency.",
            "action_button": "Bulk Validate All Files",
            "page_link": "pages/3_✅_Validation.py"
        })
    
    # Reports suggestion
    suggestions.append({
        "type": "info",
        "message": "View your validation history and generate compliance reports.",
        "action_button": "View Reports",
        "page_link": "pages/5_📄_Reports.py"
    })
    
    # Admin features suggestion (if applicable)
    if hasattr(st.session_state, 'user_role') and st.session_state.user_role == 'ADMIN':
        suggestions.append({
            "type": "action",
            "message": "As an admin, you can monitor system health and manage users.",
            "action_button": "Admin Dashboard",
            "page_link": "pages/6_👑_Admin_Dashboard.py"
        })
    
    return suggestions

# Require authentication
require_auth()

# Enhanced Extraction Header
st.markdown("""
<div class="extraction-header">
    <h1>🔍 Field Extraction</h1>
    <p>AI-powered text analysis and field extraction from product listings</p>
</div>
""", unsafe_allow_html=True)


uploads_dir = Path("app/data/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)

files = sorted(list(uploads_dir.glob("*.txt")))
if not files:
    st.markdown("""
    <div class="extraction-card">
        <h3>⚠️ No Files Found</h3>
        <p>No uploaded/pasted files found. Please go to the <strong>Ingest</strong> page first to upload your product data.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="extraction-card">
        <h3>📁 File Selection</h3>
        <p>Choose a file to extract fields from:</p>
    </div>
    """, unsafe_allow_html=True)
    
    f = st.selectbox("Choose a file to extract from", files, index=0, label_visibility="collapsed")
    text = f.read_text()
    
    st.markdown("""
    <div class="extraction-card">
        <h3>📄 Raw Text Preview</h3>
        <p>First 2000 characters of the uploaded text:</p>
    </div>
    """, unsafe_allow_html=True)
    st.code(text[:2000] + ("…" if len(text) > 2000 else ""), language="text")

    fields = extract_fields(text)
    
    # Enhanced Quick Actions Panel
    st.markdown("""
    <div class="extraction-card">
        <h3>🚀 Quick Actions</h3>
        <p>Choose your next step based on the extraction results:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Validate Now", type="primary", use_container_width=True):
            st.switch_page("pages/3_✅_Validation.py")
    
    with col2:
        if st.button("📊 View Reports", use_container_width=True):
            st.switch_page("pages/5_📄_Reports.py")
    
    with col3:
        if st.button("👤 My Dashboard", use_container_width=True):
            st.switch_page("pages/7_👤_User_Dashboard.py")
    
    with col4:
        if st.button("📥 Upload More", use_container_width=True):
            st.switch_page("pages/1_📥_Ingest.py")
    
    # Enhanced Extracted Fields Section
    st.markdown("""
    <div class="extraction-card">
        <h3>📊 Extracted Fields</h3>
        <p>Fields automatically extracted from your product text:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display main fields in a structured format
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="field-card">
            <h4>💰 Price Information</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if fields.mrp_raw:
            st.markdown(f"""
            <div class="field-card high-confidence">
                <strong>✅ MRP:</strong> {fields.mrp_raw}
                {f'<br><strong>Value:</strong> ₹{fields.mrp_value}' if fields.mrp_value else ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="field-card low-confidence">
                <strong>❌ MRP:</strong> Not found
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="field-card">
            <h4>📦 Quantity Information</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if fields.net_quantity_raw:
            st.markdown(f"""
            <div class="field-card high-confidence">
                <strong>✅ Net Quantity:</strong> {fields.net_quantity_raw}
                {f'<br><strong>Unit:</strong> {fields.unit}' if fields.unit else ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="field-card low-confidence">
                <strong>❌ Net Quantity:</strong> Not found
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="field-card">
            <h4>🏭 Manufacturer Information</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if fields.manufacturer_name:
            st.markdown(f"""
            <div class="field-card high-confidence">
                <strong>✅ Manufacturer:</strong> {fields.manufacturer_name}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="field-card low-confidence">
                <strong>❌ Manufacturer:</strong> Not found
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="field-card">
            <h4>🌍 Origin Information</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if fields.country_of_origin:
            st.markdown(f"""
            <div class="field-card high-confidence">
                <strong>✅ Country of Origin:</strong> {fields.country_of_origin}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="field-card low-confidence">
                <strong>❌ Country of Origin:</strong> Not found
            </div>
            """, unsafe_allow_html=True)
    
    # Display dates
    st.markdown("**📅 Date Information**")
    col1, col2 = st.columns(2)
    
    with col1:
        if fields.mfg_date:
            st.success(f"✅ Manufacturing Date: {fields.mfg_date}")
        else:
            st.warning("⚠️ Manufacturing Date not found")
    
    with col2:
        if fields.expiry_date:
            st.success(f"✅ Expiry Date: {fields.expiry_date}")
        else:
            st.info("ℹ️ Expiry Date not found (optional)")
    
    # Display additional fields if any
    if fields.extra:
        st.markdown("**📋 Additional Information**")
        for key, value in fields.extra.items():
            st.info(f"**{key.replace('_', ' ').title()}**: {value}")
    
    # Extraction confidence indicator
    st.markdown("---")
    extracted_count = sum([
        1 for field in [fields.mrp_raw, fields.net_quantity_raw, fields.unit, 
                       fields.manufacturer_name, fields.country_of_origin, fields.mfg_date]
        if field
    ])
    
    confidence_score = (extracted_count / 6) * 100
    
    if confidence_score >= 80:
        st.success(f"🎯 **High Confidence Extraction** ({confidence_score:.0f}%)")
    elif confidence_score >= 60:
        st.warning(f"⚠️ **Medium Confidence Extraction** ({confidence_score:.0f}%)")
    else:
        st.error(f"❌ **Low Confidence Extraction** ({confidence_score:.0f}%)")
    
    st.info(f"**Extracted {extracted_count}/6 main fields**")
    
    # Raw JSON for technical users
    with st.expander("🔧 Raw Extraction Data (JSON)"):
        st.json(fields.model_dump())
    
    # Store in session state for validation page
    st.session_state["last_extracted_fields"] = fields.model_dump()
    st.session_state["last_selected_file"] = str(f)
    
    # Progress Indicator
    st.markdown("---")
    st.subheader("📈 Extraction Progress")
    
    progress_col1, progress_col2, progress_col3 = st.columns([2, 1, 1])
    
    with progress_col1:
        st.progress(confidence_score / 100)
        st.caption(f"Extraction Quality: {confidence_score:.0f}%")
    
    with progress_col2:
        st.metric("Fields Found", f"{extracted_count}/6")
    
    with progress_col3:
        status = "🟢 Ready" if confidence_score >= 80 else "🟡 Review" if confidence_score >= 60 else "🔴 Issues"
        st.markdown(f"**Status:** {status}")
    
    # Enhanced Next Steps Suggestion Box
    st.markdown("""
    <div class="extraction-card">
        <h3>💡 What's Next? - Intelligent Suggestions</h3>
        <p>AI-powered recommendations based on your extraction results:</p>
    </div>
    """, unsafe_allow_html=True)
    
    suggestions = generate_suggestions(fields, confidence_score, extracted_count)
    
    # Group suggestions by priority
    priority_suggestions = []
    general_suggestions = []
    
    for suggestion in suggestions:
        if suggestion["type"] in ["warning", "success"] and "action_button" in suggestion:
            priority_suggestions.append(suggestion)
        else:
            general_suggestions.append(suggestion)
    
    # Display priority suggestions first
    if priority_suggestions:
        st.markdown("### 🎯 **Priority Actions**")
        for i, suggestion in enumerate(priority_suggestions, 1):
            with st.container():
                col1, col2 = st.columns([1, 10])
                
                with col1:
                    if suggestion["type"] == "success":
                        st.markdown("🟢")
                    else:
                        st.markdown("🟡")
                
                with col2:
                    if suggestion["type"] == "success":
                        st.success(f"{suggestion['message']}")
                    elif suggestion["type"] == "warning":
                        st.warning(f"{suggestion['message']}")
                    
                    if "action_button" in suggestion:
                        if st.button(suggestion["action_button"], key=f"priority_{i}", type="primary"):
                            if "page_link" in suggestion:
                                st.switch_page(suggestion["page_link"])
    
    # Display general suggestions
    if general_suggestions:
        st.markdown("### 📋 **Additional Options**")
        for i, suggestion in enumerate(general_suggestions, 1):
            with st.container():
                col1, col2 = st.columns([1, 10])
                
                with col1:
                    if suggestion["type"] == "info":
                        st.markdown("🔵")
                    elif suggestion["type"] == "action":
                        st.markdown("⚡")
                    else:
                        st.markdown("ℹ️")
                
                with col2:
                    if suggestion["type"] == "info":
                        st.info(f"{suggestion['message']}")
                    elif suggestion["type"] == "action":
                        st.markdown(f"**{suggestion['message']}**")
                    else:
                        st.write(f"{suggestion['message']}")
                    
                    if "action_button" in suggestion:
                        if st.button(suggestion["action_button"], key=f"general_{i}"):
                            if "page_link" in suggestion:
                                st.switch_page(suggestion["page_link"])
    
    # AI Assistant Suggestions
    st.markdown("""
    <div class="extraction-card">
        <h3>🤖 AI Assistant Analysis</h3>
        <p>Intelligent analysis of your extraction results:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate AI suggestions
    ai_suggestions = chatbot.analyze_extraction_result(fields, confidence_score)
    
    for suggestion in ai_suggestions:
        if "🔍" in suggestion and "Excellent" in suggestion:
            st.markdown(f"""
            <div class="suggestion-card success">
                <h4>{suggestion}</h4>
            </div>
            """, unsafe_allow_html=True)
        elif "🚨" in suggestion or "Low" in suggestion:
            st.markdown(f"""
            <div class="suggestion-card warning">
                <h4>{suggestion}</h4>
            </div>
            """, unsafe_allow_html=True)
        elif "⚠️" in suggestion or "Moderate" in suggestion:
            st.markdown(f"""
            <div class="suggestion-card warning">
                <h4>{suggestion}</h4>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="suggestion-card">
                <h4>{suggestion}</h4>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick action to chat with AI
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Ask AI Assistant", use_container_width=True):
            st.switch_page("pages/12_🤖_AI_Assistant.py")
    
    with col2:
        # Copy extraction result for AI analysis
        result_json = {
            "fields": fields.model_dump(),
            "confidence_score": confidence_score,
            "extracted_count": extracted_count
        }
        st.download_button(
            "📋 Copy Results",
            data=safe_json_dumps(result_json, indent=2),
            file_name="extraction_result.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        if st.button("✅ Validate Results", use_container_width=True):
            st.switch_page("pages/3_✅_Validation.py")
    
    # Summary and tips
    st.markdown("---")
    with st.expander("💡 **Pro Tips for Better Extraction**"):
        st.markdown("""
        **📸 Image Quality Tips:**
        - Use high-resolution images (minimum 1080p)
        - Ensure good lighting and contrast
        - Avoid shadows and reflections
        - Keep the product label flat and straight
        
        **🔍 Text Recognition Tips:**
        - Ensure text is clearly visible and not blurred
        - Avoid handwritten text when possible
        - Use images with high contrast between text and background
        - Crop the image to focus on the product label
        
        **⚡ Performance Tips:**
        - Upload multiple files for bulk processing
        - Use the bulk validation feature for efficiency
        - Check your extraction results before validation
        - Save your work frequently
        """)
