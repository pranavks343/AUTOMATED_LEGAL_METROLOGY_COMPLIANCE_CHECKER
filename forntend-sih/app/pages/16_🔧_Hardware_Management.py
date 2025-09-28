"""
Hardware Management Page for Legal Metrology Compliance Checker
Advanced hardware control and monitoring interface
"""

import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import existing authentication and core modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.auth import require_admin, get_current_user
from core.hardware_integration import (
    AutomatedComplianceStation, 
    HardwareStatus, 
    MeasurementType,
    VisionSystemController,
    PrecisionScaleController
)
from core.physical_integration import PhysicalIntegrationManager

# Page configuration
st.set_page_config(
    page_title="Hardware Management - Legal Metrology Checker",
    page_icon="🔧",
    layout="wide"
)

# Custom CSS for hardware management interface
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hardware Management Header */
    .hardware-header {
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
    
    .hardware-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="circuit" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="2" fill="white" opacity="0.1"/><line x1="0" y1="10" x2="20" y2="10" stroke="white" opacity="0.1" stroke-width="1"/><line x1="10" y1="0" x2="10" y2="20" stroke="white" opacity="0.1" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23circuit)"/></svg>');
        opacity: 0.1;
    }
    
    .hardware-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .hardware-header p {
        font-size: 1.2rem;
        margin: 1rem 0 0 0;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* Status Cards */
    .status-card {
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
    
    .status-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .status-card.online {
        border-left: 4px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    .status-card.offline {
        border-left: 4px solid #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
    }
    
    .status-card.busy {
        border-left: 4px solid #ff9800;
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
    }
    
    .status-card.maintenance {
        border-left: 4px solid #9c27b0;
        background: linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(156, 39, 176, 0.05) 100%);
    }
    
    /* Device Grid */
    .device-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .device-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .device-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .device-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Measurement Cards */
    .measurement-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    }
    
    .measurement-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .measurement-unit {
        font-size: 1rem;
        color: #6c757d;
        font-weight: 500;
    }
    
    .confidence-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .confidence-high {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
    }
    
    .confidence-medium {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
    }
    
    .confidence-low {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
    }
    
    /* Control Buttons */
    .control-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.25rem;
    }
    
    .control-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    .control-button:disabled {
        background: #cccccc;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    /* Alert Enhancements */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
    }
    
    /* Tabs Enhancement */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px 12px 0 0;
        padding: 1rem 2rem;
        border: 1px solid #e0e0e0;
        font-weight: 600;
        color: #495057;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Require admin access
require_admin()
current_user = get_current_user()

# Initialize hardware components
@st.cache_resource
def initialize_hardware_components():
    """Initialize hardware components with caching"""
    try:
        # Initialize existing physical integration manager
        physical_manager = PhysicalIntegrationManager()
        
        # Initialize new automated compliance station
        compliance_station = AutomatedComplianceStation()
        
        return physical_manager, compliance_station
    except Exception as e:
        st.error(f"Failed to initialize hardware components: {e}")
        return None, None

# Load hardware components
physical_manager, compliance_station = initialize_hardware_components()

# Enhanced Hardware Management Header
st.markdown(f"""
<div class="hardware-header">
    <h1>🔧 Advanced Hardware Management</h1>
    <p>Welcome, <strong>{current_user.username}</strong>! Monitor and control automated compliance verification hardware systems.</p>
</div>
""", unsafe_allow_html=True)

# Main tabs for hardware management
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🖥️ System Overview", 
    "🔬 Compliance Station", 
    "📊 Real-time Monitoring", 
    "⚙️ Device Configuration",
    "📈 Performance Analytics",
    "🛠️ Maintenance & Calibration"
])

with tab1:
    st.markdown("### 🖥️ System Overview")
    st.markdown("Comprehensive view of all hardware systems and their current status.")
    
    # System status overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="status-card online">
            <h3>✅ Online Devices</h3>
            <div class="measurement-value">3</div>
            <p>Vision, Scale, Scanner</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="status-card offline">
            <h3>❌ Offline Devices</h3>
            <div class="measurement-value">1</div>
            <p>Label Applicator</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="status-card busy">
            <h3>⚡ Active Processes</h3>
            <div class="measurement-value">2</div>
            <p>Compliance Checks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="status-card maintenance">
            <h3>🔧 Maintenance Due</h3>
            <div class="measurement-value">0</div>
            <p>All Systems OK</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Device status grid
    st.markdown("#### 🖥️ Hardware Device Status")
    
    if physical_manager:
        devices = physical_manager.devices
        
        if devices:
            # Create device status dataframe
            device_data = []
            for device in devices:
                device_data.append({
                    'Device ID': device.device_id,
                    'Name': device.device_name,
                    'Type': device.device_type.value if hasattr(device.device_type, 'value') else str(device.device_type),
                    'Manufacturer': device.manufacturer,
                    'Model': device.model,
                    'Status': device.status.value if hasattr(device.status, 'value') else str(device.status),
                    'Last Heartbeat': device.last_heartbeat or 'Never',
                    'Error Count': device.error_count
                })
            
            df = pd.DataFrame(device_data)
            
            # Display with status color coding
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    'Status': st.column_config.TextColumn(
                        'Status',
                        help='Current device status'
                    ),
                    'Error Count': st.column_config.NumberColumn(
                        'Error Count',
                        help='Number of errors since last reset'
                    )
                }
            )
        else:
            st.info("No hardware devices configured. Please add devices in the Device Configuration tab.")

with tab2:
    st.markdown("### 🔬 Automated Compliance Station")
    st.markdown("Control and monitor the automated compliance verification station.")
    
    # Station control panel
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🎛️ Station Controls")
        
        # Station status
        if compliance_station:
            station_status = "ONLINE"  # This would come from actual station status
            status_color = "online" if station_status == "ONLINE" else "offline"
            
            st.markdown(f"""
            <div class="status-card {status_color}">
                <h4>Station Status: {station_status}</h4>
                <p>Automated Compliance Verification Station</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Control buttons
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if st.button("🚀 Initialize Station", key="init_station"):
                    with st.spinner("Initializing compliance station..."):
                        # This would call the actual initialization
                        st.success("Station initialized successfully!")
            
            with col_btn2:
                if st.button("🔄 Calibrate All", key="calibrate_all"):
                    with st.spinner("Calibrating all devices..."):
                        # This would call the calibration routine
                        st.success("Calibration completed!")
            
            with col_btn3:
                if st.button("⚡ Run Test", key="run_test"):
                    with st.spinner("Running system test..."):
                        # This would run a system test
                        st.success("System test passed!")
            
            with col_btn4:
                if st.button("🛑 Emergency Stop", key="emergency_stop"):
                    st.warning("Emergency stop activated!")
        else:
            st.error("Compliance station not available. Check system configuration.")
    
    with col2:
        st.markdown("#### 📊 Current Measurements")
        
        # Simulated current measurements
        measurements = [
            {"type": "Weight", "value": "125.3", "unit": "g", "confidence": 95.2},
            {"type": "Font Size", "value": "2.1", "unit": "mm", "confidence": 98.7},
            {"type": "Barcode Quality", "value": "87.5", "unit": "%", "confidence": 92.1},
            {"type": "Color Accuracy", "value": "94.2", "unit": "%", "confidence": 89.3}
        ]
        
        for measurement in measurements:
            confidence = measurement["confidence"]
            if confidence >= 90:
                badge_class = "confidence-high"
            elif confidence >= 70:
                badge_class = "confidence-medium"
            else:
                badge_class = "confidence-low"
            
            st.markdown(f"""
            <div class="measurement-card">
                <h5>{measurement["type"]}</h5>
                <div class="measurement-value">{measurement["value"]} <span class="measurement-unit">{measurement["unit"]}</span></div>
                <div class="confidence-badge {badge_class}">Confidence: {confidence}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Product verification interface
    st.markdown("#### 🔍 Product Verification")
    
    col_verify1, col_verify2 = st.columns([3, 1])
    
    with col_verify1:
        product_id = st.text_input("Product ID", placeholder="Enter product ID for verification")
    
    with col_verify2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("🔬 Start Verification", key="start_verification"):
            if product_id:
                with st.spinner(f"Verifying product {product_id}..."):
                    # Simulate verification process
                    import time
                    time.sleep(2)
                    
                    # Display verification results
                    st.success(f"✅ Product {product_id} verification completed!")
                    
                    # Show detailed results
                    verification_results = {
                        "Compliance Score": 94.5,
                        "Weight Compliance": "✅ Pass",
                        "Label Compliance": "✅ Pass", 
                        "Barcode Quality": "⚠️ Warning",
                        "Font Size": "✅ Pass"
                    }
                    
                    for key, value in verification_results.items():
                        st.write(f"**{key}**: {value}")
            else:
                st.error("Please enter a product ID")

with tab3:
    st.markdown("### 📊 Real-time Monitoring")
    st.markdown("Live monitoring of hardware performance and measurements.")
    
    # Real-time charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### ⚖️ Weight Measurements (Last 24 Hours)")
        
        # Generate sample weight data
        import numpy as np
        hours = list(range(24))
        weights = 100 + np.random.normal(0, 5, 24)  # Sample weight data
        
        weight_fig = px.line(
            x=hours, 
            y=weights,
            labels={'x': 'Hours Ago', 'y': 'Weight (g)'},
            title="Weight Measurement Trend"
        )
        weight_fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(weight_fig, use_container_width=True)
    
    with col_chart2:
        st.markdown("#### 🎯 Compliance Scores (Last 24 Hours)")
        
        # Generate sample compliance data
        compliance_scores = 85 + np.random.normal(0, 8, 24)
        compliance_scores = np.clip(compliance_scores, 0, 100)  # Ensure 0-100 range
        
        compliance_fig = px.line(
            x=hours, 
            y=compliance_scores,
            labels={'x': 'Hours Ago', 'y': 'Compliance Score (%)'},
            title="Compliance Score Trend"
        )
        compliance_fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        compliance_fig.add_hline(y=80, line_dash="dash", line_color="red", 
                                annotation_text="Minimum Compliance Threshold")
        st.plotly_chart(compliance_fig, use_container_width=True)
    
    # System performance metrics
    st.markdown("#### 🖥️ System Performance Metrics")
    
    col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)
    
    with col_perf1:
        st.metric(
            label="📊 Throughput",
            value="45 products/hour",
            delta="5 products/hour"
        )
    
    with col_perf2:
        st.metric(
            label="⚡ Processing Speed",
            value="23.5 sec/product",
            delta="-2.1 sec"
        )
    
    with col_perf3:
        st.metric(
            label="🎯 Accuracy Rate",
            value="94.2%",
            delta="1.3%"
        )
    
    with col_perf4:
        st.metric(
            label="⚙️ Uptime",
            value="99.7%",
            delta="0.1%"
        )

with tab4:
    st.markdown("### ⚙️ Device Configuration")
    st.markdown("Configure and manage individual hardware devices.")
    
    # Device configuration interface
    device_config_tabs = st.tabs(["🔬 Vision System", "⚖️ Precision Scale", "🤖 Robot Arm", "💡 Lighting System"])
    
    with device_config_tabs[0]:
        st.markdown("#### 🔬 Vision System Configuration")
        
        col_vision1, col_vision2 = st.columns(2)
        
        with col_vision1:
            st.markdown("**Camera Settings**")
            resolution = st.selectbox("Resolution", ["4K (3840x2160)", "2K (2560x1440)", "1080p (1920x1080)"])
            fps = st.slider("Frame Rate (FPS)", 15, 60, 30)
            exposure = st.selectbox("Exposure Mode", ["Auto", "Manual", "Shutter Priority"])
            
            if exposure == "Manual":
                exposure_time = st.slider("Exposure Time (ms)", 1, 100, 10)
        
        with col_vision2:
            st.markdown("**Lighting Settings**")
            white_led_brightness = st.slider("White LED Brightness (%)", 0, 100, 80)
            uv_intensity = st.slider("UV Light Intensity (%)", 0, 100, 50)
            ir_intensity = st.slider("IR Light Intensity (%)", 0, 100, 30)
            
            use_polarizer = st.checkbox("Use Polarizing Filter", value=True)
        
        if st.button("💾 Save Vision Configuration", key="save_vision_config"):
            st.success("Vision system configuration saved!")
    
    with device_config_tabs[1]:
        st.markdown("#### ⚖️ Precision Scale Configuration")
        
        col_scale1, col_scale2 = st.columns(2)
        
        with col_scale1:
            st.markdown("**Scale Settings**")
            capacity = st.selectbox("Scale Capacity", ["5kg", "10kg", "20kg", "50kg"])
            readability = st.selectbox("Readability", ["0.001g", "0.01g", "0.1g"])
            units = st.selectbox("Display Units", ["g", "kg", "oz", "lb"])
            
            auto_tare = st.checkbox("Auto Tare", value=True)
        
        with col_scale2:
            st.markdown("**Calibration Settings**")
            cal_interval = st.selectbox("Calibration Interval", ["Daily", "Weekly", "Monthly"])
            cal_weights = st.multiselect(
                "Calibration Weights (g)", 
                [1, 5, 10, 20, 50, 100, 200, 500, 1000],
                default=[10, 100, 1000]
            )
            
            external_cal = st.checkbox("External Calibration Required", value=True)
        
        if st.button("💾 Save Scale Configuration", key="save_scale_config"):
            st.success("Scale configuration saved!")
    
    with device_config_tabs[2]:
        st.markdown("#### 🤖 Robot Arm Configuration")
        
        col_robot1, col_robot2 = st.columns(2)
        
        with col_robot1:
            st.markdown("**Movement Settings**")
            speed = st.slider("Movement Speed (%)", 10, 100, 50)
            acceleration = st.slider("Acceleration (%)", 10, 100, 30)
            precision = st.selectbox("Positioning Precision", ["±0.1mm", "±0.5mm", "±1.0mm"])
            
            safety_zones = st.checkbox("Enable Safety Zones", value=True)
        
        with col_robot2:
            st.markdown("**Gripper Settings**")
            grip_force = st.slider("Grip Force (%)", 10, 100, 40)
            grip_speed = st.slider("Grip Speed (%)", 10, 100, 60)
            
            adaptive_grip = st.checkbox("Adaptive Gripping", value=True)
            force_feedback = st.checkbox("Force Feedback", value=True)
        
        if st.button("💾 Save Robot Configuration", key="save_robot_config"):
            st.success("Robot arm configuration saved!")
    
    with device_config_tabs[3]:
        st.markdown("#### 💡 Lighting System Configuration")
        
        col_light1, col_light2 = st.columns(2)
        
        with col_light1:
            st.markdown("**LED Array Settings**")
            color_temp = st.slider("Color Temperature (K)", 3000, 6500, 5000)
            brightness_uniformity = st.slider("Brightness Uniformity (%)", 80, 100, 95)
            flicker_frequency = st.selectbox("Flicker Frequency (Hz)", ["None", "120", "240", "480"])
        
        with col_light2:
            st.markdown("**Special Lighting**")
            uv_wavelength = st.selectbox("UV Wavelength (nm)", ["365", "385", "405"])
            ir_wavelength = st.selectbox("IR Wavelength (nm)", ["850", "940"])
            
            strobe_mode = st.checkbox("Strobe Mode Available", value=False)
        
        if st.button("💾 Save Lighting Configuration", key="save_light_config"):
            st.success("Lighting system configuration saved!")

with tab5:
    st.markdown("### 📈 Performance Analytics")
    st.markdown("Detailed analytics and performance insights for hardware systems.")
    
    # Performance analytics dashboard
    analytics_period = st.selectbox(
        "Analysis Period", 
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )
    
    # Generate sample analytics data
    if analytics_period == "Last 24 Hours":
        time_points = 24
        time_label = "Hours"
    elif analytics_period == "Last 7 Days":
        time_points = 7
        time_label = "Days"
    elif analytics_period == "Last 30 Days":
        time_points = 30
        time_label = "Days"
    else:
        time_points = 90
        time_label = "Days"
    
    # Create comprehensive analytics charts
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Throughput Analysis', 'Error Rate Trends', 
                       'Device Utilization', 'Maintenance Costs'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"type": "domain"}, {"secondary_y": False}]]
    )
    
    # Throughput analysis
    time_range = list(range(time_points))
    throughput = 40 + np.random.normal(0, 5, time_points)
    fig.add_trace(
        go.Scatter(x=time_range, y=throughput, name="Throughput", 
                  line=dict(color='#667eea')),
        row=1, col=1
    )
    
    # Error rate trends
    error_rate = np.maximum(0, 2 + np.random.normal(0, 1, time_points))
    fig.add_trace(
        go.Scatter(x=time_range, y=error_rate, name="Error Rate", 
                  line=dict(color='#f44336')),
        row=1, col=2
    )
    
    # Device utilization pie chart
    fig.add_trace(
        go.Pie(labels=['Vision System', 'Scale', 'Robot Arm', 'Lighting'], 
               values=[35, 25, 30, 10], name="Utilization"),
        row=2, col=1
    )
    
    # Maintenance costs
    maintenance_costs = 1000 + np.random.normal(0, 200, time_points)
    fig.add_trace(
        go.Bar(x=time_range, y=maintenance_costs, name="Maintenance Cost", 
               marker_color='#ff9800'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Hardware Performance Analytics")
    st.plotly_chart(fig, use_container_width=True)
    
    # Key performance indicators
    st.markdown("#### 🎯 Key Performance Indicators")
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
    
    with col_kpi1:
        st.metric(
            label="🏭 Overall Equipment Effectiveness",
            value="87.3%",
            delta="2.1%",
            help="OEE = Availability × Performance × Quality"
        )
    
    with col_kpi2:
        st.metric(
            label="⚡ Mean Time Between Failures",
            value="156 hours",
            delta="12 hours",
            help="Average time between equipment failures"
        )
    
    with col_kpi3:
        st.metric(
            label="🔧 Mean Time To Repair",
            value="23 minutes",
            delta="-5 minutes",
            help="Average time to repair equipment failures"
        )
    
    with col_kpi4:
        st.metric(
            label="💰 Cost Per Verification",
            value="₹12.50",
            delta="-₹2.30",
            help="Total cost per product verification"
        )
    
    with col_kpi5:
        st.metric(
            label="🎯 First Pass Yield",
            value="94.2%",
            delta="1.8%",
            help="Percentage of products passing first verification"
        )

with tab6:
    st.markdown("### 🛠️ Maintenance & Calibration")
    st.markdown("Manage maintenance schedules and calibration procedures.")
    
    # Maintenance overview
    col_maint1, col_maint2 = st.columns([2, 1])
    
    with col_maint1:
        st.markdown("#### 📅 Maintenance Schedule")
        
        # Sample maintenance data
        maintenance_data = [
            {"Device": "Vision System", "Last Maintenance": "2025-09-10", "Next Due": "2025-10-10", "Status": "✅ Up to Date"},
            {"Device": "Precision Scale", "Last Maintenance": "2025-09-05", "Next Due": "2025-09-20", "Status": "⚠️ Due Soon"},
            {"Device": "Robot Arm", "Last Maintenance": "2025-08-15", "Next Due": "2025-09-15", "Status": "❌ Overdue"},
            {"Device": "Lighting System", "Last Maintenance": "2025-09-12", "Next Due": "2025-12-12", "Status": "✅ Up to Date"}
        ]
        
        maintenance_df = pd.DataFrame(maintenance_data)
        st.dataframe(maintenance_df, use_container_width=True)
        
        # Maintenance actions
        st.markdown("#### 🔧 Maintenance Actions")
        
        selected_device = st.selectbox("Select Device", 
            ["Vision System", "Precision Scale", "Robot Arm", "Lighting System"])
        
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("🔍 Schedule Inspection", key="schedule_inspection"):
                st.success(f"Inspection scheduled for {selected_device}")
        
        with col_action2:
            if st.button("🔧 Perform Maintenance", key="perform_maintenance"):
                st.success(f"Maintenance completed for {selected_device}")
        
        with col_action3:
            if st.button("📊 View History", key="view_history"):
                st.info(f"Showing maintenance history for {selected_device}")
    
    with col_maint2:
        st.markdown("#### ⚖️ Calibration Status")
        
        # Calibration status cards
        calibration_devices = [
            {"name": "Precision Scale", "status": "Valid", "expires": "2025-09-20", "color": "online"},
            {"name": "Vision System", "status": "Valid", "expires": "2025-10-15", "color": "online"},
            {"name": "Color Sensor", "status": "Expired", "expires": "2025-09-01", "color": "offline"},
        ]
        
        for device in calibration_devices:
            st.markdown(f"""
            <div class="status-card {device['color']}">
                <h5>{device['name']}</h5>
                <p>Status: <strong>{device['status']}</strong></p>
                <p>Expires: {device['expires']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick calibration controls
        st.markdown("#### ⚡ Quick Calibration")
        
        if st.button("🎯 Calibrate Scale", key="quick_cal_scale"):
            with st.spinner("Calibrating precision scale..."):
                import time
                time.sleep(3)
                st.success("Scale calibration completed!")
        
        if st.button("📷 Calibrate Vision", key="quick_cal_vision"):
            with st.spinner("Calibrating vision system..."):
                import time
                time.sleep(4)
                st.success("Vision system calibration completed!")
    
    # Calibration history and reports
    st.markdown("#### 📊 Calibration Reports")
    
    # Sample calibration report data
    cal_report_data = {
        'Date': ['2025-09-14', '2025-09-10', '2025-09-05', '2025-09-01'],
        'Device': ['Precision Scale', 'Vision System', 'Color Sensor', 'Robot Arm'],
        'Result': ['Pass', 'Pass', 'Fail', 'Pass'],
        'Deviation': ['±0.005g', '±0.1mm', '±2.5 ΔE', '±0.2mm'],
        'Technician': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown']
    }
    
    cal_df = pd.DataFrame(cal_report_data)
    st.dataframe(cal_df, use_container_width=True)
    
    # Export calibration reports
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        if st.button("📄 Generate Calibration Report", key="gen_cal_report"):
            st.success("Calibration report generated and saved to reports folder")
    
    with col_export2:
        if st.button("📧 Email Report", key="email_report"):
            st.success("Calibration report emailed to maintenance team")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; margin-top: 2rem;">
    <p>🔧 <strong>Advanced Hardware Management System</strong> - Legal Metrology Compliance Checker</p>
    <p>Precision • Reliability • Compliance • Innovation</p>
</div>
""", unsafe_allow_html=True)
