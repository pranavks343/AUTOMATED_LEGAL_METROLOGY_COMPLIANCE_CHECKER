"""
Configuration management for Legal Metrology RAG Chatbot
Handles environment variables and application settings
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Settings:
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.3
    
    # RAG Configuration
    kb_dir: str = "app/data/knowledge"
    index_path: str = "app/data/faiss_index"
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_context_length: int = 8000
    top_k_results: int = 5
    
    # Conversation Configuration
    max_conversation_history: int = 10
    conversation_timeout_minutes: int = 30
    
    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables"""
        
        # Check for required environment variables
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        
        # Create settings with defaults
        settings = cls(
            openai_api_key=openai_api_key,
            openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            openai_max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
            
            kb_dir=os.getenv("KB_DIR", "app/data/knowledge"),
            index_path=os.getenv("INDEX_PATH", "app/data/faiss_index"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
            max_context_length=int(os.getenv("MAX_CONTEXT_LENGTH", "8000")),
            top_k_results=int(os.getenv("TOP_K_RESULTS", "5")),
            
            max_conversation_history=int(os.getenv("MAX_CONVERSATION_HISTORY", "10")),
            conversation_timeout_minutes=int(os.getenv("CONVERSATION_TIMEOUT_MINUTES", "30")),
            
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        # Validate paths exist or can be created
        settings._validate_paths()
        
        logger.info("Settings loaded successfully")
        logger.info(f"Knowledge base directory: {settings.kb_dir}")
        logger.info(f"FAISS index path: {settings.index_path}")
        logger.info(f"OpenAI model: {settings.openai_chat_model}")
        
        return settings
    
    def _validate_paths(self):
        """Validate and create necessary directories"""
        
        # Create knowledge base directory if it doesn't exist
        kb_path = Path(self.kb_dir)
        kb_path.mkdir(parents=True, exist_ok=True)
        
        # Create index directory if it doesn't exist
        index_path = Path(self.index_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("Directory paths validated and created if necessary")
    
    def get_knowledge_files(self) -> list[Path]:
        """Get all knowledge files from the knowledge base directory"""
        kb_path = Path(self.kb_dir)
        
        # Supported file extensions
        extensions = ["*.md", "*.txt", "*.yaml", "*.yml", "*.jsonl", "*.json"]
        
        files = []
        for ext in extensions:
            files.extend(kb_path.glob(ext))
            # Also check subdirectories
            files.extend(kb_path.glob(f"**/{ext}"))
        
        logger.info(f"Found {len(files)} knowledge files")
        return sorted(files)


# Global settings instance
try:
    settings = Settings.from_env()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    # For development/testing, provide fallback
    settings = None
