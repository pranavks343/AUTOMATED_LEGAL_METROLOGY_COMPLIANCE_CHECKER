import streamlit as st
import traceback
from typing import Callable, Any
from functools import wraps
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    def handle_validation_error(error: Exception, context: str = "") -> None:
        """Handle validation-specific errors"""
        error_msg = f"Validation Error: {str(error)}"
        if context:
            error_msg = f"{context}: {error_msg}"
        
        st.error(f"❌ {error_msg}")
        st.info("💡 **Tip**: Check your input data format and try again.")
        
        # Log the error
        logger.error(f"Validation error in {context}: {str(error)}")
    
    @staticmethod
    def handle_file_error(error: Exception, filename: str = "") -> None:
        """Handle file operation errors"""
        error_msg = f"File Error: {str(error)}"
        if filename:
            error_msg = f"Error processing {filename}: {error_msg}"
        
        st.error(f"📁 {error_msg}")
        st.info("💡 **Tip**: Ensure the file exists and you have proper permissions.")
        
        # Log the error
        logger.error(f"File error: {str(error)}")
    
    @staticmethod
    def handle_ocr_error(error: Exception) -> None:
        """Handle OCR-specific errors"""
        st.error("🔍 **OCR Processing Error**")
        st.error(f"Error: {str(error)}")
        st.warning("⚠️ **Possible Solutions:**")
        st.markdown("""
        - Ensure Tesseract is installed: `brew install tesseract` (macOS) or `sudo apt-get install tesseract-ocr` (Ubuntu)
        - Check image quality and format (PNG, JPG supported)
        - Try uploading a clearer image with better contrast
        - Use manual text input as an alternative
        """)
        
        # Log the error
        logger.error(f"OCR error: {str(error)}")
    
    @staticmethod
    def handle_auth_error(error: Exception) -> None:
        """Handle authentication errors"""
        st.error("🔐 **Authentication Error**")
        st.error(f"Error: {str(error)}")
        st.info("💡 **Tip**: Please check your credentials and try again.")
        
        # Log the error
        logger.error(f"Authentication error: {str(error)}")
    
    @staticmethod
    def handle_system_error(error: Exception, context: str = "") -> None:
        """Handle general system errors"""
        error_msg = f"System Error: {str(error)}"
        if context:
            error_msg = f"{context}: {error_msg}"
        
        st.error(f"⚠️ {error_msg}")
        st.error("🚨 **System Error** - Please contact support if this persists.")
        
        # Show detailed error in expander for debugging
        with st.expander("🔍 Technical Details (for support)"):
            st.code(traceback.format_exc())
        
        # Log the error
        logger.error(f"System error in {context}: {str(error)}")

def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """Decorator to safely execute functions with error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            ErrorHandler.handle_file_error(e)
            return None
        except PermissionError as e:
            ErrorHandler.handle_file_error(e)
            return None
        except ValueError as e:
            ErrorHandler.handle_validation_error(e)
            return None
        except Exception as e:
            ErrorHandler.handle_system_error(e, f"in {func.__name__}")
            return None
    return wrapper

def with_error_handling(error_context: str = ""):
    """Decorator factory for error handling with custom context"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_system_error(e, error_context)
                return None
        return wrapper
    return decorator

def show_loading_spinner(message: str = "Processing..."):
    """Context manager for showing loading spinner"""
    return st.spinner(message)

def show_success_message(message: str, details: str = ""):
    """Show a standardized success message"""
    st.success(f"✅ {message}")
    if details:
        st.info(f"💡 {details}")

def show_warning_message(message: str, details: str = ""):
    """Show a standardized warning message"""
    st.warning(f"⚠️ {message}")
    if details:
        st.info(f"💡 {details}")

def show_error_message(message: str, details: str = ""):
    """Show a standardized error message"""
    st.error(f"❌ {message}")
    if details:
        st.info(f"💡 {details}")

def validate_file_upload(file, allowed_types: list = None, max_size_mb: int = 10) -> bool:
    """Validate uploaded file"""
    if file is None:
        return False
    
    # Check file type
    if allowed_types and file.type not in allowed_types:
        show_error_message(
            f"Invalid file type: {file.type}",
            f"Allowed types: {', '.join(allowed_types)}"
        )
        return False
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        show_error_message(
            f"File too large: {file.size / 1024 / 1024:.1f} MB",
            f"Maximum size allowed: {max_size_mb} MB"
        )
        return False
    
    return True

def validate_text_input(text: str, min_length: int = 1, max_length: int = 10000) -> bool:
    """Validate text input"""
    if not text or not text.strip():
        show_error_message("Text input is required")
        return False
    
    if len(text) < min_length:
        show_error_message(f"Text too short (minimum {min_length} characters)")
        return False
    
    if len(text) > max_length:
        show_error_message(f"Text too long (maximum {max_length} characters)")
        return False
    
    return True
