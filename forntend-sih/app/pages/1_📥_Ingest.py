import streamlit as st
from pathlib import Path
from core.ocr import image_to_text, is_tesseract_available
from core.auth import require_auth, get_current_user
from core.audit_logger import log_user_action
from core.barcode_scanner import get_barcode_scanner
from PIL import Image
import os

# Require authentication
require_auth()
current_user = get_current_user()

st.title("📥 Ingest Listings")

st.info("Upload images (labels/pack shots), **scan barcodes**, or paste product description text. You can process multiple files at once for bulk validation.")

os.makedirs("app/data/uploads", exist_ok=True)

# Add tabs for different input methods
tab1, tab2, tab3 = st.tabs(["📸 Image Upload", "📷 Barcode Scanner", "📝 Text Input"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 Image Upload")
    img_files = st.file_uploader(
        "Upload product images (PNG/JPG)", 
        type=["png","jpg","jpeg"],
        accept_multiple_files=True,
        help="You can upload multiple images at once for bulk processing"
    )
    
    if img_files:
        base = Path("app/data/uploads")
        base.mkdir(parents=True, exist_ok=True)
        
        if len(img_files) > 1:
            st.info(f"Processing {len(img_files)} images...")
        
        for img_file in img_files:
            with st.spinner(f"Processing {img_file.name}..."):
                img_bytes = img_file.read()
                text, boxes = ("", [])
                if is_tesseract_available():
                    text, boxes = image_to_text(img_bytes)
                else:
                    st.warning("Tesseract OCR not found. Install Tesseract to enable image OCR.")
                
                # Save text to a simple file in uploads
                out_txt = base / f"{Path(img_file.name).stem}.txt"
                out_txt.write_text(text or "")
                st.success(f"✅ {img_file.name} → {out_txt.name}")
                
                # Log the action
                log_user_action(
                    current_user.username,
                    "FILE_UPLOAD",
                    f"image:{img_file.name}",
                    {"file_size": len(img_bytes), "ocr_text_length": len(text or "")}
                )
        
        if len(img_files) == 1 and text:
            st.text_area("OCR Text (preview)", text, height=200)

with col2:
    manual_text = st.text_area("Or paste product description / listing text", height=260, placeholder="Paste product text here…\nExample: MRP: ₹199, Net Quantity: 500 g, Manufactured by: …, Country of Origin: India")    
    if st.button("Save Text"):
        if manual_text.strip():
            base = Path("app/data/uploads")
            base.mkdir(parents=True, exist_ok=True)
            idx = len(list(base.glob("manual_*.txt"))) + 1
            p = base / f"manual_{idx}.txt"
            p.write_text(manual_text)
            st.success(f"Saved to {p}")
            
            # Log the action
            log_user_action(
                current_user.username,
                "TEXT_UPLOAD",
                f"manual_text:{p.name}",
                {"text_length": len(manual_text)}
            )
        else:
            st.warning("Nothing to save. Paste some text first.")

with tab2:
    st.subheader("📷 Barcode Scanner")
    st.info("Scan product barcodes to automatically fetch product information and compliance data.")
    
    scanner = get_barcode_scanner()
    
    # Barcode scanning options
    scan_col1, scan_col2 = st.columns(2)
    
    with scan_col1:
        st.markdown("**Upload Barcode Image:**")
        barcode_image = st.file_uploader(
            "Choose an image with barcode",
            type=['png', 'jpg', 'jpeg'],
            key="barcode_upload"
        )
        
        if barcode_image is not None:
            image = Image.open(barcode_image)
            st.image(image, caption="Barcode Image", width=200)
            
            if st.button("🔍 Scan Barcode", type="primary"):
                with st.spinner("Scanning barcode..."):
                    # Extract barcodes from image
                    barcodes = scanner.scan_barcode_from_image(image)
                    
                    if barcodes:
                        st.success(f"Found barcode: {barcodes[0]}")
                        
                        # Look up product data
                        barcode_data = scanner.lookup_barcode(barcodes[0])
                        
                        if barcode_data:
                            # Extract compliance fields
                            compliance_fields = scanner.extract_compliance_fields(barcode_data)
                            
                            # Create text content for saving
                            product_text = f"""Product Name: {compliance_fields.get('product_name', '')}
Brand: {compliance_fields.get('brand_name', '')}
Manufacturer: {compliance_fields.get('manufacturer_name', '')}
MRP: {compliance_fields.get('mrp_raw', '')}
Net Quantity: {compliance_fields.get('net_quantity_raw', '')}
Country of Origin: {compliance_fields.get('country_of_origin', '')}
Category: {compliance_fields.get('category', '')}
Barcode: {barcode_data.barcode}
Data Source: {barcode_data.source_api}
Confidence: {compliance_fields.get('confidence_score', 0):.1f}%"""
                            
                            # Save to uploads
                            base = Path("app/data/uploads")
                            base.mkdir(parents=True, exist_ok=True)
                            barcode_file = base / f"barcode_{barcode_data.barcode}.txt"
                            barcode_file.write_text(product_text)
                            
                            st.success(f"✅ Product data saved to {barcode_file.name}")
                            st.text_area("Product Information", product_text, height=200)
                            
                            # Log the action
                            log_user_action(
                                current_user.username,
                                "BARCODE_SCAN",
                                f"barcode_scan:{barcode_file.name}",
                                {"barcode": barcode_data.barcode, "source": barcode_data.source_api}
                            )
                        else:
                            st.warning("Product not found in barcode databases")
                    else:
                        st.error("No barcode detected in image")
    
    with scan_col2:
        st.markdown("**Manual Barcode Entry:**")
        manual_barcode = st.text_input(
            "Enter barcode number",
            placeholder="Enter 8, 12, or 13 digit barcode",
            key="manual_barcode"
        )
        
        if st.button("🔍 Look Up Barcode", disabled=not manual_barcode):
            if manual_barcode:
                # Validate barcode
                is_valid, validation_msg = scanner.validate_barcode(manual_barcode)
                
                if is_valid:
                    with st.spinner(f"Looking up {manual_barcode}..."):
                        barcode_data = scanner.lookup_barcode(manual_barcode)
                        
                        if barcode_data:
                            # Extract compliance fields
                            compliance_fields = scanner.extract_compliance_fields(barcode_data)
                            
                            # Create text content for saving
                            product_text = f"""Product Name: {compliance_fields.get('product_name', '')}
Brand: {compliance_fields.get('brand_name', '')}
Manufacturer: {compliance_fields.get('manufacturer_name', '')}
MRP: {compliance_fields.get('mrp_raw', '')}
Net Quantity: {compliance_fields.get('net_quantity_raw', '')}
Country of Origin: {compliance_fields.get('country_of_origin', '')}
Category: {compliance_fields.get('category', '')}
Barcode: {barcode_data.barcode}
Data Source: {barcode_data.source_api}
Confidence: {compliance_fields.get('confidence_score', 0):.1f}%"""
                            
                            # Save to uploads
                            base = Path("app/data/uploads")
                            base.mkdir(parents=True, exist_ok=True)
                            barcode_file = base / f"barcode_{barcode_data.barcode}.txt"
                            barcode_file.write_text(product_text)
                            
                            st.success(f"✅ Product data saved to {barcode_file.name}")
                            st.text_area("Product Information", product_text, height=200, key="manual_product_info")
                            
                            # Log the action
                            log_user_action(
                                current_user.username,
                                "BARCODE_LOOKUP",
                                f"barcode_lookup:{barcode_file.name}",
                                {"barcode": barcode_data.barcode, "source": barcode_data.source_api}
                            )
                        else:
                            st.warning("Product not found in barcode databases")
                else:
                    st.error(f"Invalid barcode: {validation_msg}")

with tab3:
    st.subheader("📝 Text Input")
    manual_text_tab3 = st.text_area(
        "Paste product description / listing text", 
        height=260, 
        placeholder="Paste product text here…\nExample: MRP: ₹199, Net Quantity: 500 g, Manufactured by: …, Country of Origin: India",
        key="manual_text_tab3"
    )    
    if st.button("Save Text", key="save_text_tab3"):
        if manual_text_tab3.strip():
            base = Path("app/data/uploads")
            base.mkdir(parents=True, exist_ok=True)
            idx = len(list(base.glob("manual_*.txt"))) + 1
            p = base / f"manual_{idx}.txt"
            p.write_text(manual_text_tab3)
            st.success(f"Saved to {p}")
            
            # Log the action
            log_user_action(
                current_user.username,
                "TEXT_UPLOAD",
                f"manual_text:{p.name}",
                {"text_length": len(manual_text_tab3)}
            )
        else:
            st.warning("Nothing to save. Paste some text first.")

st.caption("Saved files are placed under `app/data/uploads`. They will be used by the next pages.")
