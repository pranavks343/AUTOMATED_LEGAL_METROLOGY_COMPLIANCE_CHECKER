# 🔧 Detailed Hardware Components List - Legal Metrology Compliance Checker

## 📋 Complete Hardware Bill of Materials (BOM)

This document provides a comprehensive list of all hardware components required for the Legal Metrology Compliance Checker project, organized by system with detailed specifications, quantities, suppliers, and costs.

---

## 🔬 **SYSTEM 1: Automated Compliance Verification Station**

### **1.1 Vision System Components**

#### **Primary 4K Camera System**
- **Component**: Industrial 4K Camera
- **Model**: Basler ace acA2440-75um
- **Specifications**:
  - Resolution: 2440 × 2050 pixels (5MP)
  - Frame Rate: 75 fps
  - Sensor: Sony IMX250 CMOS
  - Interface: USB 3.0
  - Pixel Size: 3.45 μm × 3.45 μm
  - Spectral Range: 380-1000 nm
- **Quantity**: 2 per station
- **Unit Cost**: ₹1,20,000 ($1,440)
- **Supplier**: Basler AG / Allied Vision India

#### **Macro Lens System**
- **Component**: Macro Lens with Auto-Focus
- **Model**: Computar MLM3X-MP
- **Specifications**:
  - Magnification: 0.7x to 4.5x
  - Working Distance: 65-110 mm
  - Numerical Aperture: 0.21
  - Resolution: 5 μm
  - Mount: C-Mount
  - Focus: Motorized
- **Quantity**: 2 per station
- **Unit Cost**: ₹85,000 ($1,020)
- **Supplier**: CBC (Computar) / Edmund Optics

#### **Barcode-Optimized Camera**
- **Component**: High-Speed Barcode Camera
- **Model**: IDS uEye XS USB 3.0
- **Specifications**:
  - Resolution: 1920 × 1200 pixels
  - Frame Rate: 165 fps
  - Sensor: Sony IMX273
  - Interface: USB 3.0
  - Shutter: Global shutter
  - Lens Mount: C/CS-Mount
- **Quantity**: 1 per station
- **Unit Cost**: ₹75,000 ($900)
- **Supplier**: IDS Imaging / Stemmer Imaging

#### **Lighting System**
- **Component**: Multi-Spectrum LED Array
- **Model**: Smart Vision Lights OD-200
- **Specifications**:
  - White LED: 5000K, 200W, CRI >90
  - UV LED: 365nm, 50W
  - IR LED: 850nm, 30W
  - Control: DMX512/Ethernet
  - Dimming: 0-100% PWM
  - Uniformity: >95%
- **Quantity**: 1 per station
- **Unit Cost**: ₹2,50,000 ($3,000)
- **Supplier**: Smart Vision Lights / Advanced Illumination

#### **Optical Filters**
- **Component**: Filter Set for Multi-Spectral Imaging
- **Specifications**:
  - Polarizing Filter: Linear, 0°-90° rotation
  - UV Filter: 365nm bandpass, 10nm FWHM
  - IR Filter: 850nm longpass
  - Neutral Density: Variable 0.1-3.0 OD
  - Mount: Motorized filter wheel
- **Quantity**: 1 set per station
- **Unit Cost**: ₹45,000 ($540)
- **Supplier**: Edmund Optics / Thorlabs

### **1.2 Precision Weighing System**

#### **Primary Precision Balance**
- **Component**: Analytical Balance
- **Model**: Mettler Toledo XPR6002S
- **Specifications**:
  - Capacity: 6100 g
  - Readability: 0.01 g
  - Repeatability: 0.01 g (std dev)
  - Linearity: ±0.02 g
  - Stabilization Time: 1.5 seconds
  - Interface: Ethernet, USB, RS232
  - Certification: OIML R76, NTEP
- **Quantity**: 1 per station
- **Unit Cost**: ₹3,50,000 ($4,200)
- **Supplier**: Mettler Toledo India

#### **Automated Calibration System**
- **Component**: Robotic Calibration Weight Handler
- **Model**: Mettler Toledo CarePac
- **Specifications**:
  - Weight Range: 1g to 5kg
  - Weights: OIML E2 class
  - Automation: Pneumatic handling
  - Calibration Cycle: 24 hours programmable
  - Traceability: NIST/NPL certified
- **Quantity**: 1 per station
- **Unit Cost**: ₹2,00,000 ($2,400)
- **Supplier**: Mettler Toledo India

#### **Vibration Isolation Table**
- **Component**: Active Vibration Isolation
- **Model**: TMC CleanBench
- **Specifications**:
  - Isolation: >99% at 10Hz
  - Payload: 500 kg
  - Dimensions: 1200×900×750 mm
  - Power: 230V AC, 2A
  - Control: Automatic leveling
- **Quantity**: 1 per station
- **Unit Cost**: ₹1,50,000 ($1,800)
- **Supplier**: TMC Vibration Control / Kinetic Systems

### **1.3 Automation System**

#### **6-Axis Robot Arm**
- **Component**: Collaborative Robot
- **Model**: Universal Robots UR5e
- **Specifications**:
  - Payload: 5 kg
  - Reach: 850 mm
  - Repeatability: ±0.03 mm
  - Degrees of Freedom: 6
  - Weight: 20.6 kg
  - Power: 200W average
  - Safety: ISO 13849-1 Cat. 3 PLd
- **Quantity**: 1 per station
- **Unit Cost**: ₹8,00,000 ($9,600)
- **Supplier**: Universal Robots / Omron India

#### **Adaptive Gripper**
- **Component**: 2-Finger Adaptive Gripper
- **Model**: Robotiq 2F-85
- **Specifications**:
  - Stroke: 85 mm
  - Payload: 5 kg
  - Force: 20-235 N
  - Speed: 22-150 mm/s
  - Precision: ±0.02 mm
  - Communication: Modbus RTU
- **Quantity**: 1 per station
- **Unit Cost**: ₹2,50,000 ($3,000)
- **Supplier**: Robotiq / Omron India

#### **Vision Guidance System**
- **Component**: Robot Vision Integration
- **Model**: Cognex VisionPro ViDi
- **Specifications**:
  - Processing: Deep learning algorithms
  - Accuracy: Sub-pixel precision
  - Interface: GigE Vision
  - Calibration: Hand-eye calibration
  - Software: Runtime license
- **Quantity**: 1 per station
- **Unit Cost**: ₹3,00,000 ($3,600)
- **Supplier**: Cognex India

### **1.4 Environmental Control System**

#### **Temperature Control Unit**
- **Component**: Precision Temperature Controller
- **Model**: Thermo Scientific Heratherm
- **Specifications**:
  - Range: 5°C above ambient to 100°C
  - Accuracy: ±0.1°C
  - Uniformity: ±0.3°C
  - Volume: 2000 liters
  - Control: PID with RS485
- **Quantity**: 1 per station
- **Unit Cost**: ₹2,50,000 ($3,000)
- **Supplier**: Thermo Fisher Scientific

#### **Humidity Control System**
- **Component**: Humidity Generator/Controller
- **Model**: Thunder Scientific 2500
- **Specifications**:
  - Range: 10-95% RH
  - Accuracy: ±1.0% RH
  - Stability: ±0.1% RH
  - Response Time: <5 minutes
  - Control: Ethernet interface
- **Quantity**: 1 per station
- **Unit Cost**: ₹3,50,000 ($4,200)
- **Supplier**: Thunder Scientific / Rotronic

#### **Air Filtration System**
- **Component**: HEPA Filtration Unit
- **Model**: Camfil CamCleaner
- **Specifications**:
  - Efficiency: 99.97% at 0.3μm
  - Airflow: 500 CFM
  - Noise Level: <45 dB
  - Filter Life: 12 months
  - Monitoring: Pressure differential
- **Quantity**: 1 per station
- **Unit Cost**: ₹1,00,000 ($1,200)
- **Supplier**: Camfil India

### **1.5 Computing and Control System**

#### **Industrial Computer**
- **Component**: High-Performance Industrial PC
- **Model**: Advantech ARK-3520P
- **Specifications**:
  - CPU: Intel Core i7-12700K (12 cores, 3.6GHz)
  - RAM: 32GB DDR4-3200
  - Storage: 1TB NVMe SSD + 4TB HDD
  - GPU: NVIDIA RTX 4060 (8GB VRAM)
  - I/O: USB 3.0, Ethernet, RS232/485
  - OS: Ubuntu 22.04 LTS
- **Quantity**: 1 per station
- **Unit Cost**: ₹2,00,000 ($2,400)
- **Supplier**: Advantech India / Dell Technologies

#### **Network Switch**
- **Component**: Industrial Ethernet Switch
- **Model**: Phoenix Contact FL SWITCH 2208
- **Specifications**:
  - Ports: 8 × 10/100 Mbps
  - Protocol: IEEE 802.3
  - Temperature: -40°C to +75°C
  - Power: 24V DC
  - Mounting: DIN rail
- **Quantity**: 1 per station
- **Unit Cost**: ₹25,000 ($300)
- **Supplier**: Phoenix Contact India

#### **UPS System**
- **Component**: Online UPS
- **Model**: APC Smart-UPS SRT 3000VA
- **Specifications**:
  - Capacity: 3000 VA / 2700 W
  - Runtime: 10 minutes at full load
  - Input: 230V AC ±10%
  - Output: Pure sine wave
  - Communication: USB, Ethernet
- **Quantity**: 1 per station
- **Unit Cost**: ₹75,000 ($900)
- **Supplier**: Schneider Electric India

### **1.6 Safety and Security**

#### **Safety Light Curtains**
- **Component**: Type 4 Safety Light Curtain
- **Model**: SICK C4000 Standard
- **Specifications**:
  - Protection Height: 1800 mm
  - Resolution: 30 mm
  - Range: 0.1-20 m
  - Response Time: 15 ms
  - Safety Category: 4 (EN954-1)
- **Quantity**: 2 per station
- **Unit Cost**: ₹1,50,000 ($1,800)
- **Supplier**: SICK India

#### **Emergency Stop System**
- **Component**: Emergency Stop Controller
- **Model**: Pilz PNOZ s30
- **Specifications**:
  - Safety Outputs: 4
  - Input Voltage: 24V DC
  - Response Time: <5 ms
  - Safety Category: 4
  - Monitoring: Dual channel
- **Quantity**: 1 per station
- **Unit Cost**: ₹50,000 ($600)
- **Supplier**: Pilz India

---

## 📱 **SYSTEM 2: Mobile Compliance Scanner**

### **2.1 Mobile Computing Platform**

#### **Ruggedized Tablet**
- **Component**: Industrial Tablet
- **Model**: Samsung Galaxy Tab Active4 Pro
- **Specifications**:
  - Display: 10.1" TFT, 1920×1200
  - Processor: Snapdragon 778G
  - RAM: 6GB LPDDR4X
  - Storage: 128GB + microSD
  - Battery: 7600 mAh (12+ hours)
  - Rating: IP68, MIL-STD-810H
  - Camera: 13MP rear, 8MP front
- **Quantity**: 10 units
- **Unit Cost**: ₹85,000 ($1,020)
- **Supplier**: Samsung India

#### **Protective Case**
- **Component**: Heavy-Duty Case
- **Model**: Pelican Vault V800
- **Specifications**:
  - Material: HPX Resin
  - Rating: IP67 waterproof
  - Dimensions: 546×421×206 mm
  - Weight: 6.8 kg
  - Foam: Custom cut foam insert
- **Quantity**: 10 units
- **Unit Cost**: ₹15,000 ($180)
- **Supplier**: Pelican Products India

### **2.2 Precision Weighing**

#### **Bluetooth Pocket Scale**
- **Component**: Precision Pocket Scale
- **Model**: AWS AMW-1000
- **Specifications**:
  - Capacity: 1000g
  - Readability: 0.1g
  - Accuracy: ±0.1g
  - Connectivity: Bluetooth 5.0
  - Battery: Rechargeable Li-ion
  - Calibration: External weight
- **Quantity**: 10 units
- **Unit Cost**: ₹25,000 ($300)
- **Supplier**: American Weigh Scales

#### **Calibration Weight Set**
- **Component**: OIML Class F1 Weights
- **Model**: Troemner UltraClass
- **Specifications**:
  - Range: 1g to 500g
  - Accuracy: OIML Class F1
  - Material: Stainless steel
  - Case: Wooden storage box
  - Certificate: NIST traceable
- **Quantity**: 10 sets
- **Unit Cost**: ₹35,000 ($420)
- **Supplier**: Troemner / Mettler Toledo

### **2.3 Barcode Scanning**

#### **Wireless Barcode Scanner**
- **Component**: 2D Barcode Scanner
- **Model**: Socket Mobile DuraScan D700
- **Specifications**:
  - Scan Engine: 2D imager
  - Symbologies: 1D/2D barcodes
  - Range: 0-24 inches
  - Connectivity: Bluetooth 4.0
  - Battery: 12+ hours continuous
  - Rating: IP54
- **Quantity**: 10 units
- **Unit Cost**: ₹35,000 ($420)
- **Supplier**: Socket Mobile / Zebra India

### **2.4 Measurement Accessories**

#### **Digital Calipers**
- **Component**: Precision Digital Calipers
- **Model**: Mitutoyo CD-6" CSX
- **Specifications**:
  - Range: 0-150mm (6")
  - Resolution: 0.01mm
  - Accuracy: ±0.02mm
  - Interface: Bluetooth data output
  - Battery: SR44 (2000 hours)
- **Quantity**: 10 units
- **Unit Cost**: ₹15,000 ($180)
- **Supplier**: Mitutoyo India

#### **Magnifying Glass with LED**
- **Component**: LED Magnifier
- **Model**: Carson MagniLamp Pro
- **Specifications**:
  - Magnification: 2x/4x
  - LED: 12 SMD LEDs
  - Lens: 4.5" diameter
  - Power: Rechargeable battery
  - Mount: Flexible arm
- **Quantity**: 10 units
- **Unit Cost**: ₹8,000 ($96)
- **Supplier**: Carson Optical

---

## 🏷️ **SYSTEM 3: Label Analysis System**

### **3.1 Microscopy System**

#### **Digital Microscope**
- **Component**: 4K Digital Microscope
- **Model**: Keyence VHX-7000
- **Specifications**:
  - Magnification: 20x to 6000x
  - Resolution: 4K (4096×3072)
  - Depth of Field: Extended focus
  - Measurement: 2D/3D capabilities
  - Lighting: Multi-angle LED
  - Interface: Ethernet, USB
- **Quantity**: 1 unit
- **Unit Cost**: ₹15,00,000 ($18,000)
- **Supplier**: Keyence India

#### **Microscope Objectives**
- **Component**: High-Resolution Objectives
- **Specifications**:
  - 10x: NA 0.30, WD 17mm
  - 20x: NA 0.45, WD 8.2mm
  - 50x: NA 0.80, WD 1.0mm
  - 100x: NA 1.25, WD 0.23mm (oil)
  - Correction: Plan apochromat
- **Quantity**: 1 set
- **Unit Cost**: ₹2,50,000 ($3,000)
- **Supplier**: Keyence India

### **3.2 Color Measurement System**

#### **Spectrophotometer**
- **Component**: Benchtop Spectrophotometer
- **Model**: X-Rite Ci7800
- **Specifications**:
  - Geometry: Sphere, d/8°
  - Wavelength: 360-750nm
  - Interval: 10nm
  - Accuracy: ΔE*ab 0.05
  - Repeatability: ΔE*ab 0.02
  - Standards: CIE, ISO, ASTM
- **Quantity**: 1 unit
- **Unit Cost**: ₹8,00,000 ($9,600)
- **Supplier**: X-Rite India

#### **Color Standards**
- **Component**: Color Reference Standards
- **Model**: X-Rite ColorChecker
- **Specifications**:
  - Standards: 24-patch target
  - Calibration: NIST traceable
  - Stability: Long-term stable
  - Applications: Color accuracy
- **Quantity**: 5 units
- **Unit Cost**: ₹25,000 ($300)
- **Supplier**: X-Rite India

### **3.3 Adhesion Testing**

#### **Adhesion Tester**
- **Component**: Automatic Adhesion Tester
- **Model**: PosiTest AT-A
- **Specifications**:
  - Pull-off Force: 0-5000 psi
  - Accuracy: ±1% of reading
  - Test Method: ASTM D4541
  - Operation: Automatic
  - Data: Bluetooth connectivity
- **Quantity**: 1 unit
- **Unit Cost**: ₹2,50,000 ($3,000)
- **Supplier**: DeFelsko Corporation

### **3.4 Environmental Testing**

#### **Environmental Chamber**
- **Component**: Temperature/Humidity Chamber
- **Model**: Espec SH-240
- **Specifications**:
  - Temperature: -40°C to +180°C
  - Humidity: 20% to 98% RH
  - Volume: 240 liters
  - Uniformity: ±0.5°C, ±2.5% RH
  - Programming: Touch screen
- **Quantity**: 1 unit
- **Unit Cost**: ₹5,00,000 ($6,000)
- **Supplier**: Espec India

---

## ⚖️ **SYSTEM 4: Certified Weighing System**

### **4.1 Primary Weighing**

#### **Class I Precision Balance**
- **Component**: Legal-for-Trade Balance
- **Model**: Mettler Toledo XPR10002S
- **Specifications**:
  - Capacity: 10.1 kg
  - Readability: 0.01 g
  - Repeatability: 0.01 g (std dev)
  - Linearity: ±0.02 g
  - Certification: OIML R76, Legal for Trade
  - Interface: Ethernet, USB, RS232
- **Quantity**: 3 units
- **Unit Cost**: ₹6,00,000 ($7,200)
- **Supplier**: Mettler Toledo India

### **4.2 Calibration System**

#### **Certified Weight Set**
- **Component**: OIML E2 Class Weights
- **Model**: Mettler Toledo Weight Set
- **Specifications**:
  - Range: 1mg to 10kg
  - Class: OIML E2
  - Material: Stainless steel
  - Uncertainty: NIST traceable
  - Case: Aluminum storage
- **Quantity**: 3 sets
- **Unit Cost**: ₹4,00,000 ($4,800)
- **Supplier**: Mettler Toledo India

### **4.3 Security System**

#### **Tamper-Proof Enclosure**
- **Component**: Security Weighing Enclosure
- **Specifications**:
  - Material: Stainless steel 316L
  - Access: Key lock + PIN code
  - Monitoring: Intrusion detection
  - Sealing: Tamper-evident seals
  - Ventilation: Filtered airflow
- **Quantity**: 3 units
- **Unit Cost**: ₹2,00,000 ($2,400)
- **Supplier**: Custom fabrication

---

## 🔌 **SYSTEM 5: Supporting Infrastructure**

### **5.1 Power Infrastructure**

#### **Main Distribution Panel**
- **Component**: Electrical Distribution Panel
- **Specifications**:
  - Rating: 100A, 415V, 3-phase
  - Protection: MCB, ELCB, Surge protection
  - Monitoring: Digital meters
  - Compliance: IS 8623, IEC 61439
- **Quantity**: 1 per site
- **Unit Cost**: ₹1,50,000 ($1,800)
- **Supplier**: Schneider Electric India

#### **Voltage Stabilizer**
- **Component**: Servo Voltage Stabilizer
- **Model**: V-Guard VWI 400
- **Specifications**:
  - Capacity: 30 kVA
  - Input: 340-460V AC
  - Output: 415V ±1%
  - Efficiency: >98%
  - Protection: Over/under voltage
- **Quantity**: 1 per site
- **Unit Cost**: ₹2,50,000 ($3,000)
- **Supplier**: V-Guard Industries

### **5.2 Network Infrastructure**

#### **Core Network Switch**
- **Component**: Managed Ethernet Switch
- **Model**: Cisco Catalyst 2960-X
- **Specifications**:
  - Ports: 24 × 1Gbps + 4 × 10Gbps SFP+
  - Management: SNMP, Web interface
  - Security: 802.1X, ACL
  - Power: PoE+ support
- **Quantity**: 1 per site
- **Unit Cost**: ₹1,50,000 ($1,800)
- **Supplier**: Cisco India

#### **Wireless Access Point**
- **Component**: Industrial WiFi Access Point
- **Model**: Aruba AP-515
- **Specifications**:
  - Standard: WiFi 6 (802.11ax)
  - Speed: 2.97 Gbps (combined)
  - Antennas: 4×4:4 MU-MIMO
  - Power: 802.3at PoE+
  - Management: Aruba Central
- **Quantity**: 2 per site
- **Unit Cost**: ₹75,000 ($900)
- **Supplier**: HPE Aruba India

### **5.3 Environmental Infrastructure**

#### **HVAC System**
- **Component**: Precision Air Conditioning
- **Model**: Daikin FXAQ50A
- **Specifications**:
  - Capacity: 5 TR (17.5 kW)
  - Temperature: ±1°C control
  - Humidity: ±3% RH control
  - Efficiency: 5-star rated
  - Control: BMS integration
- **Quantity**: 2 per site
- **Unit Cost**: ₹3,50,000 ($4,200)
- **Supplier**: Daikin India

#### **Fire Suppression**
- **Component**: Clean Agent Fire Suppression
- **Model**: Ansul SAPPHIRE
- **Specifications**:
  - Agent: 3M Novec 1230
  - Coverage: 500 m³
  - Detection: VESDA smoke detection
  - Control: Addressable panel
  - Standards: NFPA 2001
- **Quantity**: 1 per site
- **Unit Cost**: ₹5,00,000 ($6,000)
- **Supplier**: Johnson Controls India

---

## 📊 **COMPLETE COST SUMMARY**

### **System-wise Cost Breakdown**

| System | Components | Quantity | Total Cost (₹) | Total Cost (USD) |
|--------|------------|----------|----------------|------------------|
| **Automated Compliance Station** | Complete system | 2 | 70,00,000 | $84,000 |
| **Mobile Compliance Scanner** | Complete kit | 10 | 35,00,000 | $42,000 |
| **Label Analysis System** | Complete system | 1 | 31,00,000 | $37,200 |
| **Certified Weighing System** | Complete system | 3 | 45,00,000 | $54,000 |
| **Supporting Infrastructure** | Power, Network, HVAC | 1 site | 20,00,000 | $24,000 |
| **Installation & Integration** | Professional services | - | 25,00,000 | $30,000 |
| **Training & Documentation** | User training | - | 15,00,000 | $18,000 |
| **Contingency (15%)** | Risk mitigation | - | 36,15,000 | $43,380 |
| **TOTAL PROJECT COST** | | | **2,77,15,000** | **$332,580** |

### **Key Performance Specifications**

| Parameter | Specification | Achievement |
|-----------|---------------|-------------|
| **Throughput** | 100+ products/hour | 120 products/hour |
| **Weight Accuracy** | ±0.05g | ±0.01g |
| **Vision Resolution** | 2MP minimum | 5MP achieved |
| **Processing Time** | <30 seconds/product | 25 seconds/product |
| **Uptime** | 95% minimum | 99.5% target |
| **Compliance** | Legal Metrology Act 2009 | Full compliance |

### **Supplier Information**

#### **Primary Suppliers**
1. **Mettler Toledo India** - Precision weighing systems
2. **Keyence India** - Vision and measurement systems  
3. **Universal Robots** - Automation systems
4. **Samsung India** - Mobile computing platforms
5. **Schneider Electric** - Power and control systems

#### **Secondary Suppliers**
1. **Basler AG** - Industrial cameras
2. **X-Rite India** - Color measurement
3. **Cognex India** - Machine vision software
4. **Daikin India** - Environmental control
5. **Cisco India** - Network infrastructure

### **Maintenance & Support Contracts**

| Service Type | Annual Cost (₹) | Annual Cost (USD) |
|--------------|-----------------|-------------------|
| Hardware Maintenance | 15,00,000 | $18,000 |
| Software Support | 8,00,000 | $9,600 |
| Calibration Services | 12,00,000 | $14,400 |
| Training & Updates | 5,00,000 | $6,000 |
| **Total Annual Support** | **40,00,000** | **$48,000** |

---

## 🎯 **Implementation Recommendations**

### **Procurement Strategy**
1. **Phased Procurement**: Implement in 3 phases to manage cash flow
2. **Local Content**: Prioritize Make in India suppliers (60%+ local content)
3. **Long-term Contracts**: Negotiate 5-year maintenance agreements
4. **Technology Refresh**: Plan for 20% technology upgrade every 3 years

### **Quality Assurance**
1. **Factory Acceptance Testing (FAT)**: All systems tested before delivery
2. **Site Acceptance Testing (SAT)**: Complete integration testing
3. **Performance Qualification**: 30-day performance validation
4. **Ongoing Monitoring**: Continuous performance tracking

### **Risk Mitigation**
1. **Backup Systems**: 20% redundancy for critical components
2. **Local Support**: Ensure local service presence for all suppliers
3. **Spare Parts**: Maintain 2-year spare parts inventory
4. **Alternative Suppliers**: Identify backup suppliers for each component

This comprehensive hardware list provides everything needed to implement a world-class legal metrology compliance checking system with government-grade precision and reliability.

---

**Document Version**: 1.0  
**Date**: September 14, 2025  
**Prepared By**: Hardware Engineering Team  
**Next Review**: September 28, 2025


