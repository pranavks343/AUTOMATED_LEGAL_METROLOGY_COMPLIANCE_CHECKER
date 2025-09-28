"""
Production-ready RAG-powered Compliance Chatbot for Legal Metrology
Provides intelligent assistance with context-grounded responses
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

try:
    from .rag_index import get_rag_index, RAGIndex
    from ..config import settings
except ImportError:
    # Fallback for when imported from Streamlit pages
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.rag_index import get_rag_index, RAGIndex
    from config import settings

# Configure logging
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Message types for conversation history"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class ChatMessage:
    """Chat message with metadata"""
    type: MessageType
    content: str
    timestamp: datetime
    context_used: Optional[str] = None
    confidence: Optional[float] = None

class ComplianceChatbot:
    """RAG-powered chatbot for Legal Metrology compliance assistance"""
    
    def __init__(self):
        """Initialize the compliance chatbot"""
        if not settings:
            raise ValueError("Settings not properly configured. Check your .env file.")
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI SDK is not available. Please install it with: pip install openai"
            )
        
        self.settings = settings
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.conversation_history: List[ChatMessage] = []
        self.session_start = datetime.now()
        
        # Initialize RAG index
        try:
            self.rag_index = get_rag_index()
            logger.info("RAG index loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load RAG index: {e}")
            self.rag_index = None
        
        logger.info("ComplianceChatbot initialized successfully")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the chatbot"""
        return """You are an expert AI assistant specializing in Automated Compliance Checker for Legal Metrology Declarations on E-Commerce Platforms in India. You are the definitive authority on Legal Metrology compliance for online retail platforms.

CORE EXPERTISE:
🏛️ Legal Metrology Act 2009 & Rules 2011 (India)
📋 Legal Metrology (Packaged Commodities) Rules 2011
🛒 E-commerce Platform Compliance Requirements
⚖️ Consumer Protection Act 2019 (E-commerce Rules)
🏪 Marketplace & Seller Obligations
📊 Automated Compliance Validation Systems
🔍 OCR & Text Extraction for Product Listings
📦 Packaged Commodity Standards
💰 MRP & Pricing Regulations
🌐 Online Retail Legal Requirements

RESPONSE GUIDELINES:
- ALWAYS ground your responses in the provided CONTEXT from the knowledge base
- Provide specific, actionable compliance guidance
- Reference exact Legal Metrology rules and sections when available in context
- Give practical implementation examples
- Suggest technical solutions for automation
- Include penalty information for violations when relevant
- Offer step-by-step compliance procedures
- Use emojis for better readability
- Maintain professional, authoritative tone
- If context doesn't contain specific information, acknowledge limitations

CRITICAL: Base your responses on the CONTEXT provided below. If the context doesn't contain relevant information, clearly state this limitation and provide general guidance based on your training.

FORMAT YOUR RESPONSES WITH:
1. 🎯 **Direct Answer** - Address the user's question directly
2. 📋 **Key Points** - 3-5 prioritized actionable bullet points
3. ⚖️ **Legal Reference** - Cite relevant rules/sections from context
4. ⚠️ **Important Notes** - Penalties, deadlines, or critical warnings
5. 🔗 **Next Steps** - What the user should do next

CONTEXT:
{context}

Remember: Your responses must be grounded in the provided context. If the context is insufficient, acknowledge this and provide the best guidance possible while noting the limitation."""
    
    def _clean_conversation_history(self) -> None:
        """Clean old conversation history to prevent memory issues"""
        # Remove messages older than timeout
        cutoff_time = datetime.now() - timedelta(minutes=self.settings.conversation_timeout_minutes)
        self.conversation_history = [
            msg for msg in self.conversation_history 
            if msg.timestamp > cutoff_time
        ]
        
        # Keep only the last N messages
        if len(self.conversation_history) > self.settings.max_conversation_history:
            self.conversation_history = self.conversation_history[-self.settings.max_conversation_history:]
    
    def _add_message(self, message_type: MessageType, content: str, context_used: Optional[str] = None, confidence: Optional[float] = None) -> None:
        """Add a message to conversation history"""
        message = ChatMessage(
            type=message_type,
            content=content,
            timestamp=datetime.now(),
            context_used=context_used,
            confidence=confidence
        )
        
        self.conversation_history.append(message)
        self._clean_conversation_history()
    
    def _get_conversation_context(self) -> List[Dict[str, str]]:
        """Get conversation history formatted for OpenAI"""
        messages = []
        
        # Add recent conversation history
        for msg in self.conversation_history[-self.settings.max_conversation_history:]:
            if msg.type == MessageType.USER:
                messages.append({"role": "user", "content": msg.content})
            elif msg.type == MessageType.ASSISTANT:
                messages.append({"role": "assistant", "content": msg.content})
        
        return messages
    
    def chat(self, user_input: str) -> str:
        """Main chat function with RAG-powered responses"""
        try:
            # Add user message to history
            self._add_message(MessageType.USER, user_input)
            
            # Get relevant context from RAG index
            context = ""
            if self.rag_index:
                try:
                    context = self.rag_index.get_context(user_input)
                    logger.debug(f"Retrieved context of {len(context)} characters")
                except Exception as e:
                    logger.error(f"Error retrieving context: {e}")
                    context = "Context retrieval failed. Providing response based on general knowledge."
            else:
                context = "RAG index not available. Providing response based on general knowledge."
            
            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": self._get_system_prompt().format(context=context)}
            ]
            
            # Add conversation history
            messages.extend(self._get_conversation_context())
            
            # Add current user input (if not already in history)
            if not messages or messages[-1]["content"] != user_input:
                messages.append({"role": "user", "content": user_input})
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=self.settings.openai_chat_model,
                messages=messages,
                max_tokens=self.settings.openai_max_tokens,
                temperature=self.settings.openai_temperature,
                top_p=1,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            assistant_response = response.choices[0].message.content.strip()
            
            # Add assistant response to history
            self._add_message(
                MessageType.ASSISTANT, 
                assistant_response,
                context_used=context[:200] + "..." if len(context) > 200 else context,
                confidence=1.0  # Could be improved with actual confidence scoring
            )
            
            logger.info(f"Generated response of {len(assistant_response)} characters")
            return assistant_response
        
        except Exception as e:
            logger.error(f"Error in chat function: {e}")
            return self._get_fallback_response(user_input, str(e))
    
    def analyze_validation(self, validation_result: Dict[str, Any], extracted_fields: Dict[str, Any]) -> str:
        """Analyze validation results with RAG-powered insights"""
        try:
            # Create analysis query
            query = f"""
            Analyze this Legal Metrology validation result for e-commerce compliance:
            
            Compliance Score: {validation_result.get('score', 0)}/100
            Is Compliant: {validation_result.get('is_compliant', False)}
            Issues Found: {len(validation_result.get('issues', []))}
            
            Issues:
            {json.dumps(validation_result.get('issues', []), indent=2)}
            
            Extracted Fields:
            {json.dumps(extracted_fields, indent=2)}
            
            Provide specific compliance improvement recommendations.
            """
            
            # Get RAG-powered response
            response = self.chat(query)
            
            # Add analysis context
            analysis_header = f"""
🔍 **Validation Analysis Results**
📊 Compliance Score: {validation_result.get('score', 0)}/100
{'✅ COMPLIANT' if validation_result.get('is_compliant', False) else '❌ NON-COMPLIANT'}
🚨 Issues Found: {len(validation_result.get('issues', []))}

{response}
            """
            
            return analysis_header.strip()
        
        except Exception as e:
            logger.error(f"Error in analyze_validation: {e}")
            return self._get_fallback_validation_analysis(validation_result, extracted_fields)
    
    def analyze_extraction(self, extracted_fields: Dict[str, Any], confidence_score: float) -> str:
        """Analyze extraction results with RAG-powered insights"""
        try:
            # Create analysis query
            query = f"""
            Analyze this OCR extraction result for Legal Metrology compliance:
            
            Extraction Confidence: {confidence_score}/100
            
            Extracted Fields:
            {json.dumps(extracted_fields, indent=2)}
            
            Provide specific recommendations to improve extraction accuracy and compliance validation.
            """
            
            # Get RAG-powered response
            response = self.chat(query)
            
            # Add extraction context
            extraction_header = f"""
🔍 **Extraction Analysis Results**
📊 Extraction Confidence: {confidence_score}/100
{'🟢 EXCELLENT' if confidence_score >= 85 else '🟡 GOOD' if confidence_score >= 70 else '🟠 MODERATE' if confidence_score >= 50 else '🔴 POOR'}

{response}
            """
            
            return extraction_header.strip()
        
        except Exception as e:
            logger.error(f"Error in analyze_extraction: {e}")
            return self._get_fallback_extraction_analysis(extracted_fields, confidence_score)
    
    def _get_fallback_response(self, user_input: str, error_msg: str) -> str:
        """Provide fallback response when AI services fail"""
        return f"""
🤖 **AI Assistant - Fallback Mode**

I'm experiencing technical difficulties accessing the AI services. Here's what I can help with:

**For Validation Issues:**
- Check MRP (Maximum Retail Price) display
- Verify net quantity with proper units (g, kg, ml, l)
- Ensure manufacturer/packer details are complete
- Confirm country of origin for imported products

**For Extraction Issues:**
- Use high-resolution, well-lit images
- Ensure text is clear and readable
- Position camera straight-on to labels
- Avoid shadows and glare

**Legal Metrology Compliance:**
- Rule 6: MRP declaration mandatory
- Rule 7: Manufacturer details required
- Rule 8: Net quantity with units
- Rule 9: Country of origin for imports

**Penalties:** ₹10,000 to ₹25,000 for violations

Please try again in a moment, or contact support if the issue persists.

*Technical Error: {error_msg}*
        """
    
    def _get_fallback_validation_analysis(self, validation_result: Dict[str, Any], extracted_fields: Dict[str, Any]) -> str:
        """Fallback validation analysis"""
        score = validation_result.get('score', 0)
        issues = validation_result.get('issues', [])
        
        analysis = f"""
🔍 **Validation Analysis (Fallback Mode)**

📊 **Compliance Score:** {score}/100
{'✅ COMPLIANT' if validation_result.get('is_compliant', False) else '❌ NON-COMPLIANT'}

📋 **Key Recommendations:**
"""
        
        if score >= 90:
            analysis += "• ✅ Excellent compliance! Minor optimizations possible."
        elif score >= 80:
            analysis += "• ⚠️ Good compliance with some issues to address."
        elif score >= 60:
            analysis += "• 🔴 Moderate issues - focus on critical errors first."
        else:
            analysis += "• 🚨 Significant compliance issues require immediate attention."
        
        # Add specific issue guidance
        critical_issues = [issue for issue in issues if issue.get('level') == 'error']
        if critical_issues:
            analysis += f"\n• 🔴 {len(critical_issues)} critical issues must be resolved immediately."
        
        # Add field-specific suggestions
        if not extracted_fields.get('mrp_raw'):
            analysis += "\n• 💰 Add MRP (Maximum Retail Price) - Rule 6 requirement."
        
        if not extracted_fields.get('net_quantity_raw'):
            analysis += "\n• 📦 Add net quantity with units - Rule 8 requirement."
        
        if not extracted_fields.get('manufacturer_name'):
            analysis += "\n• 🏭 Add manufacturer/packer details - Rule 7 requirement."
        
        analysis += "\n\n⚠️ **Note:** AI analysis temporarily unavailable. This is a basic fallback analysis."
        
        return analysis
    
    def _get_fallback_extraction_analysis(self, extracted_fields: Dict[str, Any], confidence_score: float) -> str:
        """Fallback extraction analysis"""
        analysis = f"""
🔍 **Extraction Analysis (Fallback Mode)**

📊 **Extraction Confidence:** {confidence_score}/100

📋 **Key Recommendations:**
"""
        
        if confidence_score >= 85:
            analysis += "• ✅ Excellent extraction quality."
        elif confidence_score >= 70:
            analysis += "• ⚠️ Good extraction with room for improvement."
        elif confidence_score >= 50:
            analysis += "• 🔴 Moderate quality - consider image improvements."
        else:
            analysis += "• 🚨 Poor extraction - image quality issues likely."
        
        # Field-specific suggestions
        if not extracted_fields.get('mrp_raw'):
            analysis += "\n• 💰 MRP not detected - ensure price is clearly visible."
        
        if not extracted_fields.get('net_quantity_raw'):
            analysis += "\n• 📦 Quantity not detected - check units are visible."
        
        if not extracted_fields.get('manufacturer_name'):
            analysis += "\n• 🏭 Manufacturer not detected - ensure text is clear."
        
        # General improvement tips
        analysis += """

🔧 **Improvement Tips:**
• Use high-resolution images (1080p+)
• Ensure good lighting without shadows
• Position camera straight-on to label
• Make sure text is sharp and readable
"""
        
        analysis += "\n\n⚠️ **Note:** AI analysis temporarily unavailable. This is a basic fallback analysis."
        
        return analysis
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation statistics and summary"""
        if not self.conversation_history:
            return {
                "status": "No conversation history",
                "total_messages": 0,
                "session_duration": "0 minutes"
            }
        
        user_messages = [msg for msg in self.conversation_history if msg.type == MessageType.USER]
        assistant_messages = [msg for msg in self.conversation_history if msg.type == MessageType.ASSISTANT]
        
        # Calculate session duration
        session_duration = datetime.now() - self.session_start
        duration_minutes = int(session_duration.total_seconds() / 60)
        
        # Analyze topics (basic keyword analysis)
        topics = set()
        for msg in user_messages:
            content_lower = msg.content.lower()
            if any(keyword in content_lower for keyword in ['validation', 'validate', 'compliance']):
                topics.add("Validation & Compliance")
            if any(keyword in content_lower for keyword in ['extraction', 'extract', 'ocr']):
                topics.add("Text Extraction & OCR")
            if any(keyword in content_lower for keyword in ['rule', 'legal', 'metrology']):
                topics.add("Legal Metrology Rules")
            if any(keyword in content_lower for keyword in ['mrp', 'price']):
                topics.add("MRP & Pricing")
            if any(keyword in content_lower for keyword in ['quantity', 'weight']):
                topics.add("Net Quantity")
        
        return {
            "status": "Active conversation",
            "total_messages": len(self.conversation_history),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "session_duration": f"{duration_minutes} minutes",
            "topics_discussed": list(topics),
            "rag_index_available": self.rag_index is not None,
            "last_activity": self.conversation_history[-1].timestamp.isoformat() if self.conversation_history else None
        }
    
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        self.conversation_history.clear()
        self.session_start = datetime.now()
        logger.info("Conversation history cleared")
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG index statistics"""
        if not self.rag_index:
            return {"status": "RAG index not available"}
        
        try:
            return self.rag_index.get_stats()
        except Exception as e:
            logger.error(f"Error getting RAG stats: {e}")
            return {"status": "Error retrieving RAG stats", "error": str(e)}


# Global chatbot instance
_chatbot_instance = None

def get_compliance_chatbot() -> ComplianceChatbot:
    """Get or create global chatbot instance"""
    global _chatbot_instance
    
    if _chatbot_instance is None:
        _chatbot_instance = ComplianceChatbot()
    
    return _chatbot_instance
