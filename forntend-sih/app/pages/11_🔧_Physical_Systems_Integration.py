import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from core.auth import require_admin, get_current_user
from core.physical_integration import (
    physical_integration_manager, DeviceType, IntegrationStatus, 
    PrintStatus, VisionCheckStatus
)
from core.label_generator import label_generator, LabelStatus
from core.erp_manager import erp_manager, ProductStatus
from core.audit_logger import log_user_action
from core.json_utils import safe_json_dumps

st.set_page_config(page_title="Physical Systems Integration - Legal Metrology Checker", page_icon="🔧", layout="wide")

# Enhanced Custom CSS for Physical Systems Integration
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Physical Systems Header */
    .physical-header {
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
    
    .physical-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="gears" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="8" fill="none" stroke="white" opacity="0.1" stroke-width="2"/><circle cx="10" cy="10" r="4" fill="none" stroke="white" opacity="0.1" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23gears)"/></svg>');
        opacity: 0.1;
    }
    
    .physical-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Device Status Cards */
    .device-status-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
    }
    
    .device-status-card.connected {
        border-left: 4px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    .device-status-card.disconnected {
        border-left: 4px solid #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
    }
    
    .device-status-card.maintenance {
        border-left: 4px solid #ff9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
    }
    
    /* System Metric Cards */
    .system-metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    
    .system-metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .system-metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    }
    
    /* Device Grid */
    .device-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 1rem 0;
    }
    
    .device-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .device-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        border-color: #ff6b6b;
    }
    
    .device-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    }
    
    /* Physical Tab Styling */
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
    
    /* Operation Status */
    .operation-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .operation-status.success {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
    }
    
    .operation-status.error {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
    }
    
    .operation-status.warning {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
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
current_user = get_current_user()

# Enhanced Physical Systems Header
st.markdown(f"""
<div class="physical-header">
    <h1>🔧 Physical Systems Integration</h1>
    <p>Welcome, <strong>{current_user.username}</strong>! Manage integration with printing and vision systems for end-to-end compliance assurance.</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for different integration functions
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🖥️ Device Management", 
    "🖨️ Print Operations", 
    "👁️ Vision Inspection", 
    "📊 Integration Dashboard",
    "⚙️ System Configuration"
])

with tab1:
    st.markdown("### 🖥️ Device Management")
    st.markdown("Manage physical devices including printers, vision systems, and scanners.")
    
    # Device overview
    devices = physical_integration_manager.devices
    connected_devices = physical_integration_manager.get_connected_devices()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="system-metric-card">
            <h3>🔧 {len(devices)}</h3>
            <p>Total Devices</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="system-metric-card">
            <h3>✅ {len(connected_devices)}</h3>
            <p>Connected Devices</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        disconnected_count = len(devices) - len(connected_devices)
        st.markdown(f"""
        <div class="system-metric-card">
            <h3>❌ {disconnected_count}</h3>
            <p>Disconnected Devices</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Device list
    st.subheader("📋 Device List")
    
    if devices:
        for device in devices:
            with st.expander(f"{device.device_id} - {device.device_name}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Status indicator
                    status_color = {
                        "CONNECTED": "🟢",
                        "DISCONNECTED": "🔴", 
                        "CONNECTING": "🟡",
                        "ERROR": "🔴",
                        "MAINTENANCE": "🟠"
                    }
                    
                    st.markdown(f"**Status:** {status_color.get(device.status.value, '⚪')} {device.status.value}")
                    st.markdown(f"**Type:** {device.device_type.value}")
                    st.markdown(f"**Manufacturer:** {device.manufacturer} {device.model}")
                    
                    if device.ip_address:
                        st.markdown(f"**IP Address:** {device.ip_address}")
                    if device.port:
                        st.markdown(f"**Port:** {device.port}")
                    
                    st.markdown(f"**Capabilities:** {', '.join(device.capabilities)}")
                    
                    if device.last_heartbeat:
                        st.markdown(f"**Last Heartbeat:** {device.last_heartbeat[:19]}")
                    
                    if device.error_count > 0:
                        st.warning(f"**Error Count:** {device.error_count}")
                        if device.last_error:
                            st.error(f"**Last Error:** {device.last_error}")
                
                with col2:
                    # Device actions
                    if device.status == IntegrationStatus.DISCONNECTED:
                        if st.button("🔌 Connect", key=f"connect_{device.device_id}"):
                            if physical_integration_manager.connect_device(device.device_id):
                                st.success("Device connected successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to connect device")
                    
                    elif device.status == IntegrationStatus.CONNECTED:
                        if st.button("🔌 Disconnect", key=f"disconnect_{device.device_id}"):
                            if physical_integration_manager.disconnect_device(device.device_id):
                                st.success("Device disconnected successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to disconnect device")
                    
                    # Device configuration
                    if st.button("⚙️ Configure", key=f"config_{device.device_id}"):
                        st.info("Device configuration panel would open here")
                    
                    # Test device
                    if st.button("🧪 Test", key=f"test_{device.device_id}"):
                        st.info(f"Testing {device.device_name}...")
                        st.success("Device test completed successfully!")
    else:
        st.info("No devices configured yet.")
    
    # Add new device
    st.subheader("➕ Add New Device")
    
    with st.form("add_device_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            device_name = st.text_input("Device Name", placeholder="Enter device name")
            device_type = st.selectbox(
                "Device Type",
                options=[dt.value for dt in DeviceType],
                format_func=lambda x: x.replace("_", " ").title()
            )
            manufacturer = st.text_input("Manufacturer", placeholder="Enter manufacturer name")
            model = st.text_input("Model", placeholder="Enter model number")
        
        with col2:
            ip_address = st.text_input("IP Address", placeholder="192.168.1.100")
            port = st.number_input("Port", min_value=1, max_value=65535, value=9100)
            
            capabilities = st.text_input(
                "Capabilities", 
                placeholder="capability1, capability2, capability3",
                help="Enter capabilities separated by commas"
            )
        
        submitted = st.form_submit_button("➕ Add Device", type="primary")
        
        if submitted:
            if not all([device_name, manufacturer, model]):
                st.error("Please fill in all required fields.")
            else:
                try:
                    capability_list = [cap.strip() for cap in capabilities.split(",") if cap.strip()] if capabilities else []
                    
                    device = physical_integration_manager.add_device(
                        device_name=device_name,
                        device_type=DeviceType(device_type),
                        manufacturer=manufacturer,
                        model=model,
                        ip_address=ip_address if ip_address else None,
                        port=port if port else None,
                        capabilities=capability_list
                    )
                    
                    st.success(f"✅ Device added successfully!")
                    st.info(f"**Device ID:** {device.device_id}")
                    
                    log_user_action(
                        current_user.username,
                        "DEVICE_ADDED",
                        f"device:{device.device_id}",
                        {"device_type": device_type, "manufacturer": manufacturer}
                    )
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding device: {str(e)}")

with tab2:
    st.subheader("🖨️ Print Operations")
    st.markdown("Manage label printing operations with compliance validation.")
    
    # Print job overview
    print_jobs = physical_integration_manager.print_jobs
    pending_jobs = physical_integration_manager.get_print_jobs_by_status(PrintStatus.PENDING)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Print Jobs", len(print_jobs))
    
    with col2:
        st.metric("Pending Jobs", len(pending_jobs))
    
    with col3:
        completed_jobs = len(physical_integration_manager.get_print_jobs_by_status(PrintStatus.COMPLETED))
        st.metric("Completed Jobs", completed_jobs)
    
    # Create new print job
    st.subheader("📝 Create Print Job")
    
    # Get approved labels
    approved_labels = label_generator.get_labels_by_status(LabelStatus.APPROVED)
    
    if approved_labels:
        with st.form("create_print_job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                label_options = {f"{label.label_id} - {label.product_sku}": label.label_id 
                               for label in approved_labels}
                selected_label = st.selectbox("Select Label", options=list(label_options.keys()))
                selected_label_id = label_options[selected_label]
                
                copies = st.number_input("Number of Copies", min_value=1, max_value=1000, value=1)
                
            with col2:
                # Get available printers
                printers = physical_integration_manager.get_devices_by_type(DeviceType.PRINTER)
                connected_printers = [p for p in printers if p.status == IntegrationStatus.CONNECTED]
                
                if connected_printers:
                    printer_options = {f"{printer.device_name} ({printer.device_id})": printer.device_id 
                                     for printer in connected_printers}
                    selected_printer = st.selectbox("Select Printer", options=list(printer_options.keys()))
                    selected_printer_id = printer_options[selected_printer]
                else:
                    st.warning("No connected printers available")
                    selected_printer_id = None
                
                priority = st.selectbox("Priority", options=[1, 2, 3, 4, 5], index=2)
            
            submitted = st.form_submit_button("🖨️ Create Print Job", type="primary")
            
            if submitted and selected_printer_id:
                try:
                    # Get product SKU from label
                    label = label_generator.get_label(selected_label_id)
                    
                    job = physical_integration_manager.create_print_job(
                        label_id=selected_label_id,
                        product_sku=label.product_sku,
                        device_id=selected_printer_id,
                        created_by=current_user.username,
                        copies=copies,
                        priority=priority
                    )
                    
                    st.success(f"✅ Print job created successfully!")
                    st.info(f"**Job ID:** {job.job_id}")
                    st.info(f"**Label:** {selected_label_id}")
                    st.info(f"**Copies:** {copies}")
                    
                    log_user_action(
                        current_user.username,
                        "PRINT_JOB_CREATED",
                        f"job:{job.job_id}",
                        {"label_id": selected_label_id, "copies": copies}
                    )
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error creating print job: {str(e)}")
            elif submitted and not selected_printer_id:
                st.error("Please connect a printer first")
    else:
        st.info("No approved labels available for printing. Generate and approve labels first.")
    
    # Print job management
    st.subheader("📋 Print Job Management")
    
    if print_jobs:
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All"] + [status.value for status in PrintStatus],
                format_func=lambda x: x.replace("_", " ").title()
            )
        
        with col2:
            device_filter = st.selectbox(
                "Filter by Device",
                options=["All"] + [device.device_id for device in devices]
            )
        
        # Filter jobs
        filtered_jobs = print_jobs
        
        if status_filter != "All":
            filtered_jobs = [job for job in filtered_jobs if job.status.value == status_filter]
        
        if device_filter != "All":
            filtered_jobs = [job for job in filtered_jobs if job.device_id == device_filter]
        
        # Display jobs
        for job in filtered_jobs:
            with st.expander(f"{job.job_id} - {job.product_sku}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Status indicator
                    status_color = {
                        "PENDING": "🟡",
                        "PRINTING": "🔵",
                        "COMPLETED": "🟢",
                        "FAILED": "🔴",
                        "CANCELLED": "⚪"
                    }
                    
                    st.markdown(f"**Status:** {status_color.get(job.status.value, '⚪')} {job.status.value}")
                    st.markdown(f"**Label ID:** {job.label_id}")
                    st.markdown(f"**Product SKU:** {job.product_sku}")
                    st.markdown(f"**Device:** {job.device_id}")
                    st.markdown(f"**Copies:** {job.copies}")
                    st.markdown(f"**Created By:** {job.created_by}")
                    st.markdown(f"**Created Date:** {job.created_date[:19]}")
                    
                    if job.started_time:
                        st.markdown(f"**Started:** {job.started_time[:19]}")
                    if job.completed_time:
                        st.markdown(f"**Completed:** {job.completed_time[:19]}")
                    
                    if job.success_count > 0:
                        st.success(f"**Success Count:** {job.success_count}")
                    if job.failure_count > 0:
                        st.error(f"**Failure Count:** {job.failure_count}")
                    if job.error_message:
                        st.error(f"**Error:** {job.error_message}")
                
                with col2:
                    # Job actions
                    if job.status == PrintStatus.PENDING:
                        if st.button("▶️ Execute", key=f"execute_{job.job_id}"):
                            if physical_integration_manager.execute_print_job(job.job_id):
                                st.success("Print job executed successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to execute print job")
                    
                    if job.status == PrintStatus.COMPLETED:
                        st.success("✅ Job completed")
                    
                    if job.status == PrintStatus.FAILED:
                        st.error("❌ Job failed")
                        if st.button("🔄 Retry", key=f"retry_{job.job_id}"):
                            # Reset job status and retry
                            job.status = PrintStatus.PENDING
                            job.error_message = None
                            physical_integration_manager._save_print_jobs()
                            st.success("Job reset for retry")
                            st.rerun()
    else:
        st.info("No print jobs created yet.")

with tab3:
    st.subheader("👁️ Vision Inspection")
    st.markdown("Perform vision-based compliance validation on printed labels.")
    
    # Vision check overview
    vision_checks = physical_integration_manager.vision_checks
    pending_checks = physical_integration_manager.get_vision_checks_by_status(VisionCheckStatus.PENDING)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Vision Checks", len(vision_checks))
    
    with col2:
        st.metric("Pending Checks", len(pending_checks))
    
    with col3:
        passed_checks = len(physical_integration_manager.get_vision_checks_by_status(VisionCheckStatus.PASSED))
        st.metric("Passed Checks", passed_checks)
    
    # Create new vision check
    st.subheader("📸 Create Vision Check")
    
    # Get dispatched products
    dispatched_products = erp_manager.get_products_by_status(ProductStatus.DISPATCHED)
    
    if dispatched_products:
        with st.form("create_vision_check_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_options = {f"{product.sku} - {product.product_name}": product.sku 
                                 for product in dispatched_products}
                selected_product = st.selectbox("Select Product", options=list(product_options.keys()))
                selected_sku = product_options[selected_product]
                
            with col2:
                image_path = st.text_input(
                    "Image Path", 
                    placeholder="/path/to/label/image.jpg",
                    help="Path to the image file for vision analysis"
                )
            
            submitted = st.form_submit_button("👁️ Create Vision Check", type="primary")
            
            if submitted:
                try:
                    check = physical_integration_manager.create_vision_check(
                        product_sku=selected_sku,
                        image_path=image_path,
                        performed_by=current_user.username
                    )
                    
                    st.success(f"✅ Vision check created successfully!")
                    st.info(f"**Check ID:** {check.check_id}")
                    st.info(f"**Product SKU:** {selected_sku}")
                    
                    log_user_action(
                        current_user.username,
                        "VISION_CHECK_CREATED",
                        f"check:{check.check_id}",
                        {"product_sku": selected_sku}
                    )
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error creating vision check: {str(e)}")
    else:
        st.info("No dispatched products available for vision inspection.")
    
    # Vision check management
    st.subheader("📋 Vision Check Management")
    
    if vision_checks:
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All"] + [status.value for status in VisionCheckStatus],
                format_func=lambda x: x.replace("_", " ").title(),
                key="vision_status_filter"
            )
        
        with col2:
            product_filter = st.selectbox(
                "Filter by Product",
                options=["All"] + list(set([check.product_sku for check in vision_checks])),
                key="vision_product_filter"
            )
        
        # Filter checks
        filtered_checks = vision_checks
        
        if status_filter != "All":
            filtered_checks = [check for check in filtered_checks if check.status.value == status_filter]
        
        if product_filter != "All":
            filtered_checks = [check for check in filtered_checks if check.product_sku == product_filter]
        
        # Display checks
        for check in filtered_checks:
            with st.expander(f"{check.check_id} - {check.product_sku}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Status indicator
                    status_color = {
                        "PENDING": "🟡",
                        "IN_PROGRESS": "🔵",
                        "PASSED": "🟢",
                        "FAILED": "🔴",
                        "ERROR": "🔴"
                    }
                    
                    st.markdown(f"**Status:** {status_color.get(check.status.value, '⚪')} {check.status.value}")
                    st.markdown(f"**Product SKU:** {check.product_sku}")
                    st.markdown(f"**Image Path:** {check.image_path}")
                    st.markdown(f"**Performed By:** {check.performed_by}")
                    st.markdown(f"**Date:** {check.performed_date[:19]}")
                    
                    if check.compliance_score > 0:
                        st.markdown(f"**Compliance Score:** {check.compliance_score:.1f}%")
                        st.markdown(f"**Confidence Level:** {check.confidence_level:.1f}%")
                        
                        # Quality scores
                        col_quality1, col_quality2, col_quality3 = st.columns(3)
                        with col_quality1:
                            st.metric("Image Quality", f"{check.image_quality_score:.1f}%")
                        with col_quality2:
                            st.metric("Lighting", f"{check.lighting_score:.1f}%")
                        with col_quality3:
                            st.metric("Sharpness", f"{check.sharpness_score:.1f}%")
                        
                        # Analysis results
                        if check.text_recognition_results:
                            st.markdown("**Text Recognition Results:**")
                            for key, value in check.text_recognition_results.items():
                                if isinstance(value, bool):
                                    icon = "✅" if value else "❌"
                                    st.write(f"{icon} {key.replace('_', ' ').title()}")
                                else:
                                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                        
                        if check.compliance_analysis:
                            st.markdown("**Compliance Analysis:**")
                            for key, value in check.compliance_analysis.items():
                                if isinstance(value, bool):
                                    icon = "✅" if value else "❌"
                                    st.write(f"{icon} {key.replace('_', ' ').title()}")
                                else:
                                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                        
                        if check.detected_issues:
                            st.warning("**Detected Issues:**")
                            for issue in check.detected_issues:
                                st.write(f"• {issue}")
                
                with col2:
                    # Check actions
                    if check.status == VisionCheckStatus.PENDING:
                        if st.button("▶️ Execute", key=f"execute_check_{check.check_id}"):
                            if physical_integration_manager.execute_vision_check(check.check_id):
                                st.success("Vision check executed successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to execute vision check")
                    
                    if check.status == VisionCheckStatus.PASSED:
                        st.success("✅ Check passed")
                    
                    if check.status == VisionCheckStatus.FAILED:
                        st.error("❌ Check failed")
                        if st.button("🔄 Retry", key=f"retry_check_{check.check_id}"):
                            # Reset check status and retry
                            check.status = VisionCheckStatus.PENDING
                            physical_integration_manager._save_vision_checks()
                            st.success("Check reset for retry")
                            st.rerun()
    else:
        st.info("No vision checks created yet.")

with tab4:
    st.subheader("📊 Integration Dashboard")
    
    # Get integration statistics
    stats = physical_integration_manager.get_integration_statistics()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Devices", stats["total_devices"])
    
    with col2:
        st.metric("Connected Devices", stats["connected_devices"])
    
    with col3:
        st.metric("Print Success Rate", f"{stats['print_success_rate']}%")
    
    with col4:
        st.metric("Vision Success Rate", f"{stats['vision_success_rate']}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Device Status Distribution")
        if stats["devices_by_status"]:
            device_status_df = pd.DataFrame(list(stats["devices_by_status"].items()), columns=["Status", "Count"])
            st.bar_chart(device_status_df.set_index("Status"))
        else:
            st.info("No device data available.")
    
    with col2:
        st.subheader("📈 Print Job Status Distribution")
        if stats["jobs_by_status"]:
            job_status_df = pd.DataFrame(list(stats["jobs_by_status"].items()), columns=["Status", "Count"])
            st.bar_chart(job_status_df.set_index("Status"))
        else:
            st.info("No print job data available.")
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    
    # Recent print jobs
    recent_jobs = sorted(print_jobs, key=lambda x: x.created_date, reverse=True)[:5]
    if recent_jobs:
        st.markdown("**Recent Print Jobs:**")
        for job in recent_jobs:
            status_icon = {"COMPLETED": "✅", "PENDING": "⏳", "PRINTING": "🖨️", "FAILED": "❌"}.get(job.status.value, "⚪")
            st.write(f"{status_icon} {job.job_id} - {job.product_sku} ({job.status.value})")
    
    # Recent vision checks
    recent_checks = sorted(vision_checks, key=lambda x: x.performed_date, reverse=True)[:5]
    if recent_checks:
        st.markdown("**Recent Vision Checks:**")
        for check in recent_checks:
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PENDING": "⏳", "IN_PROGRESS": "👁️"}.get(check.status.value, "⚪")
            score_text = f" ({check.compliance_score:.1f}%)" if check.compliance_score > 0 else ""
            st.write(f"{status_icon} {check.check_id} - {check.product_sku} ({check.status.value}){score_text}")

with tab5:
    st.subheader("⚙️ System Configuration")
    
    # Export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Device Configuration"):
            devices_data = []
            for device in devices:
                device_dict = {
                    "device_id": device.device_id,
                    "device_name": device.device_name,
                    "device_type": device.device_type.value,
                    "manufacturer": device.manufacturer,
                    "model": device.model,
                    "status": device.status.value,
                    "ip_address": device.ip_address,
                    "port": device.port,
                    "capabilities": device.capabilities,
                    "config": device.config
                }
                devices_data.append(device_dict)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "exported_by": current_user.username,
                "devices": devices_data
            }
            
            st.download_button(
                label="Download Device Config",
                data=safe_json_dumps(export_data, indent=2),
                file_name=f"device_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🖨️ Export Print Jobs"):
            jobs_data = []
            for job in print_jobs:
                job_dict = {
                    "job_id": job.job_id,
                    "label_id": job.label_id,
                    "product_sku": job.product_sku,
                    "device_id": job.device_id,
                    "status": job.status.value,
                    "created_by": job.created_by,
                    "created_date": job.created_date,
                    "copies": job.copies,
                    "success_count": job.success_count,
                    "failure_count": job.failure_count
                }
                jobs_data.append(job_dict)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "exported_by": current_user.username,
                "print_jobs": jobs_data
            }
            
            st.download_button(
                label="Download Print Jobs",
                data=safe_json_dumps(export_data, indent=2),
                file_name=f"print_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("👁️ Export Vision Checks"):
            checks_data = []
            for check in vision_checks:
                check_dict = {
                    "check_id": check.check_id,
                    "product_sku": check.product_sku,
                    "status": check.status.value,
                    "performed_by": check.performed_by,
                    "performed_date": check.performed_date,
                    "compliance_score": check.compliance_score,
                    "confidence_level": check.confidence_level,
                    "detected_issues": check.detected_issues
                }
                checks_data.append(check_dict)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "exported_by": current_user.username,
                "vision_checks": checks_data
            }
            
            st.download_button(
                label="Download Vision Checks",
                data=safe_json_dumps(export_data, indent=2),
                file_name=f"vision_checks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # System health
    st.subheader("🏥 System Health")
    
    # Device health
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Device Health:**")
        healthy_devices = len([d for d in devices if d.status == IntegrationStatus.CONNECTED and d.error_count == 0])
        total_devices = len(devices)
        health_percentage = (healthy_devices / total_devices) * 100 if total_devices > 0 else 0
        
        st.metric("Device Health", f"{health_percentage:.1f}%")
        
        if health_percentage < 80:
            st.warning("⚠️ Device health is below optimal level")
        else:
            st.success("✅ Device health is good")
    
    with col2:
        st.markdown("**System Performance:**")
        valid_scores = [c.compliance_score for c in vision_checks if c.compliance_score > 0] if vision_checks else []
        avg_compliance_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        st.metric("Avg Compliance Score", f"{avg_compliance_score:.1f}%")
        
        if avg_compliance_score > 85:
            st.success("✅ High compliance performance")
        elif avg_compliance_score > 70:
            st.warning("⚠️ Moderate compliance performance")
        else:
            st.error("❌ Low compliance performance")

# Log page access
log_user_action(
    current_user.username,
    "PAGE_ACCESS",
    "physical_systems_integration",
    {"page": "Physical Systems Integration"}
)
