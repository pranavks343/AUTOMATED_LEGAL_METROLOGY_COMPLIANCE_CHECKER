import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from core.auth import require_auth, get_current_user
from core.physical_barcode_scanner import (
    get_physical_scanner_manager, 
    ScannerConfig, 
    ScannerConnectionType, 
    ScannerStatus,
    ScanResult
)
from core.barcode_scanner import get_barcode_scanner
from core.schemas import ExtractedFields
from core.rules_engine import load_rules, validate
from core.json_utils import safe_json_dumps

st.set_page_config(
    page_title="Physical Barcode Scanner - Legal Metrology Checker", 
    page_icon="🔌", 
    layout="wide"
)

# Enhanced Custom CSS for Physical Scanner Page
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Physical Scanner Header */
    .physical-scanner-header {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(74, 144, 226, 0.3);
    }
    
    .physical-scanner-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Scanner Status Cards */
    .scanner-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #4A90E2;
    }
    
    .scanner-card.connected {
        border-left-color: #28a745;
    }
    
    .scanner-card.disconnected {
        border-left-color: #dc3545;
    }
    
    .scanner-card.scanning {
        border-left-color: #ffc107;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        50% { box-shadow: 0 4px 25px rgba(255,193,7,0.3); }
        100% { box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-indicator.connected {
        background-color: #28a745;
    }
    
    .status-indicator.disconnected {
        background-color: #dc3545;
    }
    
    .status-indicator.scanning {
        background-color: #ffc107;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    /* Scan Result Display */
    .scan-result {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
    }
    
    /* Product Information Display */
    .product-info-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        color: #333333;
    }
    
    .product-info-card h4 {
        color: #4A90E2;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .product-detail {
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #4A90E2;
    }
    
    .product-detail strong {
        color: #495057;
        font-weight: 600;
    }
    
    .compliance-status {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .compliance-status.compliant {
        border-left: 4px solid #28a745;
    }
    
    .compliance-status.non-compliant {
        border-left: 4px solid #dc3545;
    }
    
    .issue-item {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        color: #856404;
    }
    
    .issue-item.error {
        background: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    
    /* Configuration Form */
    .config-form {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Require authentication
require_auth()
current_user = get_current_user()

# Enhanced Physical Scanner Header
st.markdown(f"""
<div class="physical-scanner-header">
    <h1>🔌 Physical Barcode Scanner</h1>
    <p>Welcome, <strong>{current_user.username}</strong>! Connect and manage physical barcode scanners for real-time scanning.</p>
    <p><small>Supports USB Serial, USB HID, Bluetooth, and Network scanners</small></p>
</div>
""", unsafe_allow_html=True)

# Initialize scanner manager
scanner_manager = get_physical_scanner_manager()
barcode_scanner = get_barcode_scanner()

# Initialize session state
if "scanning_active" not in st.session_state:
    st.session_state.scanning_active = False
if "last_scan_result" not in st.session_state:
    st.session_state.last_scan_result = None
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

# Main interface tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Scanner Control", "⚙️ Configuration", "📊 Detection", "📋 History"])

with tab1:
    st.markdown("### 🔌 Connected Scanners")
    
    # Display available scanners
    available_scanners = scanner_manager.get_available_scanners()
    
    if not available_scanners:
        st.info("ℹ️ No scanners configured. Add a scanner in the Configuration tab.")
    else:
        # Display scanner cards
        for scanner_info in available_scanners:
            status_class = scanner_info['status'].lower()
            
            with st.container():
                st.markdown(f'<div class="scanner-card {status_class}">', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    status_color = {
                        'connected': 'connected',
                        'disconnected': 'disconnected', 
                        'scanning': 'scanning'
                    }.get(scanner_info['status'].lower(), 'disconnected')
                    
                    st.markdown(f"""
                    <span class="status-indicator {status_color}"></span>
                    <strong>{scanner_info['name']}</strong><br>
                    <small>{scanner_info['manufacturer']} {scanner_info['model']} ({scanner_info['connection_type']})</small>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.write(f"**Status:** {scanner_info['status']}")
                    if scanner_info['is_active']:
                        st.success("🎯 Active")
                
                with col3:
                    if scanner_info['status'] == 'DISCONNECTED':
                        if st.button(f"🔌 Connect", key=f"connect_{scanner_info['scanner_id']}"):
                            with st.spinner("Connecting..."):
                                success = asyncio.run(scanner_manager.connect_scanner(scanner_info['scanner_id']))
                                if success:
                                    st.success("✅ Connected!")
                                    st.rerun()
                                else:
                                    st.error("❌ Connection failed")
                    
                    elif scanner_info['status'] == 'CONNECTED':
                        if st.button(f"🔌 Disconnect", key=f"disconnect_{scanner_info['scanner_id']}"):
                            with st.spinner("Disconnecting..."):
                                success = asyncio.run(scanner_manager.disconnect_active_scanner())
                                if success:
                                    st.success("✅ Disconnected!")
                                    st.rerun()
                
                with col4:
                    if scanner_info['status'] == 'CONNECTED' and scanner_info['is_active']:
                        if not st.session_state.scanning_active:
                            if st.button(f"▶️ Start Scan", key=f"start_{scanner_info['scanner_id']}"):
                                # Define scan callback
                                def scan_callback(result: ScanResult):
                                    st.session_state.last_scan_result = result
                                    st.session_state.scan_history.append({
                                        'timestamp': result.timestamp,
                                        'barcode': result.barcode,
                                        'scanner': result.scanner_id,
                                        'quality': result.quality
                                    })
                                
                                success = asyncio.run(scanner_manager.start_scanning(scan_callback))
                                if success:
                                    st.session_state.scanning_active = True
                                    st.success("✅ Scanning started!")
                                    st.rerun()
                        else:
                            if st.button(f"⏹️ Stop Scan", key=f"stop_{scanner_info['scanner_id']}"):
                                success = asyncio.run(scanner_manager.stop_scanning())
                                if success:
                                    st.session_state.scanning_active = False
                                    st.success("✅ Scanning stopped!")
                                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Display scan results
    if st.session_state.last_scan_result:
        st.markdown("### 📊 Latest Scan Result")
        result = st.session_state.last_scan_result
        
        st.markdown(f"""
        <div class="scan-result">
            <h3>📦 Barcode Detected!</h3>
            <p><strong>Code:</strong> {result.barcode}</p>
            <p><strong>Quality:</strong> {result.quality}% | <strong>Scanner:</strong> {result.scanner_id}</p>
            <p><small>Scanned at: {result.timestamp}</small></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-lookup product information
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔍 Look Up Product Info", type="primary"):
                with st.spinner("Looking up product information..."):
                    barcode_data = barcode_scanner.lookup_barcode(result.barcode)
        
        # Auto-lookup on scan (if not already done)
        if 'last_lookup_barcode' not in st.session_state or st.session_state.last_lookup_barcode != result.barcode:
            with st.spinner("🔍 Auto-looking up product information..."):
                barcode_data = barcode_scanner.lookup_barcode(result.barcode)
                st.session_state.last_lookup_barcode = result.barcode
                st.session_state.last_barcode_data = barcode_data
        else:
            barcode_data = st.session_state.get('last_barcode_data')
        
        # Display product information if available
        if barcode_data:
            st.success(f"✅ Product found via {barcode_data.source_api}!")
            
            # Display product information with light background
            st.markdown(f"""
            <div class="product-info-card">
                <h4>📦 Product Information</h4>
                <div class="product-detail">
                    <strong>Product Name:</strong> {barcode_data.product_name or 'Not available'}
                </div>
                <div class="product-detail">
                    <strong>Brand:</strong> {barcode_data.brand or 'Not available'}
                </div>
                <div class="product-detail">
                    <strong>Category:</strong> {barcode_data.category or 'Not available'}
                </div>
                <div class="product-detail">
                    <strong>Net Weight/Quantity:</strong> {barcode_data.net_weight or 'Not available'}
                </div>
                <div class="product-detail">
                    <strong>Manufacturer:</strong> {barcode_data.manufacturer or 'Not available'}
                </div>
                <div class="product-detail">
                    <strong>Country of Origin:</strong> {barcode_data.country_of_origin or 'Not available'}
                </div>
                <div class="product-detail">
                    <strong>Data Source:</strong> {barcode_data.source_api}
                </div>
                <div class="product-detail">
                    <strong>Confidence Score:</strong> {barcode_data.confidence * 100:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display product image if available
            if barcode_data.images:
                try:
                    st.markdown("#### 📷 Product Image")
                    st.image(barcode_data.images[0], caption="Product Image", width=200)
                except:
                    st.info("📷 Product image not available")
            
            # Perform compliance validation
            st.markdown("#### ⚖️ Compliance Analysis")
            
            # Extract compliance fields
            compliance_fields = barcode_scanner.extract_compliance_fields(barcode_data)
            
            # Convert to ExtractedFields for validation
            extracted_fields = ExtractedFields(
                manufacturer_name=compliance_fields.get('manufacturer_name', ''),
                mrp_raw=compliance_fields.get('mrp_raw', ''),
                net_quantity_raw=compliance_fields.get('net_quantity_raw', ''),
                country_of_origin=compliance_fields.get('country_of_origin', ''),
                extra={
                    'barcode': barcode_data.barcode,
                    'category': barcode_data.category,
                    'data_source': compliance_fields.get('data_source', ''),
                    'confidence_score': compliance_fields.get('confidence_score', 0)
                }
            )
            
            # Validate compliance
            rules = load_rules("app/data/rules/legal_metrology_rules.yaml")
            validation_result = validate(extracted_fields, rules)
            
            # Display compliance status with light background
            status_class = "compliant" if validation_result.is_compliant else "non-compliant"
            status_text = "✅ COMPLIANT" if validation_result.is_compliant else "❌ NON-COMPLIANT"
            status_color = "#28a745" if validation_result.is_compliant else "#dc3545"
            
            st.markdown(f"""
            <div class="compliance-status {status_class}">
                <h4>⚖️ Compliance Analysis</h4>
                <div style="text-align: center; margin: 1rem 0;">
                    <h3 style="color: {status_color}; margin: 0;">{status_text}</h3>
                    <p style="color: #6c757d; margin: 0.5rem 0;">Score: {validation_result.score}/100</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display issues if any
            if validation_result.issues:
                st.markdown("#### 🔍 Issues Found")
                for issue in validation_result.issues:
                    level_class = "error" if issue.level == "error" else ""
                    level_icon = "🔴" if issue.level == "error" else "🟡"
                    st.markdown(f"""
                    <div class="issue-item {level_class}">
                        <strong>{level_icon} {issue.field}:</strong> {issue.message}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Product not found in any database")
        
        with col2:
            if st.button("🗑️ Clear Result"):
                st.session_state.last_scan_result = None
                st.rerun()

with tab2:
    st.markdown("### ⚙️ Scanner Configuration")
    
    # Add new scanner section
    with st.expander("➕ Add New Scanner", expanded=False):
        st.markdown('<div class="config-form">', unsafe_allow_html=True)
        
        with st.form("add_scanner_form"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                scanner_name = st.text_input("Scanner Name", placeholder="e.g., Honeywell 1450g")
                manufacturer = st.text_input("Manufacturer", placeholder="e.g., Honeywell")
                model = st.text_input("Model", placeholder="e.g., 1450g")
                
                connection_type = st.selectbox(
                    "Connection Type",
                    options=[
                        ScannerConnectionType.USB_SERIAL.value,
                        ScannerConnectionType.USB_HID.value,
                        ScannerConnectionType.BLUETOOTH.value,
                        ScannerConnectionType.NETWORK.value
                    ]
                )
            
            with col2:
                # Connection-specific settings
                if connection_type == ScannerConnectionType.USB_SERIAL.value:
                    port = st.text_input("COM Port", placeholder="e.g., COM3 or /dev/ttyUSB0")
                    baud_rate = st.selectbox("Baud Rate", [9600, 19200, 38400, 57600, 115200], index=0)
                    
                elif connection_type == ScannerConnectionType.USB_HID.value:
                    vendor_id = st.text_input("Vendor ID (hex)", placeholder="e.g., 0x05E0")
                    product_id = st.text_input("Product ID (hex)", placeholder="e.g., 0x1450")
                    
                elif connection_type == ScannerConnectionType.NETWORK.value:
                    ip_address = st.text_input("IP Address", placeholder="e.g., 192.168.1.100")
                    tcp_port = st.number_input("TCP Port", min_value=1, max_value=65535, value=8080)
                
                # Common settings
                beep_enabled = st.checkbox("Enable Beep", value=True)
                led_enabled = st.checkbox("Enable LED", value=True)
            
            submitted = st.form_submit_button("➕ Add Scanner", type="primary")
            
            if submitted and scanner_name and manufacturer and model:
                try:
                    scanner_id = f"SCANNER_{len(scanner_manager.scanners) + 1:03d}"
                    
                    config = ScannerConfig(
                        scanner_id=scanner_id,
                        name=scanner_name,
                        manufacturer=manufacturer,
                        model=model,
                        connection_type=ScannerConnectionType(connection_type),
                        beep_enabled=beep_enabled,
                        led_enabled=led_enabled
                    )
                    
                    # Set connection-specific parameters
                    if connection_type == ScannerConnectionType.USB_SERIAL.value:
                        config.port = port if port else None
                        config.baud_rate = baud_rate
                        
                    elif connection_type == ScannerConnectionType.USB_HID.value:
                        if vendor_id:
                            config.vendor_id = int(vendor_id, 16) if vendor_id.startswith('0x') else int(vendor_id)
                        if product_id:
                            config.product_id = int(product_id, 16) if product_id.startswith('0x') else int(product_id)
                            
                    elif connection_type == ScannerConnectionType.NETWORK.value:
                        config.ip_address = ip_address if ip_address else None
                        config.tcp_port = tcp_port
                    
                    success = scanner_manager.add_scanner(config)
                    
                    if success:
                        st.success(f"✅ Scanner '{scanner_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add scanner")
                        
                except Exception as e:
                    st.error(f"❌ Error adding scanner: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Manage existing scanners
    if available_scanners:
        st.markdown("#### 📋 Manage Scanners")
        
        for scanner_info in available_scanners:
            with st.expander(f"🔧 {scanner_info['name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**ID:** {scanner_info['scanner_id']}")
                    st.write(f"**Manufacturer:** {scanner_info['manufacturer']}")
                    st.write(f"**Model:** {scanner_info['model']}")
                    st.write(f"**Connection:** {scanner_info['connection_type']}")
                    st.write(f"**Status:** {scanner_info['status']}")
                
                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_{scanner_info['scanner_id']}"):
                        success = scanner_manager.remove_scanner(scanner_info['scanner_id'])
                        if success:
                            st.success("✅ Scanner removed!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to remove scanner")

with tab3:
    st.markdown("### 📊 Scanner Detection")
    
    # Auto-detect connected scanners
    if st.button("🔍 Detect Connected Scanners", type="primary"):
        with st.spinner("Detecting connected scanners..."):
            detected = scanner_manager.detect_connected_scanners()
            
            if detected:
                st.success(f"✅ Found {len(detected)} connected scanner(s)!")
                
                for device in detected:
                    with st.container():
                        st.markdown("---")
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.write(f"**Type:** {device['type']}")
                            if 'description' in device:
                                st.write(f"**Description:** {device['description']}")
                            elif 'product' in device:
                                st.write(f"**Product:** {device['product']}")
                        
                        with col2:
                            if 'port' in device:
                                st.write(f"**Port:** {device['port']}")
                            if 'vid' in device and 'pid' in device:
                                st.write(f"**VID:PID:** 0x{device['vid']:04X}:0x{device['pid']:04X}")
                        
                        with col3:
                            if st.button(f"➕ Add", key=f"add_detected_{device.get('port', device.get('vid', 'unknown'))}"):
                                # Pre-fill form with detected device info
                                st.info("Use the 'Add New Scanner' form above with the detected information")
            else:
                st.warning("⚠️ No scanners detected. Make sure your scanner is connected and drivers are installed.")
    
    # Display system information
    st.markdown("#### 💻 System Information")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Available Serial Ports:**")
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            
            if ports:
                for port in ports:
                    st.write(f"• {port.device}: {port.description}")
            else:
                st.write("No serial ports found")
        except Exception as e:
            st.write(f"Error: {e}")
    
    with col2:
        st.markdown("**USB Devices:**")
        try:
            import usb.core
            devices = usb.core.find(find_all=True)
            device_count = 0
            
            for device in devices:
                if device_count < 5:  # Limit display
                    try:
                        manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else 'Unknown'
                        product = usb.util.get_string(device, device.iProduct) if device.iProduct else 'Unknown'
                        st.write(f"• {manufacturer}: {product}")
                        device_count += 1
                    except:
                        pass
            
            if device_count == 0:
                st.write("No USB devices accessible")
                
        except Exception as e:
            st.write(f"Error: {e}")

with tab4:
    st.markdown("### 📋 Scan History")
    
    if st.session_state.scan_history:
        # Display recent scans
        st.markdown(f"**Recent Scans ({len(st.session_state.scan_history)} total):**")
        
        # Show last 20 scans
        recent_scans = st.session_state.scan_history[-20:]
        recent_scans.reverse()  # Show newest first
        
        for i, scan in enumerate(recent_scans):
            with st.expander(f"📦 {scan['barcode']} - {scan['timestamp'][:19]}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Barcode:** {scan['barcode']}")
                    st.write(f"**Scanner:** {scan['scanner']}")
                
                with col2:
                    st.write(f"**Quality:** {scan['quality']}%")
                    st.write(f"**Time:** {scan['timestamp'][11:19]}")
                
                with col3:
                    if st.button(f"🔍 Lookup", key=f"lookup_history_{i}"):
                        # Create a mock scan result for lookup
                        mock_result = ScanResult(
                            scanner_id=scan['scanner'],
                            barcode=scan['barcode'],
                            format="Unknown",
                            timestamp=scan['timestamp'],
                            quality=scan['quality']
                        )
                        st.session_state.last_scan_result = mock_result
                        st.rerun()
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.scan_history = []
            st.success("✅ History cleared!")
            st.rerun()
    
    else:
        st.info("📝 No scan history available. Start scanning to see results here.")

# Footer with status information
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Physical Scanner Manager | User: {current_user.username} | 
    Scanners: {len(available_scanners)} configured | 
    Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}
</div>
""", unsafe_allow_html=True)
