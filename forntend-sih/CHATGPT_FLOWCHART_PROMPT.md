# ChatGPT Prompt for Legal Metrology Compliance Checker Flowchart

## PROMPT FOR CHATGPT:

---

**Create a comprehensive, professional flowchart for a Legal Metrology Compliance Checker system. This is a production-grade enterprise application with multiple integrated components. Please create a detailed flowchart that shows the complete data flow from input to output.**

## SYSTEM OVERVIEW:
This is a Streamlit-based Legal Metrology Compliance Checker for India's regulatory requirements. It processes product data through multiple stages of validation, approval workflows, and physical system integration.

## DETAILED COMPONENT BREAKDOWN:

### 1. **INPUT STAGE - Data Ingestion**
**Components:**
- **Authentication System**: Role-based access (Admin, Manager, Validator, User)
- **Ingest Page**: 3 input methods
  - 📸 Image Upload → Tesseract OCR processing
  - 📷 Barcode Scanner → Multi-API lookup (Open Food Facts, UPC Item DB, Barcode Lookup)
  - 📝 Manual Text Entry
- **File Storage**: Saves to `app/data/uploads/*.txt`
- **Audit Logger**: Records all user actions with timestamps

### 2. **EXTRACTION STAGE - NLP Processing**
**Components:**
- **NLP Extract Engine** (`core/nlp_extract.py`)
- **Pattern Matching**: Uses regex patterns for:
  - MRP: `₹`, `RS.`, `MRP:`, `Price:` patterns
  - Quantity: `net quantity`, `weight`, `volume` with units (g, kg, ml, l)
  - Dates: Manufacturing/expiry date patterns
  - Manufacturer: `manufactured by`, `mfg. by`, `company` patterns
  - Origin: `country of origin` patterns
- **Data Cleaning & Validation**:
  - Date format validation
  - Manufacturer name cleaning
  - Unit standardization
- **Confidence Scoring**: 0-100% based on extracted field completeness
- **AI Assistant Integration**: Provides intelligent suggestions

### 3. **VALIDATION STAGE - Rules Engine**
**Components:**
- **Rules Engine** (`core/rules_engine.py`)
- **YAML Rules**: Loads from `legal_metrology_rules.yaml`
- **Multi-Level Validation**:
  - Required fields check (MRP, net quantity, manufacturer, etc.)
  - Value validation (min/max MRP, allowed units, quantity ranges)
  - Format validation (currency symbols, date formats)
  - Font size validation using OCR boxes
- **Compliance Scoring**:
  - Base: 100 points
  - Deductions: -20 for errors, -5 for warnings
- **Issue Classification**: ERROR, WARN, INFO levels
- **Report Generation**: Saves to `app/data/reports/validated.jsonl`

### 4. **ERP INTEGRATION STAGE - Product Management**
**Components:**
- **ERP Manager** (`core/erp_manager.py`)
- **Product Data Model**: Complete product lifecycle management
- **Auto SKU Generation**: Timestamp-based unique IDs
- **Status Tracking**: Draft → Submitted → Under Review → Compliant → Approved → Dispatched
- **Category Management**: Food, Beverages, Cosmetics, Pharmaceuticals, etc.
- **Version Control**: Complete change tracking with user attribution

### 5. **WORKFLOW MANAGEMENT STAGE - Approval Process**
**Components:**
- **Workflow Manager** (`core/workflow_manager.py`)
- **Multi-Level Approval System**: 4-level approval process
  - Level 1: Validator (Data Validation)
  - Level 2: Compliance Officer (Compliance Check)
  - Level 3: Manager (Manager Approval)
  - Level 4: Admin (Final Approval)
- **Workflow Types**:
  - Product Approval
  - Compliance Review
  - Label Generation
  - Dispatch Approval
- **Role-Based Assignment**: Automatic step assignment based on user roles
- **Audit Trail**: Complete workflow history with timestamps

### 6. **LABEL GENERATION STAGE - Pre-Print Compliance Gate**
**Components:**
- **Label Generator** (`core/label_generator.py`)
- **Compliant Label Design**: Ensures all mandatory elements
- **Multiple Formats**: Standard, Premium, Minimal, Detailed, Multilingual
- **Pre-Print Validation**: Final compliance check before printing
- **Visual Preview**: Generated label images with compliance status

### 7. **PHYSICAL INTEGRATION STAGE - System Integration**
**Components:**
- **Physical Integration** (`core/physical_integration.py`)
- **Device Management**: Printer and vision system control
- **Print Operations**: Automated printing with quality control
- **Vision Inspection**: Post-print compliance verification
- **Quality Assurance**: Defect detection and handling

### 8. **REPORTING & ANALYTICS STAGE - Final Output**
**Components:**
- **Dashboard System**: Real-time analytics and metrics
- **Report Generator**: Multiple export formats (JSON, CSV, PDF)
- **System Monitor**: Performance and health monitoring
- **Audit Records**: Complete traceability documentation

## ADDITIONAL INTEGRATIONS:

### **AI Assistant** (`core/chatbot.py`):
- RAG Integration for intelligent suggestions
- Context-aware compliance guidance
- Real-time analysis of extraction and validation results

### **Barcode Scanner** (`core/barcode_scanner.py`):
- Multi-API integration (3 different barcode APIs)
- Computer vision processing (OpenCV + pyzbar)
- Automatic product data extraction and mapping

### **Web Crawler** (`core/web_crawler.py`):
- E-commerce data acquisition
- Automated compliance checking of online listings
- Bulk processing capabilities

## QUALITY GATES & CONTROL POINTS:
1. **🔐 Authentication Gate**: Role-based access control
2. **📋 Extraction Gate**: Confidence scoring (80%+ = high, 60-80% = medium, <60% = low)
3. **✅ Compliance Gate**: Rules engine validation (100-point scoring system)
4. **🔄 Approval Gate**: Multi-level workflow approvals (4 levels)
5. **🏷️ Pre-Print Gate**: Label compliance verification
6. **👁️ Vision Gate**: Post-print quality inspection
7. **📊 Audit Gate**: Complete traceability and reporting

## FLOWCHART REQUIREMENTS:

### **Visual Style:**
- Use professional, modern design with clear icons
- Color coding: Green for compliant/approved, Red for non-compliant/blocked, Orange for pending/review, Blue for processing
- Include decision diamonds for quality gates
- Show parallel processing paths where applicable
- Use different shapes for different component types (rectangles for processes, diamonds for decisions, cylinders for data storage)

### **Detail Level:**
- Show main data flow with thick arrows
- Include feedback loops and error handling paths
- Display all major components and their connections
- Show data transformation at each stage
- Include quality gates and approval checkpoints

### **Technical Accuracy:**
- Reflect the actual component architecture
- Show proper data flow directions
- Include all major processing stages
- Display integration points between components
- Show audit logging touchpoints

### **Layout:**
- Left-to-right or top-to-bottom flow
- Group related components visually
- Show clear stage boundaries
- Include legend for symbols and colors
- Ensure readability at different zoom levels

## KEY DATA TRANSFORMATIONS TO HIGHLIGHT:
1. **Raw Input** → **Structured Text** (OCR/Barcode/Manual)
2. **Structured Text** → **Extracted Fields** (NLP + Pattern Matching)
3. **Extracted Fields** → **Validated Data** (Rules Engine + Compliance)
4. **Validated Data** → **ERP Records** (Product Management + Status)
5. **ERP Records** → **Approved Products** (Workflow + Multi-level Approval)
6. **Approved Products** → **Compliant Labels** (Label Generation + Pre-print Gate)
7. **Compliant Labels** → **Physical Products** (Printing + Vision Inspection)
8. **Physical Products** → **Audit Records** (Reports + Compliance Documentation)

## SPECIAL REQUIREMENTS:
- Show error handling and non-compliant data paths
- Include regulatory update feedback loops
- Display system monitoring and health checks
- Show user role interactions at each stage
- Include external API integrations (barcode APIs, etc.)

**Please create a comprehensive, professional flowchart that captures all these components and their interactions. The flowchart should be suitable for technical documentation and executive presentations. Focus on clarity, completeness, and visual appeal.**

---

## ALTERNATIVE SIMPLIFIED VERSION PROMPT:

If you need a simpler version, use this condensed prompt:

**"Create a professional flowchart for a Legal Metrology Compliance Checker system showing: Input Stage (Image OCR, Barcode Scan, Manual Text) → Extraction Stage (NLP Field Extraction with confidence scoring) → Validation Stage (Rules Engine with compliance scoring) → ERP Integration (Product management with status tracking) → Workflow Management (4-level approval process) → Label Generation (Pre-print compliance gate) → Physical Integration (Printing + Vision inspection) → Reports & Analytics. Include quality gates, error handling, and audit logging throughout. Use professional colors and modern design."**
