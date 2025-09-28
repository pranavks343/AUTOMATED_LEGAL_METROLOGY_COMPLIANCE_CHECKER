"""
RAG Integration Module for existing workflow components
Provides RAG-powered analysis for validation and extraction results
"""

import logging
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

def get_rag_validation_analysis(validation_result: Dict[str, Any], extracted_fields: Dict[str, Any]) -> List[str]:
    """Get RAG-powered validation analysis with fallback"""
    try:
        from services.compliance_chatbot import get_compliance_chatbot
        
        chatbot = get_compliance_chatbot()
        analysis_text = chatbot.analyze_validation(validation_result, extracted_fields)
        
        # Convert to list format expected by existing code
        suggestions = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                # Clean bullet points
                suggestion = line.lstrip('•-* ').strip()
                if suggestion:
                    suggestions.append(suggestion)
            elif line and any(line.startswith(prefix) for prefix in ['🎯', '📋', '⚖️', '⚠️', '🔗']):
                # Include formatted sections
                suggestions.append(line)
        
        # If no structured suggestions found, return the full analysis
        if not suggestions:
            suggestions = [analysis_text]
        
        return suggestions[:5]  # Limit to 5 suggestions
        
    except Exception as e:
        logger.warning(f"RAG validation analysis failed: {e}")
        return get_fallback_validation_analysis(validation_result, extracted_fields)

def get_rag_extraction_analysis(extracted_fields: Dict[str, Any], confidence_score: float) -> List[str]:
    """Get RAG-powered extraction analysis with fallback"""
    try:
        from services.compliance_chatbot import get_compliance_chatbot
        
        chatbot = get_compliance_chatbot()
        analysis_text = chatbot.analyze_extraction(extracted_fields, confidence_score)
        
        # Convert to list format expected by existing code
        suggestions = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                # Clean bullet points
                suggestion = line.lstrip('•-* ').strip()
                if suggestion:
                    suggestions.append(suggestion)
            elif line and any(line.startswith(prefix) for prefix in ['🎯', '📋', '⚖️', '⚠️', '🔗']):
                # Include formatted sections
                suggestions.append(line)
        
        # If no structured suggestions found, return the full analysis
        if not suggestions:
            suggestions = [analysis_text]
        
        return suggestions[:5]  # Limit to 5 suggestions
        
    except Exception as e:
        logger.warning(f"RAG extraction analysis failed: {e}")
        return get_fallback_extraction_analysis(extracted_fields, confidence_score)

def get_fallback_validation_analysis(validation_result: Dict[str, Any], extracted_fields: Dict[str, Any]) -> List[str]:
    """Fallback validation analysis when RAG is unavailable"""
    suggestions = []
    score = validation_result.get('score', 0)
    issues = validation_result.get('issues', [])
    
    # Score-based suggestions
    if score >= 90:
        suggestions.append("🎉 Excellent compliance! Your product meets all Legal Metrology requirements.")
    elif score >= 80:
        suggestions.append("✅ Good compliance with minor issues. Review warnings and make adjustments.")
    elif score >= 60:
        suggestions.append("⚠️ Moderate compliance issues. Focus on critical errors first.")
    else:
        suggestions.append("🚨 Significant compliance issues require immediate attention.")
    
    # Issue-based suggestions
    critical_issues = [issue for issue in issues if issue.get('level') == 'error']
    if critical_issues:
        suggestions.append(f"🔴 {len(critical_issues)} critical issues must be resolved immediately.")
    
    # Field-specific suggestions
    if not extracted_fields.get('mrp_raw'):
        suggestions.append("💰 Add MRP (Maximum Retail Price) - Rule 6 requirement.")
    
    if not extracted_fields.get('net_quantity_raw'):
        suggestions.append("📦 Add net quantity with units - Rule 8 requirement.")
    
    if not extracted_fields.get('manufacturer_name'):
        suggestions.append("🏭 Add manufacturer/packer details - Rule 7 requirement.")
    
    return suggestions

def get_fallback_extraction_analysis(extracted_fields: Dict[str, Any], confidence_score: float) -> List[str]:
    """Fallback extraction analysis when RAG is unavailable"""
    suggestions = []
    
    # Confidence-based suggestions
    if confidence_score >= 85:
        suggestions.append("🔍 Excellent extraction quality! All major fields identified.")
    elif confidence_score >= 70:
        suggestions.append("📊 Good extraction with some fields identified. Review for accuracy.")
    elif confidence_score >= 50:
        suggestions.append("⚠️ Moderate extraction quality. Consider uploading clearer images.")
    else:
        suggestions.append("🚨 Low extraction quality. Upload higher quality images with better lighting.")
    
    # Field-specific suggestions
    if not extracted_fields.get('mrp_raw'):
        suggestions.append("💰 MRP not detected - ensure price is clearly visible.")
    
    if not extracted_fields.get('net_quantity_raw'):
        suggestions.append("📦 Quantity not detected - check units are visible.")
    
    if not extracted_fields.get('manufacturer_name'):
        suggestions.append("🏭 Manufacturer not detected - ensure text is clear.")
    
    # General improvement tips
    suggestions.append("📸 Use high-resolution images with good lighting for better extraction.")
    
    return suggestions

def is_rag_available() -> bool:
    """Check if RAG system is available and properly configured"""
    try:
        from services.compliance_chatbot import get_compliance_chatbot
        chatbot = get_compliance_chatbot()
        return chatbot.rag_index is not None
    except:
        return False
