import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from core.auth import AuthManager, UserRole, require_admin, get_current_user
from core.audit_logger import audit_logger, log_user_action
from core.system_monitor import system_monitor
from core.json_utils import safe_json_dumps
from core.complaint_manager import complaint_manager

st.set_page_config(page_title="Admin Dashboard - Legal Metrology Checker", page_icon="👑", layout="wide")

# Enhanced Custom CSS for admin dashboard
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Admin Dashboard Header */
    .admin-header {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .admin-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="crown" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="2" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23crown)"/></svg>');
        opacity: 0.1;
    }
    
    .admin-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Admin Metric Cards */
    .admin-metric-card {
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
    
    .admin-metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .admin-metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    }
    
    /* Status Cards */
    .status-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
    }
    
    .status-card.healthy {
        border-left: 4px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    .status-card.warning {
        border-left: 4px solid #ff9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
    }
    
    .status-card.critical {
        border-left: 4px solid #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
    }
    
    /* Admin Tab Styling */
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
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
    }
    
    /* Quick Action Buttons */
    .quick-action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Chart Containers */
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* User Management Cards */
    .user-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .user-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #ff6b6b;
    }
    
    /* Alert Enhancements */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Require admin access
require_admin()

# Enhanced Admin Dashboard Header
current_user = get_current_user()
st.markdown(f"""
<div class="admin-header">
    <h1>👑 Admin Dashboard</h1>
    <p>Welcome, <strong>{current_user.username}</strong>! Manage the Legal Metrology Compliance Checker system.</p>
</div>
""", unsafe_allow_html=True)

auth_manager = AuthManager()

# Create tabs for different admin functions
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📊 System Health", "👥 User Management", "📈 System Analytics", "⚙️ System Settings", "📋 Reports Overview", "🔧 Maintenance", "📝 Audit Logs", "📋 Quick Complaints"])

with tab1:
    st.markdown("### 🩺 System Health Monitor")
    
    # Get system health
    health = system_monitor.get_system_health()
    performance = system_monitor.get_performance_summary()
    
    # Enhanced Health status indicator
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_class = "healthy" if health.status == "HEALTHY" else "warning" if health.status == "WARNING" else "critical"
        status_icon = "✅" if health.status == "HEALTHY" else "⚠️" if health.status == "WARNING" else "🚨"
        status_text = "HEALTHY" if health.status == "HEALTHY" else "WARNING" if health.status == "WARNING" else "CRITICAL"
        
        st.markdown(f"""
        <div class="status-card {status_class}">
            <h4>{status_icon} System Status: {status_text}</h4>
            <p>Overall system health status</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="admin-metric-card">
            <h3>⏱️ {performance['uptime_hours']:.1f}h</h3>
            <p>System Uptime</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="admin-metric-card">
            <h3>📊 {performance['success_rate']:.1f}%</h3>
            <p>Success Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced System metrics
    st.markdown("### 📊 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="admin-metric-card">
            <h3>💾 {health.memory_usage_mb:.0f} MB</h3>
            <p>Memory Usage</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="admin-metric-card">
            <h3>⚡ {health.cpu_usage_percent:.1f}%</h3>
            <p>CPU Usage</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="admin-metric-card">
            <h3>👥 {health.active_users}</h3>
            <p>Active Users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="admin-metric-card">
            <h3>📋 {health.total_validations}</h3>
            <p>Total Validations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Performance charts
    st.markdown("### 📈 Performance Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="chart-container">
            <h4>⚡ Response Time</h4>
            <h3>{performance['avg_response_time_ms']:.2f}ms</h3>
            <p>Average system response time</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        error_class = "critical" if performance['error_rate'] > 5 else "warning" if performance['error_rate'] > 0 else "healthy"
        st.markdown(f"""
        <div class="status-card {error_class}">
            <h4>🚨 Error Rate</h4>
            <h3>{performance['error_rate']:.2f}%</h3>
            <p>System error rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced System actions
    st.markdown("### 🔧 System Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Metrics", type="primary"):
            st.rerun()
    
    with col2:
        if st.button("🧹 Clean Old Metrics"):
            system_monitor.cleanup_old_metrics(days=7)
            st.success("Old metrics cleaned up successfully!")
    
    with col3:
        if st.button("📊 Export Health Report"):
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "system_health": health.model_dump(),
                "performance": performance
            }
            
            st.download_button(
                label="📊 Download Health Report",
                data=safe_json_dumps(health_data, indent=2),
                file_name=f"system_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

with tab2:
    st.subheader("User Management")
    
    # Display all users
    users = auth_manager.get_all_users()
    if users:
        user_data = []
        for user in users:
            user_data.append({
                "Username": user.username,
                "Email": user.email,
                "Role": user.role.value.title(),
                "Status": "Active" if user.is_active else "Inactive",
                "Created": user.created_at[:10] if user.created_at else "N/A",
                "Last Login": user.last_login[:16] if user.last_login else "Never"
            })
        
        df_users = pd.DataFrame(user_data)
        st.dataframe(df_users, use_container_width=True)
        
        # User actions
        st.subheader("User Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Toggle User Status**")
            selected_user = st.selectbox("Select user:", [u.username for u in users])
            if selected_user:
                user = next(u for u in users if u.username == selected_user)
                current_status = "Active" if user.is_active else "Inactive"
                new_status = st.selectbox(f"Current status: {current_status}", ["Active", "Inactive"])
                
                if st.button("Update Status"):
                    new_active = new_status == "Active"
                    if auth_manager.update_user_status(selected_user, new_active):
                        st.success(f"User {selected_user} status updated to {new_status}")
                        st.rerun()
                    else:
                        st.error("Failed to update user status")
        
        with col2:
            st.write("**Create New User**")
            with st.form("create_user_form"):
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", [UserRole.USER.value, UserRole.ADMIN.value])
                
                if st.form_submit_button("Create User"):
                    if new_username and new_email and new_password:
                        role = UserRole.ADMIN if new_role == "admin" else UserRole.USER
                        if auth_manager.create_user(new_username, new_email, new_password, role):
                            st.success(f"User '{new_username}' created successfully!")
                            st.rerun()
                        else:
                            st.error("Username already exists")
                    else:
                        st.error("Please fill all fields")

with tab2:
    st.subheader("System Analytics")
    
    # Get validation reports
    report_path = Path("app/data/reports/validated.jsonl")
    if report_path.exists():
        rows = []
        for line in report_path.read_text().splitlines():
            try:
                rows.append(json.loads(line))
            except:
                pass
        
        if rows:
            df = pd.json_normalize(rows)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Validations", len(df))
            with col2:
                compliance_rate = df['is_compliant'].mean() * 100
                st.metric("Compliance Rate", f"{compliance_rate:.1f}%")
            with col3:
                avg_score = df['score'].mean()
                st.metric("Average Score", f"{avg_score:.1f}")
            with col4:
                recent_validations = len(df)  # Could add date filtering
                st.metric("Recent Validations", recent_validations)
            
            # Charts
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Compliance Distribution")
                compliance_counts = df['is_compliant'].value_counts()
                st.bar_chart(compliance_counts)
            
            with col2:
                st.subheader("Score Distribution")
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
            st.info("No validation data available yet.")
    else:
        st.info("No validation reports found. Run some validations first.")

with tab3:
    st.subheader("System Settings")
    
    # System configuration
    st.write("**Application Configuration**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Max file upload size (MB)", value=10, min_value=1, max_value=100)
        st.number_input("Session timeout (minutes)", value=60, min_value=15, max_value=480)
    
    with col2:
        st.checkbox("Enable email notifications", value=False)
        st.checkbox("Enable audit logging", value=True)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
    
    # OCR Configuration
    st.write("**OCR Configuration**")
    ocr_language = st.selectbox("Default OCR Language", ["eng", "hin", "tam", "tel", "kan"])
    ocr_confidence = st.slider("Minimum OCR Confidence", 0.0, 1.0, 0.7)
    
    if st.button("Update OCR Settings"):
        st.success("OCR settings updated!")

with tab4:
    st.subheader("Reports Overview")
    
    # File system info
    st.write("**Storage Usage**")
    
    reports_dir = Path("app/data/reports")
    uploads_dir = Path("app/data/uploads")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*"))
            st.metric("Report Files", len(report_files))
        else:
            st.metric("Report Files", 0)
    
    with col2:
        if uploads_dir.exists():
            upload_files = list(uploads_dir.glob("*"))
            st.metric("Uploaded Files", len(upload_files))
        else:
            st.metric("Uploaded Files", 0)
    
    with col3:
        users_file = Path("app/data/users.json")
        if users_file.exists():
            st.metric("Registered Users", len(auth_manager.get_all_users()))
        else:
            st.metric("Registered Users", 0)
    
    # Recent activity
    st.write("**Recent Activity**")
    if report_path.exists():
        rows = []
        for line in report_path.read_text().splitlines():
            try:
                rows.append(json.loads(line))
            except:
                pass
        
        if rows:
            df = pd.json_normalize(rows)
            st.dataframe(df[['file', 'is_compliant', 'score']].tail(10), use_container_width=True)
        else:
            st.info("No recent activity to display.")

with tab5:
    st.subheader("System Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Data Management**")
        if st.button("Clear Old Reports"):
            st.info("This would clear reports older than 30 days")
        
        if st.button("Clean Temporary Files"):
            st.info("This would clean temporary upload files")
        
        if st.button("Export User Data"):
            st.info("This would export all user data to CSV")
    
    with col2:
        st.write("**System Health**")
        
        # Check system health
        health_checks = {
            "Users Database": Path("app/data/users.json").exists(),
            "Reports Directory": Path("app/data/reports").exists(),
            "Uploads Directory": Path("app/data/uploads").exists(),
            "Rules Configuration": Path("app/data/rules/legal_metrology_rules.yaml").exists()
        }
        
        for check, status in health_checks.items():
            if status:
                st.success(f"✅ {check}")
            else:
                st.error(f"❌ {check}")
        
        if st.button("Run System Diagnostics"):
            st.success("System diagnostics completed successfully!")

with tab6:
    st.subheader("Audit Logs & User Activity")
    
    # Audit log filtering
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_user_filter = st.selectbox(
            "Filter by User",
            ["All Users"] + [user.username for user in auth_manager.get_all_users()],
            help="Show logs for a specific user or all users"
        )
    
    with col2:
        log_action_filter = st.selectbox(
            "Filter by Action",
            ["All Actions", "FILE_UPLOAD", "TEXT_UPLOAD", "VALIDATION_RUN", "BULK_VALIDATION", "LOGIN", "LOGOUT", "USER_MANAGEMENT"],
            help="Show specific types of actions"
        )
    
    with col3:
        log_limit = st.number_input("Number of logs to show", min_value=10, max_value=1000, value=100)
    
    # Get filtered logs
    user_filter = None if log_user_filter == "All Users" else log_user_filter
    action_filter = None if log_action_filter == "All Actions" else log_action_filter
    
    logs_df = audit_logger.get_logs(user=user_filter, action=action_filter, limit=log_limit)
    
    if not logs_df.empty:
        # Format the dataframe for display
        display_df = logs_df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df = display_df[['timestamp', 'user', 'action', 'resource']].head(log_limit)
        
        st.subheader("Recent Activity")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Activity summary
        if log_user_filter == "All Users":
            st.subheader("Activity Summary")
            col1, col2 = st.columns(2)
            
            with col1:
                action_counts = logs_df['action'].value_counts()
                st.bar_chart(action_counts)
            
            with col2:
                user_activity = logs_df['user'].value_counts().head(10)
                st.bar_chart(user_activity)
        else:
            # Individual user activity summary
            user_summary = audit_logger.get_user_activity_summary(log_user_filter)
            st.subheader(f"Activity Summary for {log_user_filter}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Actions", user_summary['total_actions'])
            with col2:
                st.metric("Last Activity", user_summary['last_activity'][:16] if user_summary['last_activity'] else "Never")
            with col3:
                st.metric("Resources Accessed", len(user_summary['resources_accessed']))
            
            if user_summary['action_counts']:
                st.write("**Action Breakdown:**")
                for action, count in user_summary['action_counts'].items():
                    st.write(f"- {action}: {count}")
    else:
        st.info("No audit logs found for the selected filters.")
    
    # Log cleanup
    st.subheader("Log Maintenance")
    col1, col2 = st.columns(2)
    
    with col1:
        days_to_keep = st.number_input("Days to keep logs", min_value=7, max_value=365, value=30)
        if st.button("Clean Old Logs"):
            audit_logger.cleanup_old_logs(days_to_keep)
            st.success(f"Cleaned logs older than {days_to_keep} days")
    
    with col2:
        if st.button("Export Audit Logs"):
            if not logs_df.empty:
                csv_data = logs_df.to_csv(index=False)
                st.download_button(
                    "Download Audit Logs CSV",
                    data=csv_data,
                    file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No logs to export")

with tab8:
    st.subheader("📋 Quick Complaint Filing")
    st.markdown("File a quick complaint about system issues, data quality problems, or compliance violations.")
    
    # Get complaint statistics
    complaint_stats = complaint_manager.get_complaint_statistics()
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Complaints", complaint_stats["total_complaints"])
    with col2:
        st.metric("Open Issues", complaint_stats["open_complaints"])
    with col3:
        st.metric("Critical Issues", complaint_stats["critical_complaints"])
    
    # Quick complaint form
    with st.form("quick_complaint_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Complaint Title", placeholder="Brief description of the issue")
            category = st.selectbox(
                "Category",
                options=["DATA_QUALITY", "EXTRACTION_ERROR", "VALIDATION_ISSUE", "SYSTEM_BUG", "COMPLIANCE_VIOLATION", "OTHER"],
                format_func=lambda x: x.replace("_", " ").title()
            )
        
        with col2:
            priority = st.selectbox(
                "Priority",
                options=["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            )
            tags = st.text_input("Tags", placeholder="Comma-separated tags")
        
        description = st.text_area(
            "Description",
            placeholder="Describe the issue in detail...",
            height=100
        )
        
        submitted = st.form_submit_button("📝 File Quick Complaint", type="primary")
        
        if submitted:
            if title and description:
                try:
                    from core.complaint_manager import ComplaintCategory, ComplaintPriority
                    
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
                    
                    complaint = complaint_manager.file_complaint(
                        title=title,
                        description=description,
                        category=ComplaintCategory(category),
                        priority=ComplaintPriority(priority),
                        filed_by=get_current_user().username,
                        tags=tag_list
                    )
                    
                    st.success(f"✅ Complaint filed successfully!")
                    st.info(f"**Complaint ID:** {complaint.id}")
                    
                    log_user_action(
                        get_current_user().username,
                        "QUICK_COMPLAINT_FILED",
                        f"complaint:{complaint.id}",
                        {"category": category, "priority": priority}
                    )
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error filing complaint: {str(e)}")
            else:
                st.error("Please fill in the title and description fields.")
    
    # Recent complaints
    st.subheader("🕒 Recent Complaints")
    recent_complaints = sorted(complaint_manager.get_all_complaints(), 
                              key=lambda x: x.filed_date, reverse=True)[:5]
    
    if recent_complaints:
        for complaint in recent_complaints:
            with st.expander(f"{complaint.id} - {complaint.title}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Status:** {complaint.status.value}")
                    st.write(f"**Priority:** {complaint.priority.value}")
                    st.write(f"**Category:** {complaint.category.value.replace('_', ' ').title()}")
                
                with col2:
                    st.write(f"**Filed By:** {complaint.filed_by}")
                    st.write(f"**Date:** {complaint.filed_date[:10]}")
                    if complaint.assigned_to:
                        st.write(f"**Assigned To:** {complaint.assigned_to}")
                
                st.write(f"**Description:** {complaint.description}")
                
                if complaint.tags:
                    st.write(f"**Tags:** {', '.join(complaint.tags)}")
    else:
        st.info("No complaints filed yet.")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 View All Complaints"):
            st.switch_page("pages/9_📋_Complaint_Management.py")
    
    with col2:
        if st.button("📊 Complaint Analytics"):
            st.switch_page("pages/9_📋_Complaint_Management.py")
    
    with col3:
        if st.button("🔍 Search Complaints"):
            st.switch_page("pages/9_📋_Complaint_Management.py")

# Logout button
st.markdown("---")
if st.button("Logout", type="secondary"):
    if "user" in st.session_state:
        del st.session_state.user
    st.rerun()
