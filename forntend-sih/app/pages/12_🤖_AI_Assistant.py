import streamlit as st
from datetime import datetime
from core.auth import require_auth, get_current_user
from core.schemas import ValidationResult, ExtractedFields
import json
import os

# Import RAG chatbot (with fallback to old chatbot)
try:
    import sys
    from pathlib import Path
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.compliance_chatbot import get_compliance_chatbot
    RAG_AVAILABLE = True
except ImportError as e:
    RAG_AVAILABLE = False
    # Fallback to old chatbot
    try:
        from core.chatbot import chatbot, ChatMessageType
    except ImportError:
        # If old chatbot also fails, set up basic fallback
        chatbot = None
        ChatMessageType = None

st.set_page_config(page_title="AI Assistant - Legal Metrology Checker", page_icon="🤖", layout="wide")

# Enhanced Custom CSS for Chatbot Page
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Chatbot Header */
    .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .chatbot-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Chat Container */
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        min-height: 500px;
        max-height: 600px;
        overflow-y: auto;
    }
    
    /* Message Bubbles */
    .message-bubble {
        margin: 1rem 0;
        padding: 1rem 1.5rem;
        border-radius: 20px;
        max-width: 80%;
        word-wrap: break-word;
        position: relative;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .message-bubble.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }
    
    .message-bubble.assistant {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #333;
        border: 1px solid #dee2e6;
        border-bottom-left-radius: 5px;
    }
    
    .message-bubble.system {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        text-align: center;
        margin: 0.5rem auto;
        max-width: 90%;
        font-size: 0.9rem;
    }
    
    .message-timestamp {
        font-size: 0.7rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    
    /* Input Area */
    .input-container {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Custom Scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
</style>
""", unsafe_allow_html=True)

# Require authentication
require_auth()
current_user = get_current_user()

# Enhanced Chatbot Header with RAG status
rag_status = "🟢 RAG-Powered" if RAG_AVAILABLE else "🟡 Fallback Mode"
st.markdown(f"""
<div class="chatbot-header">
    <h1>🤖 AI Compliance Assistant</h1>
    <p>Welcome, <strong>{current_user.username}</strong>! Ask me anything about Legal Metrology compliance.</p>
    <p><small>{rag_status} • Intelligent responses with context-grounded answers</small></p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for chat
if "chat_context" not in st.session_state:
    st.session_state.chat_context = {}
if "current_response" not in st.session_state:
    st.session_state.current_response = None
if "rag_chatbot" not in st.session_state:
    if RAG_AVAILABLE:
        try:
            st.session_state.rag_chatbot = get_compliance_chatbot()
        except Exception as e:
            st.error(f"⚠️ RAG chatbot initialization failed: {e}")
            st.info("💡 Make sure you have:")
            st.info("1. Set OPENAI_API_KEY in your .env file")
            st.info("2. Built the RAG index: `python scripts/build_rag_index.py`")
            st.info("3. Installed all dependencies: `pip install -r requirements.txt`")
            st.session_state.rag_chatbot = None
    else:
        st.session_state.rag_chatbot = None

# Chat Interface
st.markdown("""
<div class="input-container">
""", unsafe_allow_html=True)

# Display RAG system status and info
if RAG_AVAILABLE and st.session_state.rag_chatbot:
    with st.expander("🔍 RAG System Status", expanded=False):
        try:
            rag_stats = st.session_state.rag_chatbot.get_rag_stats()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Chunks", rag_stats.get('total_chunks', 'N/A'))
            with col2:
                st.metric("Source Files", rag_stats.get('total_source_files', 'N/A'))
            with col3:
                st.metric("Status", "✅ Ready" if rag_stats.get('status') == 'Index loaded' else "❌ Error")
        except:
            st.warning("Unable to load RAG statistics")

# Chat Container - Display current response if available
if st.session_state.current_response:
    st.markdown("### 🤖 AI Response:")
    st.markdown(st.session_state.current_response)
else:
    if RAG_AVAILABLE and st.session_state.rag_chatbot:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <p>🤖 <strong>RAG-Powered AI Assistant Ready!</strong></p>
            <p>Ask me about Legal Metrology compliance, validation issues, extraction problems, or any compliance questions.</p>
            <p><small>My responses are grounded in official Legal Metrology rules and regulations.</small></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <p>Type your question below and get instant AI assistance.</p>
            <p><small>⚠️ RAG system not available - using fallback mode</small></p>
        </div>
        """, unsafe_allow_html=True)

# Chat Input
user_input = st.text_input(
    "Type your message:",
    placeholder="Ask me about compliance, validation, extraction, or anything else...",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    send_button = st.button("Send", type="primary", use_container_width=True)

with col2:
    if st.button("Clear Response", use_container_width=True):
        st.session_state.current_response = None
        if RAG_AVAILABLE and st.session_state.rag_chatbot:
            st.session_state.rag_chatbot.clear_conversation()
        st.rerun()

with col3:
    if RAG_AVAILABLE and st.session_state.rag_chatbot:
        if st.button("📊 Conversation Summary", use_container_width=True):
            try:
                summary = st.session_state.rag_chatbot.get_conversation_summary()
                st.info(f"💬 {summary.get('total_messages', 0)} messages | ⏱️ {summary.get('session_duration', '0 minutes')}")
            except:
                st.warning("Unable to get conversation summary")

st.markdown("</div>", unsafe_allow_html=True)

# Process user input
if send_button and user_input:
    with st.spinner("🤖 Thinking..."):
        try:
            if RAG_AVAILABLE and st.session_state.rag_chatbot:
                # Use RAG-powered chatbot
                response = st.session_state.rag_chatbot.chat(user_input)
            else:
                # Fallback to old chatbot
                response = chatbot.get_contextual_response(user_input, st.session_state.chat_context)
            
            # Store response in session state for display
            st.session_state.current_response = response
            
        except Exception as e:
            st.error(f"❌ Error generating response: {e}")
            st.session_state.current_response = f"""
⚠️ **Error occurred while generating response**

Please try:
1. Check your internet connection
2. Verify your OpenAI API key in .env file
3. Ensure the RAG index is built: `python scripts/build_rag_index.py`
4. Try a simpler question

*Error details: {str(e)}*
            """
    
    # Rerun to display response
    st.rerun()

# Add helpful examples and tips
if not st.session_state.current_response:
    st.markdown("---")
    st.markdown("### 💡 Try asking about:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📋 Compliance Questions:**
        - "Is MRP mandatory for e-commerce?"
        - "What units for net quantity?"
        - "Penalties for violations?"
        - "BIS certification requirements?"
        """)
    
    with col2:
        st.markdown("""
        **🔧 Technical Questions:**
        - "How to improve OCR accuracy?"
        - "Best image quality for extraction?"
        - "Bulk processing recommendations?"
        - "API integration guidance?"
        """)

# Add setup instructions if RAG is not available
if not RAG_AVAILABLE or not st.session_state.rag_chatbot:
    st.markdown("---")
    st.warning("⚠️ **RAG System Not Available**")
    st.markdown("""
    **To enable the full RAG-powered AI Assistant:**
    
    1. **Install dependencies:**
       ```bash
       pip install openai faiss-cpu python-dotenv
       ```
    
    2. **Configure environment:**
       ```bash
       cp .env.example .env
       # Edit .env and add your OPENAI_API_KEY
       ```
    
    3. **Build RAG index:**
       ```bash
       python scripts/build_rag_index.py
       ```
    
    4. **Restart the application**
    """)

# Footer with system info
st.markdown("---")
system_info = f"""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    System: {'🟢 RAG-Powered' if RAG_AVAILABLE and st.session_state.rag_chatbot else '🟡 Fallback Mode'} | 
    User: {current_user.username} | 
    Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}
</div>
"""
st.markdown(system_info, unsafe_allow_html=True)