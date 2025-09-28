"""
Enhanced Computer Vision and Image Recognition for Legal Metrology
Advanced image processing, label region detection, and multi-language OCR support
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from typing import List, Tuple, Dict, Optional, Any
import logging
import re
import json
from pathlib import Path
from dataclasses import dataclass
import easyocr
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage import measure, morphology, segmentation
from scipy import ndimage
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class LabelRegion:
    """Represents a detected label region in an image"""
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    text_density: float
    region_type: str  # 'nutrition', 'ingredients', 'legal_info', 'branding'
    extracted_text: str = ""
    language: str = "en"
    
class EnhancedVisionProcessor:
    """Advanced computer vision processor for Legal Metrology compliance"""
    
    def __init__(self):
        """Initialize the enhanced vision processor"""
        
        # OCR engines configuration
        self.ocr_engines = {
            'tesseract': {
                'languages': ['eng', 'hin', 'ben', 'guj', 'kan', 'mal', 'mar', 'ori', 'pan', 'tam', 'tel'],
                'config': '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz₹.,():-/% '
            },
            'easyocr': {
                'languages': ['en', 'hi', 'bn', 'gu', 'kn', 'ml', 'mr', 'or', 'pa', 'ta', 'te'],
                'gpu': False
            }
        }
        
        # Initialize EasyOCR reader
        try:
            self.easyocr_reader = easyocr.Reader(
                self.ocr_engines['easyocr']['languages'], 
                gpu=self.ocr_engines['easyocr']['gpu']
            )
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
            self.easyocr_reader = None
        
        # Label region detection models
        self.region_classifiers = {
            'nutrition_facts': {
                'keywords': ['nutrition', 'facts', 'calories', 'protein', 'carbohydrates', 'fat', 'sodium'],
                'patterns': [r'\d+\s*g', r'\d+\s*mg', r'\d+\s*kcal', r'per\s+\d+g']
            },
            'ingredients': {
                'keywords': ['ingredients', 'contains', 'made with', 'composition'],
                'patterns': [r'[A-Za-z\s]+,\s*[A-Za-z\s]+', r'\([^)]*\)']
            },
            'legal_info': {
                'keywords': ['mrp', 'mfg', 'exp', 'batch', 'net wt', 'net weight', 'manufacturer', 'packed by'],
                'patterns': [r'₹\s*\d+', r'mfg[:\s]*\d{2}[/-]\d{2}[/-]\d{4}', r'exp[:\s]*\d{2}[/-]\d{2}[/-]\d{4}']
            },
            'branding': {
                'keywords': ['brand', 'logo', 'trademark', 'company'],
                'patterns': [r'®', r'™', r'©']
            }
        }
        
        logger.info("EnhancedVisionProcessor initialized with multi-language OCR support")
    
    def preprocess_image(self, image: np.ndarray, enhancement_type: str = 'auto') -> np.ndarray:
        """
        Advanced image preprocessing for better OCR accuracy
        
        Args:
            image: Input image as numpy array
            enhancement_type: Type of enhancement ('auto', 'contrast', 'brightness', 'sharpness', 'denoising')
        
        Returns:
            Preprocessed image
        """
        try:
            # Convert to PIL for easier manipulation
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = image
            
            # Auto enhancement based on image analysis
            if enhancement_type == 'auto':
                enhancement_type = self._analyze_image_quality(pil_image)
            
            # Apply specific enhancements
            if enhancement_type == 'contrast':
                enhancer = ImageEnhance.Contrast(pil_image)
                pil_image = enhancer.enhance(1.5)
            
            elif enhancement_type == 'brightness':
                enhancer = ImageEnhance.Brightness(pil_image)
                pil_image = enhancer.enhance(1.2)
            
            elif enhancement_type == 'sharpness':
                enhancer = ImageEnhance.Sharpness(pil_image)
                pil_image = enhancer.enhance(2.0)
            
            elif enhancement_type == 'denoising':
                # Convert back to OpenCV for denoising
                cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                cv_image = cv2.fastNlMeansDenoisingColored(cv_image, None, 10, 10, 7, 21)
                pil_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            # Additional processing
            pil_image = pil_image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            
            # Convert back to OpenCV format
            processed_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            logger.debug(f"Applied {enhancement_type} enhancement to image")
            return processed_image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image
    
    def _analyze_image_quality(self, image: Image.Image) -> str:
        """Analyze image quality and recommend enhancement type"""
        try:
            # Convert to grayscale for analysis
            gray = image.convert('L')
            img_array = np.array(gray)
            
            # Calculate various metrics
            mean_brightness = np.mean(img_array)
            std_brightness = np.std(img_array)
            
            # Determine best enhancement
            if mean_brightness < 80:
                return 'brightness'
            elif std_brightness < 30:
                return 'contrast'
            elif self._calculate_blur_metric(img_array) > 100:
                return 'sharpness'
            else:
                return 'denoising'
                
        except Exception:
            return 'contrast'
    
    def _calculate_blur_metric(self, image: np.ndarray) -> float:
        """Calculate blur metric using Laplacian variance"""
        return cv2.Laplacian(image, cv2.CV_64F).var()
    
    def detect_label_regions(self, image: np.ndarray) -> List[LabelRegion]:
        """
        Detect and classify different label regions in product packaging
        
        Args:
            image: Input image as numpy array
        
        Returns:
            List of detected label regions
        """
        try:
            regions = []
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            gray = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            
            # Text region detection using MSER (Maximally Stable Extremal Regions)
            mser = cv2.MSER_create()
            regions_mser, _ = mser.detectRegions(gray)
            
            # Convert MSER regions to bounding boxes
            text_regions = []
            for region in regions_mser:
                if len(region) > 50:  # Filter small regions
                    x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))
                    
                    # Filter by aspect ratio and size
                    if w > 20 and h > 10 and w/h < 10 and h/w < 5:
                        text_regions.append((x, y, w, h))
            
            # Merge nearby regions
            merged_regions = self._merge_nearby_regions(text_regions)
            
            # Extract text from each region and classify
            for bbox in merged_regions:
                x, y, w, h = bbox
                region_image = processed_image[y:y+h, x:x+w]
                
                # Extract text using multiple OCR engines
                extracted_text = self._extract_text_multi_engine(region_image)
                
                if extracted_text.strip():
                    # Classify region type
                    region_type = self._classify_region_type(extracted_text)
                    
                    # Calculate confidence and text density
                    confidence = self._calculate_region_confidence(region_image, extracted_text)
                    text_density = len(extracted_text.strip()) / (w * h) * 1000
                    
                    # Detect language
                    language = self._detect_language(extracted_text)
                    
                    region = LabelRegion(
                        bbox=bbox,
                        confidence=confidence,
                        text_density=text_density,
                        region_type=region_type,
                        extracted_text=extracted_text,
                        language=language
                    )
                    regions.append(region)
            
            logger.info(f"Detected {len(regions)} label regions")
            return regions
            
        except Exception as e:
            logger.error(f"Label region detection failed: {e}")
            return []
    
    def _merge_nearby_regions(self, regions: List[Tuple[int, int, int, int]], 
                            threshold: int = 20) -> List[Tuple[int, int, int, int]]:
        """Merge nearby text regions"""
        if not regions:
            return []
        
        merged = []
        regions = sorted(regions, key=lambda x: (x[1], x[0]))  # Sort by y, then x
        
        current_group = [regions[0]]
        
        for region in regions[1:]:
            x, y, w, h = region
            
            # Check if region is close to any region in current group
            should_merge = False
            for group_region in current_group:
                gx, gy, gw, gh = group_region
                
                # Check vertical proximity
                if abs(y - (gy + gh)) < threshold or abs(gy - (y + h)) < threshold:
                    # Check horizontal overlap or proximity
                    if (x < gx + gw + threshold and gx < x + w + threshold):
                        should_merge = True
                        break
            
            if should_merge:
                current_group.append(region)
            else:
                # Merge current group and start new group
                if current_group:
                    merged_bbox = self._merge_bboxes(current_group)
                    merged.append(merged_bbox)
                current_group = [region]
        
        # Don't forget the last group
        if current_group:
            merged_bbox = self._merge_bboxes(current_group)
            merged.append(merged_bbox)
        
        return merged
    
    def _merge_bboxes(self, bboxes: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
        """Merge multiple bounding boxes into one"""
        if not bboxes:
            return (0, 0, 0, 0)
        
        min_x = min(bbox[0] for bbox in bboxes)
        min_y = min(bbox[1] for bbox in bboxes)
        max_x = max(bbox[0] + bbox[2] for bbox in bboxes)
        max_y = max(bbox[1] + bbox[3] for bbox in bboxes)
        
        return (min_x, min_y, max_x - min_x, max_y - min_y)
    
    def _extract_text_multi_engine(self, image: np.ndarray) -> str:
        """Extract text using multiple OCR engines and return best result"""
        results = []
        
        # Tesseract OCR
        try:
            tesseract_config = self.ocr_engines['tesseract']['config']
            tesseract_text = pytesseract.image_to_string(image, config=tesseract_config)
            if tesseract_text.strip():
                results.append(('tesseract', tesseract_text.strip()))
        except Exception as e:
            logger.debug(f"Tesseract OCR failed: {e}")
        
        # EasyOCR
        if self.easyocr_reader:
            try:
                easyocr_results = self.easyocr_reader.readtext(image)
                easyocr_text = ' '.join([result[1] for result in easyocr_results if result[2] > 0.5])
                if easyocr_text.strip():
                    results.append(('easyocr', easyocr_text.strip()))
            except Exception as e:
                logger.debug(f"EasyOCR failed: {e}")
        
        # Return the longest result (usually more accurate)
        if results:
            best_result = max(results, key=lambda x: len(x[1]))
            return best_result[1]
        
        return ""
    
    def _classify_region_type(self, text: str) -> str:
        """Classify the type of label region based on extracted text"""
        text_lower = text.lower()
        
        # Score each region type
        scores = {}
        
        for region_type, config in self.region_classifiers.items():
            score = 0
            
            # Keyword matching
            for keyword in config['keywords']:
                if keyword in text_lower:
                    score += 2
            
            # Pattern matching
            for pattern in config['patterns']:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches)
            
            scores[region_type] = score
        
        # Return the region type with highest score
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            if best_type[1] > 0:
                return best_type[0]
        
        return 'general'
    
    def _calculate_region_confidence(self, image: np.ndarray, text: str) -> float:
        """Calculate confidence score for a region based on image quality and text"""
        try:
            # Image quality metrics
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Blur detection
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_confidence = min(blur_score / 100, 1.0)
            
            # Contrast
            contrast = gray.std()
            contrast_confidence = min(contrast / 50, 1.0)
            
            # Text quality metrics
            text_length_confidence = min(len(text.strip()) / 20, 1.0)
            
            # Combine confidences
            overall_confidence = (blur_confidence + contrast_confidence + text_length_confidence) / 3
            
            return min(max(overall_confidence, 0.0), 1.0)
            
        except Exception:
            return 0.5
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of extracted text"""
        try:
            # Simple language detection based on character patterns
            if re.search(r'[\u0900-\u097F]', text):  # Devanagari (Hindi)
                return 'hi'
            elif re.search(r'[\u0980-\u09FF]', text):  # Bengali
                return 'bn'
            elif re.search(r'[\u0A80-\u0AFF]', text):  # Gujarati
                return 'gu'
            elif re.search(r'[\u0C80-\u0CFF]', text):  # Kannada
                return 'kn'
            elif re.search(r'[\u0D00-\u0D7F]', text):  # Malayalam
                return 'ml'
            elif re.search(r'[\u0B80-\u0BFF]', text):  # Tamil
                return 'ta'
            elif re.search(r'[\u0C00-\u0C7F]', text):  # Telugu
                return 'te'
            else:
                return 'en'  # Default to English
                
        except Exception:
            return 'en'
    
    def segment_packaging_declarations(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Advanced segmentation of packaging declarations using computer vision
        
        Args:
            image: Input product image
        
        Returns:
            Dictionary containing segmented declarations and metadata
        """
        try:
            # Detect label regions
            regions = self.detect_label_regions(image)
            
            # Group regions by type
            segmented_declarations = {
                'nutrition_facts': [],
                'ingredients': [],
                'legal_info': [],
                'branding': [],
                'general': []
            }
            
            for region in regions:
                segmented_declarations[region.region_type].append({
                    'bbox': region.bbox,
                    'text': region.extracted_text,
                    'confidence': region.confidence,
                    'language': region.language,
                    'text_density': region.text_density
                })
            
            # Extract specific Legal Metrology fields
            legal_metrology_fields = self._extract_legal_metrology_fields(regions)
            
            # Generate processing metadata
            metadata = {
                'total_regions': len(regions),
                'processing_timestamp': pd.Timestamp.now().isoformat(),
                'image_dimensions': image.shape[:2],
                'detected_languages': list(set(r.language for r in regions)),
                'average_confidence': np.mean([r.confidence for r in regions]) if regions else 0.0
            }
            
            return {
                'segmented_declarations': segmented_declarations,
                'legal_metrology_fields': legal_metrology_fields,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Packaging declaration segmentation failed: {e}")
            return {
                'segmented_declarations': {},
                'legal_metrology_fields': {},
                'metadata': {'error': str(e)}
            }
    
    def _extract_legal_metrology_fields(self, regions: List[LabelRegion]) -> Dict[str, Any]:
        """Extract specific Legal Metrology fields from detected regions"""
        fields = {
            'mrp': None,
            'net_quantity': None,
            'manufacturer': None,
            'mfg_date': None,
            'exp_date': None,
            'batch_number': None,
            'country_of_origin': None,
            'fssai_license': None
        }
        
        # Combine all text from legal_info regions
        legal_text = ""
        for region in regions:
            if region.region_type == 'legal_info':
                legal_text += " " + region.extracted_text
        
        # If no specific legal_info regions, use all text
        if not legal_text.strip():
            legal_text = " ".join(region.extracted_text for region in regions)
        
        # Extract MRP
        mrp_patterns = [
            r'mrp[:\s]*₹?\s*(\d+(?:\.\d{2})?)',
            r'₹\s*(\d+(?:\.\d{2})?)',
            r'price[:\s]*₹?\s*(\d+(?:\.\d{2})?)',
            r'rs\.?\s*(\d+(?:\.\d{2})?)'
        ]
        
        for pattern in mrp_patterns:
            match = re.search(pattern, legal_text, re.IGNORECASE)
            if match:
                try:
                    fields['mrp'] = float(match.group(1))
                    break
                except ValueError:
                    continue
        
        # Extract Net Quantity
        qty_patterns = [
            r'net\s+(?:wt|weight|qty|quantity)[:\s]*(\d+(?:\.\d+)?)\s*(g|kg|ml|l|gm|gms|ltr|litre)',
            r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l|gm|gms|ltr|litre)(?:\s+net)?',
            r'weight[:\s]*(\d+(?:\.\d+)?)\s*(g|kg|ml|l|gm|gms|ltr|litre)'
        ]
        
        for pattern in qty_patterns:
            match = re.search(pattern, legal_text, re.IGNORECASE)
            if match:
                fields['net_quantity'] = f"{match.group(1)} {match.group(2)}"
                break
        
        # Extract Manufacturing Date
        mfg_patterns = [
            r'mfg[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'manufactured[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'mfd[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in mfg_patterns:
            match = re.search(pattern, legal_text, re.IGNORECASE)
            if match:
                fields['mfg_date'] = match.group(1)
                break
        
        # Extract Expiry Date
        exp_patterns = [
            r'exp[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'expiry[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'best\s+before[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, legal_text, re.IGNORECASE)
            if match:
                fields['exp_date'] = match.group(1)
                break
        
        # Extract Batch Number
        batch_patterns = [
            r'batch[:\s]*([A-Z0-9]+)',
            r'lot[:\s]*([A-Z0-9]+)',
            r'b[:\s]*([A-Z0-9]+)'
        ]
        
        for pattern in batch_patterns:
            match = re.search(pattern, legal_text, re.IGNORECASE)
            if match:
                fields['batch_number'] = match.group(1)
                break
        
        # Extract Manufacturer
        mfr_patterns = [
            r'mfr[:\s]*([^,\n]+)',
            r'manufactured\s+by[:\s]*([^,\n]+)',
            r'manufacturer[:\s]*([^,\n]+)'
        ]
        
        for pattern in mfr_patterns:
            match = re.search(pattern, legal_text, re.IGNORECASE)
            if match:
                fields['manufacturer'] = match.group(1).strip()
                break
        
        # Extract Country of Origin
        origin_patterns = [
            r'country\s+of\s+origin[:\s]*([^,\n]+)',
            r'origin[:\s]*([^,\n]+)',
            r'made\s+in[:\s]*([^,\n]+)'
        ]
        
        for pattern in origin_patterns:
            match = re.search(pattern, legal_text, re.IGNORECASE)
            if match:
                fields['country_of_origin'] = match.group(1).strip()
                break
        
        # Extract FSSAI License
        fssai_patterns = [
            r'fssai[:\s]*([0-9]{14})',
            r'lic[:\s]*no[:\s]*([0-9]{14})',
            r'license[:\s]*([0-9]{14})'
        ]
        
        for pattern in fssai_patterns:
            match = re.search(pattern, legal_text, re.IGNORECASE)
            if match:
                fields['fssai_license'] = match.group(1)
                break
        
        return fields
    
    def visualize_detected_regions(self, image: np.ndarray, regions: List[LabelRegion], 
                                 save_path: Optional[str] = None) -> np.ndarray:
        """
        Visualize detected label regions on the image
        
        Args:
            image: Original image
            regions: Detected label regions
            save_path: Optional path to save the visualization
        
        Returns:
            Image with visualized regions
        """
        try:
            # Create a copy of the image for visualization
            vis_image = image.copy()
            
            # Color map for different region types
            color_map = {
                'nutrition_facts': (0, 255, 0),      # Green
                'ingredients': (255, 0, 0),          # Blue
                'legal_info': (0, 0, 255),           # Red
                'branding': (255, 255, 0),           # Cyan
                'general': (128, 128, 128)           # Gray
            }
            
            # Draw bounding boxes and labels
            for i, region in enumerate(regions):
                x, y, w, h = region.bbox
                color = color_map.get(region.region_type, (128, 128, 128))
                
                # Draw bounding box
                cv2.rectangle(vis_image, (x, y), (x + w, y + h), color, 2)
                
                # Add label
                label = f"{region.region_type} ({region.confidence:.2f})"
                cv2.putText(vis_image, label, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                # Add region number
                cv2.putText(vis_image, str(i + 1), (x + 5, y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Save if path provided
            if save_path:
                cv2.imwrite(save_path, vis_image)
                logger.info(f"Visualization saved to {save_path}")
            
            return vis_image
            
        except Exception as e:
            logger.error(f"Region visualization failed: {e}")
            return image
    
    def batch_process_images(self, image_paths: List[str], 
                           output_dir: str = "app/data/processed") -> List[Dict[str, Any]]:
        """
        Batch process multiple images for label region detection and text extraction
        
        Args:
            image_paths: List of paths to images
            output_dir: Directory to save results
        
        Returns:
            List of processing results
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            results = []
            
            for i, image_path in enumerate(image_paths):
                logger.info(f"Processing image {i+1}/{len(image_paths)}: {image_path}")
                
                try:
                    # Load image
                    image = cv2.imread(image_path)
                    if image is None:
                        logger.warning(f"Could not load image: {image_path}")
                        continue
                    
                    # Process image
                    result = self.segment_packaging_declarations(image)
                    result['image_path'] = image_path
                    result['image_name'] = Path(image_path).name
                    
                    # Detect regions for visualization
                    regions = self.detect_label_regions(image)
                    
                    # Save visualization
                    vis_path = output_path / f"visualization_{Path(image_path).stem}.jpg"
                    self.visualize_detected_regions(image, regions, str(vis_path))
                    result['visualization_path'] = str(vis_path)
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Failed to process {image_path}: {e}")
                    results.append({
                        'image_path': image_path,
                        'error': str(e)
                    })
            
            # Save batch results
            results_path = output_path / f"batch_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Batch processing completed. Results saved to {results_path}")
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return []
    
    def get_processing_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics from batch processing results"""
        try:
            if not results:
                return {}
            
            # Filter successful results
            successful_results = [r for r in results if 'error' not in r]
            
            if not successful_results:
                return {'error': 'No successful processing results'}
            
            stats = {
                'total_images': len(results),
                'successful_processing': len(successful_results),
                'success_rate': len(successful_results) / len(results) * 100,
                'region_types': {},
                'languages_detected': {},
                'average_confidence': 0.0,
                'field_extraction_rates': {}
            }
            
            # Analyze region types
            all_regions = []
            for result in successful_results:
                segmented = result.get('segmented_declarations', {})
                for region_type, regions in segmented.items():
                    stats['region_types'][region_type] = stats['region_types'].get(region_type, 0) + len(regions)
                    all_regions.extend(regions)
            
            # Calculate average confidence
            if all_regions:
                confidences = [r.get('confidence', 0) for r in all_regions]
                stats['average_confidence'] = np.mean(confidences)
            
            # Analyze languages
            for result in successful_results:
                languages = result.get('metadata', {}).get('detected_languages', [])
                for lang in languages:
                    stats['languages_detected'][lang] = stats['languages_detected'].get(lang, 0) + 1
            
            # Field extraction rates
            legal_fields = ['mrp', 'net_quantity', 'manufacturer', 'mfg_date', 'exp_date']
            for field in legal_fields:
                extracted_count = sum(1 for result in successful_results 
                                    if result.get('legal_metrology_fields', {}).get(field) is not None)
                stats['field_extraction_rates'][field] = extracted_count / len(successful_results) * 100
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics generation failed: {e}")
            return {'error': str(e)}


def demo_enhanced_vision():
    """Demonstration of enhanced vision processing capabilities"""
    
    # Initialize processor
    processor = EnhancedVisionProcessor()
    
    # Sample image paths (replace with actual paths)
    sample_images = [
        "app/data/samples/product1.jpg",
        "app/data/samples/product2.jpg",
        "app/data/samples/product3.jpg"
    ]
    
    # Check if sample images exist
    existing_images = [img for img in sample_images if Path(img).exists()]
    
    if existing_images:
        print(f"Processing {len(existing_images)} sample images...")
        
        # Batch process images
        results = processor.batch_process_images(existing_images)
        
        # Generate statistics
        stats = processor.get_processing_statistics(results)
        
        print(f"Processing completed!")
        print(f"Success rate: {stats.get('success_rate', 0):.1f}%")
        print(f"Average confidence: {stats.get('average_confidence', 0):.2f}")
        print(f"Region types detected: {list(stats.get('region_types', {}).keys())}")
        print(f"Languages detected: {list(stats.get('languages_detected', {}).keys())}")
        
        return results, stats
    else:
        print("No sample images found. Please add sample images to app/data/samples/")
        return [], {}

if __name__ == "__main__":
    # Run demonstration
    demo_enhanced_vision()
