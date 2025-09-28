import streamlit as st
from core.auth import AuthManager, UserRole

st.set_page_config(page_title="Login - Legal Metrology Checker", page_icon="🔐", layout="wide")

# Enhanced Custom CSS for login page
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Login Container */
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin: 2rem auto;
        max-width: 500px;
    }
    
    /* Login Header */
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    
    .login-header p {
        font-size: 1.1rem;
        color: #666;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
    }
    
    /* Form Styling */
    .stForm {
        background: transparent !important;
    }
    
    .stTextInput > div > div > input {
        border-radius: 15px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        box-shadow: 0 5px 15px rgba(240, 147, 251, 0.4) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.6) !important;
    }
    
    /* Feature Cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Alert Styling */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
    }
    
    /* Role Selection Cards */
    .role-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .role-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    .role-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Background Animation */
    body {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
</style>
""", unsafe_allow_html=True)

# Main login container
st.markdown("""
<div class="login-container">
    <div class="login-header">
        <h1>⚖️ Legal Metrology</h1>
        <p>Compliance Checker</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("### 🔐 Welcome Back!")
st.markdown("Sign in to access your Legal Metrology compliance dashboard.")

# Initialize auth manager
auth_manager = AuthManager()

# Login form
with st.form("login_form"):
    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        login_button = st.form_submit_button("🚀 Login", type="primary")
    with col2:
        register_button = st.form_submit_button("📝 Register", type="secondary")

    if login_button:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            user = auth_manager.authenticate(username, password)
            if user:
                st.session_state.user = user
                st.success(f"Welcome back, {user.username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    if register_button:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            # For registration, we'll show a role selection modal
            st.session_state.show_registration_form = True
            st.session_state.registration_username = username
            st.session_state.registration_password = password
            st.rerun()

# Registration form (shown when register button is clicked)
if st.session_state.get("show_registration_form", False):
    st.markdown("""
    <div class="feature-card">
        <h3>📝 Create New Account</h3>
        <p>Select your role and complete your registration to get started with Legal Metrology compliance validation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("registration_form"):
        # Display account info
        st.markdown(f"""
        <div style="background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <strong>👤 Username:</strong> {st.session_state.registration_username}<br>
            <strong>🔒 Password:</strong> {'*' * len(st.session_state.registration_password)}
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("📧 Email Address", placeholder="Enter your email address")
        
        st.markdown("### 🎯 Select Account Type")
        
        # Enhanced role selection with cards
        col1, col2 = st.columns(2)
        
        with col1:
            user_selected = st.checkbox("👤 User Account", value=True)
            st.markdown("""
            <div class="role-card">
                <h4>👤 Standard User</h4>
                <p>• Access to compliance validation<br>
                • View reports and analytics<br>
                • Upload and process products<br>
                • Limited system access</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            admin_selected = st.checkbox("👑 Admin Account", value=False)
            st.markdown("""
            <div class="role-card">
                <h4>👑 Administrator</h4>
                <p>• Full system access<br>
                • User management<br>
                • System configuration<br>
                • All compliance features</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Determine role based on selection
        if admin_selected and not user_selected:
            role_choice = "Admin"
        else:
            role_choice = "User"
            user_selected = True
        
        # Show warning for admin registration
        if role_choice == "Admin":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                <h4>⚠️ Admin Registration Notice</h4>
                <p>Admin accounts have full system access including user management, system settings, and all data. Only register as Admin if you need administrative privileges.</p>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            confirm_register = st.form_submit_button("🚀 Create Account", type="primary")
        with col2:
            cancel_register = st.form_submit_button("❌ Cancel", type="secondary")
        
        if confirm_register:
            if not email:
                st.error("Please enter your email address.")
            else:
                role = UserRole.ADMIN if role_choice == "Admin" else UserRole.USER
                success = auth_manager.create_user(
                    st.session_state.registration_username, 
                    email, 
                    st.session_state.registration_password, 
                    role
                )
                if success:
                    st.success(f"{role_choice} account '{st.session_state.registration_username}' created successfully! You can now login.")
                    # Clear registration form state
                    st.session_state.show_registration_form = False
                    st.session_state.registration_username = None
                    st.session_state.registration_password = None
                    st.rerun()
                else:
                    st.error("Username already exists. Please choose a different username.")
        
        if cancel_register:
            # Clear registration form state
            st.session_state.show_registration_form = False
            st.session_state.registration_username = None
            st.session_state.registration_password = None
            st.rerun()

# Close login container
st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; color: rgba(255, 255, 255, 0.8);">
    <p>⚖️ <strong>Legal Metrology Compliance Checker</strong></p>
    <p>Automated compliance validation for Legal Metrology (India)</p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">© 2024 - Secure • Reliable • Compliant</p>
</div>
""", unsafe_allow_html=True)


# Check if already logged in
if "user" in st.session_state and st.session_state.user:
    st.success(f"Already logged in as: {st.session_state.user.username} ({st.session_state.user.role.value})")
    if st.button("Logout"):
        del st.session_state.user
        st.rerun()
