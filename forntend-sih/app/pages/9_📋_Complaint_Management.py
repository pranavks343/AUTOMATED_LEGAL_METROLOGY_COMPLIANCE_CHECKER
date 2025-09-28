import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from core.auth import require_admin, get_current_user
from core.complaint_manager import (
    complaint_manager, ComplaintStatus, ComplaintPriority, 
    ComplaintCategory, Complaint
)
from core.audit_logger import log_user_action
from core.json_utils import safe_json_dumps

st.set_page_config(page_title="Complaint Management - Legal Metrology Checker", page_icon="📋")

# Require admin access
require_admin()
current_user = get_current_user()

st.title("📋 Complaint Management System")
st.markdown(f"Welcome, {current_user.username}! Manage Legal Metrology compliance complaints and issues.")

# Create tabs for different complaint functions
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 File New Complaint", 
    "📊 Complaint Dashboard", 
    "🔍 View & Manage", 
    "📈 Analytics & Reports",
    "⚙️ System Settings"
])

with tab1:
    st.subheader("📝 File New Complaint")
    st.markdown("Report compliance issues, data quality problems, or system bugs.")
    
    with st.form("file_complaint_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Complaint Title *",
                placeholder="Brief description of the issue",
                help="Provide a clear, concise title for the complaint"
            )
            
            category = st.selectbox(
                "Category *",
                options=[cat.value for cat in ComplaintCategory],
                format_func=lambda x: x.replace("_", " ").title(),
                help="Select the most appropriate category for this complaint"
            )
            
            priority = st.selectbox(
                "Priority Level *",
                options=[pri.value for pri in ComplaintPriority],
                help="Select the priority level based on severity and impact"
            )
        
        with col2:
            # Get available files for reference
            uploads_dir = Path("app/data/uploads")
            uploaded_files = sorted(list(uploads_dir.glob("*.txt"))) if uploads_dir.exists() else []
            
            related_files = st.multiselect(
                "Related Files (Optional)",
                options=[f.name for f in uploaded_files],
                help="Select files related to this complaint"
            )
            
            tags = st.text_input(
                "Tags (Optional)",
                placeholder="Enter tags separated by commas",
                help="Add relevant tags for better categorization and search"
            )
        
        description = st.text_area(
            "Detailed Description *",
            placeholder="Provide a detailed description of the issue, including:\n• What happened\n• When it occurred\n• Impact on compliance\n• Steps to reproduce (if applicable)",
            height=150,
            help="Be as detailed as possible to help with investigation and resolution"
        )
        
        # Evidence upload
        st.markdown("**📎 Evidence Files (Optional)**")
        evidence_files = st.file_uploader(
            "Upload supporting documents, screenshots, or other evidence",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'pdf', 'txt', 'doc', 'docx'],
            help="Upload any files that support your complaint"
        )
        
        submitted = st.form_submit_button("📝 File Complaint", type="primary")
        
        if submitted:
            if not title or not description:
                st.error("Please fill in the title and description fields.")
            else:
                try:
                    # Process tags
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
                    
                    # Process evidence files
                    evidence_file_names = []
                    if evidence_files:
                        evidence_dir = Path("app/data/evidence")
                        evidence_dir.mkdir(parents=True, exist_ok=True)
                        
                        for file in evidence_files:
                            file_path = evidence_dir / file.name
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())
                            evidence_file_names.append(str(file_path))
                    
                    # File the complaint
                    complaint = complaint_manager.file_complaint(
                        title=title,
                        description=description,
                        category=ComplaintCategory(category),
                        priority=ComplaintPriority(priority),
                        filed_by=current_user.username,
                        related_files=related_files,
                        evidence_files=evidence_file_names,
                        tags=tag_list
                    )
                    
                    st.success(f"✅ Complaint filed successfully!")
                    st.info(f"**Complaint ID:** {complaint.id}")
                    st.info(f"**Status:** {complaint.status.value}")
                    st.info(f"**Priority:** {complaint.priority.value}")
                    
                    # Log the action
                    log_user_action(
                        current_user.username,
                        "COMPLAINT_FILED",
                        f"complaint:{complaint.id}",
                        {
                            "category": category,
                            "priority": priority,
                            "title": title
                        }
                    )
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error filing complaint: {str(e)}")

with tab2:
    st.subheader("📊 Complaint Dashboard")
    
    # Get complaint statistics
    stats = complaint_manager.get_complaint_statistics()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Complaints", stats["total_complaints"])
    
    with col2:
        st.metric("Open Complaints", stats["open_complaints"])
    
    with col3:
        st.metric("Critical Issues", stats["critical_complaints"])
    
    with col4:
        avg_time = stats["avg_resolution_time_hours"]
        if avg_time > 24:
            avg_time_str = f"{avg_time/24:.1f} days"
        else:
            avg_time_str = f"{avg_time:.1f} hours"
        st.metric("Avg Resolution Time", avg_time_str)
    
    # Status distribution
    st.subheader("📈 Status Distribution")
    if stats["by_status"]:
        status_df = pd.DataFrame(list(stats["by_status"].items()), columns=["Status", "Count"])
        st.bar_chart(status_df.set_index("Status"))
    else:
        st.info("No complaints filed yet.")
    
    # Priority distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Priority Distribution")
        if stats["by_priority"]:
            priority_df = pd.DataFrame(list(stats["by_priority"].items()), columns=["Priority", "Count"])
            st.bar_chart(priority_df.set_index("Priority"))
        else:
            st.info("No complaints filed yet.")
    
    with col2:
        st.subheader("📂 Category Distribution")
        if stats["by_category"]:
            category_df = pd.DataFrame(list(stats["by_category"].items()), columns=["Category", "Count"])
            st.bar_chart(category_df.set_index("Category"))
        else:
            st.info("No complaints filed yet.")
    
    # Recent complaints
    st.subheader("🕒 Recent Complaints")
    recent_complaints = sorted(complaint_manager.get_all_complaints(), 
                              key=lambda x: x.filed_date, reverse=True)[:10]
    
    if recent_complaints:
        complaint_data = []
        for complaint in recent_complaints:
            complaint_data.append({
                "ID": complaint.id,
                "Title": complaint.title,
                "Category": complaint.category.value.replace("_", " ").title(),
                "Priority": complaint.priority.value,
                "Status": complaint.status.value.replace("_", " ").title(),
                "Filed By": complaint.filed_by,
                "Filed Date": complaint.filed_date[:10]
            })
        
        df = pd.DataFrame(complaint_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No complaints filed yet.")

with tab3:
    st.subheader("🔍 View & Manage Complaints")
    
    # Search and filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("🔍 Search Complaints", placeholder="Search by title, description, or tags")
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All"] + [status.value for status in ComplaintStatus],
            format_func=lambda x: x.replace("_", " ").title()
        )
    
    with col3:
        priority_filter = st.selectbox(
            "Filter by Priority",
            options=["All"] + [priority.value for priority in ComplaintPriority]
        )
    
    # Get filtered complaints
    all_complaints = complaint_manager.get_all_complaints()
    
    if search_query:
        all_complaints = complaint_manager.search_complaints(search_query)
    
    if status_filter != "All":
        all_complaints = [c for c in all_complaints if c.status.value == status_filter]
    
    if priority_filter != "All":
        all_complaints = [c for c in all_complaints if c.priority.value == priority_filter]
    
    # Display complaints
    if all_complaints:
        st.markdown(f"**Found {len(all_complaints)} complaint(s)**")
        
        for complaint in all_complaints:
            with st.expander(f"{complaint.id} - {complaint.title}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {complaint.description}")
                    st.markdown(f"**Category:** {complaint.category.value.replace('_', ' ').title()}")
                    st.markdown(f"**Priority:** {complaint.priority.value}")
                    st.markdown(f"**Status:** {complaint.status.value.replace('_', ' ').title()}")
                    st.markdown(f"**Filed By:** {complaint.filed_by}")
                    st.markdown(f"**Filed Date:** {complaint.filed_date}")
                    
                    if complaint.assigned_to:
                        st.markdown(f"**Assigned To:** {complaint.assigned_to}")
                    
                    if complaint.resolution:
                        st.markdown(f"**Resolution:** {complaint.resolution}")
                        st.markdown(f"**Resolved Date:** {complaint.resolution_date}")
                    
                    if complaint.related_files:
                        st.markdown(f"**Related Files:** {', '.join(complaint.related_files)}")
                    
                    if complaint.tags:
                        st.markdown(f"**Tags:** {', '.join(complaint.tags)}")
                
                with col2:
                    # Status update
                    st.markdown("**Update Status:**")
                    new_status = st.selectbox(
                        "Status",
                        options=[status.value for status in ComplaintStatus],
                        index=list(ComplaintStatus).index(complaint.status),
                        key=f"status_{complaint.id}"
                    )
                    
                    if st.button("Update Status", key=f"update_status_{complaint.id}"):
                        if complaint_manager.update_complaint_status(
                            complaint.id, 
                            ComplaintStatus(new_status), 
                            current_user.username
                        ):
                            st.success("Status updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update status.")
                    
                    # Add note
                    st.markdown("**Add Note:**")
                    note = st.text_area(
                        "Note",
                        placeholder="Add a note or comment...",
                        key=f"note_{complaint.id}",
                        height=100
                    )
                    
                    if st.button("Add Note", key=f"add_note_{complaint.id}"):
                        if note.strip():
                            if complaint_manager.add_complaint_note(
                                complaint.id, 
                                note.strip(), 
                                current_user.username
                            ):
                                st.success("Note added successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to add note.")
                        else:
                            st.warning("Please enter a note.")
                    
                    # Quick actions
                    if complaint.status == ComplaintStatus.OPEN:
                        if st.button("Assign to Me", key=f"assign_{complaint.id}"):
                            if complaint_manager.assign_complaint(
                                complaint.id, 
                                current_user.username, 
                                current_user.username
                            ):
                                st.success("Complaint assigned to you!")
                                st.rerun()
                    
                    # Resolve complaint
                    if complaint.status != ComplaintStatus.RESOLVED:
                        resolution = st.text_area(
                            "Resolution",
                            placeholder="Describe how the complaint was resolved...",
                            key=f"resolution_{complaint.id}",
                            height=100
                        )
                        
                        if st.button("Mark as Resolved", key=f"resolve_{complaint.id}"):
                            if resolution.strip():
                                if complaint_manager.resolve_complaint(
                                    complaint.id, 
                                    resolution.strip(), 
                                    current_user.username
                                ):
                                    st.success("Complaint resolved successfully!")
                                    st.rerun()
                            else:
                                st.warning("Please provide a resolution description.")
                
                # Display notes
                if complaint.notes:
                    st.markdown("**📝 Notes & History:**")
                    for note in complaint.notes[-5:]:  # Show last 5 notes
                        st.caption(f"**{note['user']}** - {note['timestamp'][:16]} - {note['note']}")
    else:
        st.info("No complaints found matching the criteria.")

with tab4:
    st.subheader("📈 Analytics & Reports")
    
    # Export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Complaint Summary"):
            summary_data = {
                "export_timestamp": datetime.now().isoformat(),
                "exported_by": current_user.username,
                "statistics": stats,
                "total_complaints": len(complaint_manager.get_all_complaints())
            }
            
            st.download_button(
                label="Download Summary Report",
                data=safe_json_dumps(summary_data, indent=2),
                file_name=f"complaint_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📋 Export All Complaints"):
            complaints_data = []
            for complaint in complaint_manager.get_all_complaints():
                complaint_dict = {
                    "id": complaint.id,
                    "title": complaint.title,
                    "description": complaint.description,
                    "category": complaint.category.value,
                    "priority": complaint.priority.value,
                    "status": complaint.status.value,
                    "filed_by": complaint.filed_by,
                    "filed_date": complaint.filed_date,
                    "assigned_to": complaint.assigned_to,
                    "resolution": complaint.resolution,
                    "resolution_date": complaint.resolution_date,
                    "related_files": complaint.related_files,
                    "evidence_files": complaint.evidence_files,
                    "tags": complaint.tags,
                    "notes": complaint.notes
                }
                complaints_data.append(complaint_dict)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "exported_by": current_user.username,
                "complaints": complaints_data
            }
            
            st.download_button(
                label="Download All Complaints",
                data=safe_json_dumps(export_data, indent=2),
                file_name=f"all_complaints_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📈 Generate Analytics Report"):
            # Generate detailed analytics
            analytics_data = {
                "report_generated": datetime.now().isoformat(),
                "generated_by": current_user.username,
                "complaint_statistics": stats,
                "trends": {
                    "complaints_last_30_days": len([
                        c for c in complaint_manager.get_all_complaints()
                        if datetime.fromisoformat(c.filed_date) > datetime.now() - timedelta(days=30)
                    ]),
                    "complaints_last_7_days": len([
                        c for c in complaint_manager.get_all_complaints()
                        if datetime.fromisoformat(c.filed_date) > datetime.now() - timedelta(days=7)
                    ])
                },
                "top_categories": dict(sorted(stats["by_category"].items(), key=lambda x: x[1], reverse=True)[:3]),
                "resolution_efficiency": {
                    "avg_resolution_time_hours": stats["avg_resolution_time_hours"],
                    "resolved_complaints": stats["by_status"].get("RESOLVED", 0),
                    "closed_complaints": stats["by_status"].get("CLOSED", 0)
                }
            }
            
            st.download_button(
                label="Download Analytics Report",
                data=safe_json_dumps(analytics_data, indent=2),
                file_name=f"complaint_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Trend analysis
    st.subheader("📊 Trend Analysis")
    
    # Last 30 days complaints
    recent_complaints = [
        c for c in complaint_manager.get_all_complaints()
        if datetime.fromisoformat(c.filed_date) > datetime.now() - timedelta(days=30)
    ]
    
    if recent_complaints:
        # Group by date
        date_counts = {}
        for complaint in recent_complaints:
            date = complaint.filed_date[:10]
            date_counts[date] = date_counts.get(date, 0) + 1
        
        if date_counts:
            trend_df = pd.DataFrame(list(date_counts.items()), columns=["Date", "Complaints"])
            trend_df = trend_df.sort_values("Date")
            st.line_chart(trend_df.set_index("Date"))
        else:
            st.info("No complaints in the last 30 days.")
    else:
        st.info("No complaints in the last 30 days.")

with tab5:
    st.subheader("⚙️ System Settings")
    
    st.markdown("**Complaint Management Configuration**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 Available Categories:**")
        for category in ComplaintCategory:
            st.write(f"• {category.value.replace('_', ' ').title()}")
        
        st.markdown("**🎯 Priority Levels:**")
        for priority in ComplaintPriority:
            st.write(f"• {priority.value}")
    
    with col2:
        st.markdown("**📊 Status Types:**")
        for status in ComplaintStatus:
            st.write(f"• {status.value.replace('_', ' ').title()}")
        
        st.markdown("**📁 Data Storage:**")
        st.info(f"Complaints stored in: `{complaint_manager.complaints_file}`")
        
        if complaint_manager.complaints_file.exists():
            file_size = complaint_manager.complaints_file.stat().st_size
            st.info(f"File size: {file_size} bytes")
    
    # System maintenance
    st.markdown("**🔧 System Maintenance**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            complaint_manager.complaints = complaint_manager._load_complaints()
            st.success("Data refreshed successfully!")
            st.rerun()
    
    with col2:
        if st.button("📊 Update Statistics"):
            st.success("Statistics updated!")
            st.rerun()
    
    # Data cleanup
    st.markdown("**🧹 Data Cleanup**")
    
    if st.button("🗑️ Archive Resolved Complaints (Demo)"):
        resolved_count = len(complaint_manager.get_complaints_by_status(ComplaintStatus.RESOLVED))
        if resolved_count > 0:
            st.warning(f"This would archive {resolved_count} resolved complaints. (Demo mode - no actual archiving)")
        else:
            st.info("No resolved complaints to archive.")

# Log page access
log_user_action(
    current_user.username,
    "PAGE_ACCESS",
    "complaint_management",
    {"page": "Complaint Management"}
)
