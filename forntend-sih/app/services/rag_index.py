"""
RAG Index Service for Legal Metrology Compliance Chatbot
Handles document chunking, embedding generation, and FAISS vector search
"""

import os
import json
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

try:
    from app.config import settings
except ImportError:
    # Fallback for when imported from Streamlit pages
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from config import settings
    except ImportError:
        # Create a minimal settings object if config is not available
        class Settings:
            def __init__(self):
                self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
                self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
                self.knowledge_base_dir = Path('app/data/knowledge')
                self.faiss_index_path = Path('app/data/faiss_index')
        
        settings = Settings()

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class DocChunk:
    """Represents a document chunk with metadata"""
    
    id: str
    content: str
    source_file: str
    chunk_index: int
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert numpy array to list for JSON serialization
        if self.embedding is not None:
            data['embedding'] = self.embedding.tolist()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocChunk":
        """Create from dictionary"""
        # Convert list back to numpy array
        if data.get('embedding') is not None:
            data['embedding'] = np.array(data['embedding'])
        return cls(**data)


class RAGIndex:
    """RAG Index for Legal Metrology knowledge base using FAISS"""
    
    def __init__(self):
        """Initialize RAG Index"""
        if not settings:
            raise ValueError("Settings not properly configured. Check your .env file.")
        
        if not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS is not available. Please install it with: pip install faiss-cpu"
            )
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI SDK is not available. Please install it with: pip install openai"
            )
        
        self.settings = settings
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.chunks: List[DocChunk] = []
        self.index: Optional[faiss.Index] = None
        self.embedding_dim: Optional[int] = None
        
        logger.info("RAGIndex initialized successfully")
    
    def _chunk_text(self, text: str, source_file: str) -> List[str]:
        """Split text into chunks with overlap"""
        chunk_size = self.settings.chunk_size
        chunk_overlap = self.settings.chunk_overlap
        
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # Skip very small chunks
            if len(chunk_text.strip()) < 50:
                continue
                
            chunks.append(chunk_text.strip())
        
        logger.debug(f"Split {source_file} into {len(chunks)} chunks")
        return chunks
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=text
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            
            # Set embedding dimension on first call
            if self.embedding_dim is None:
                self.embedding_dim = len(embedding)
                logger.info(f"Embedding dimension: {self.embedding_dim}")
            
            return embedding
        
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
    
    def _process_file(self, file_path: Path) -> List[DocChunk]:
        """Process a single file and return document chunks"""
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Read file content based on extension
            if file_path.suffix.lower() in ['.json', '.jsonl']:
                content = self._process_json_file(file_path)
            else:
                # Text-based files (.md, .txt, .yaml, .yml)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Skip empty files
            if not content.strip():
                logger.warning(f"Skipping empty file: {file_path}")
                return []
            
            # Chunk the content
            text_chunks = self._chunk_text(content, str(file_path))
            
            # Create DocChunk objects
            doc_chunks = []
            for i, chunk_text in enumerate(text_chunks):
                chunk_id = f"{file_path.stem}_{i}"
                
                # Extract metadata based on file type
                metadata = self._extract_metadata(file_path, chunk_text)
                
                doc_chunk = DocChunk(
                    id=chunk_id,
                    content=chunk_text,
                    source_file=str(file_path),
                    chunk_index=i,
                    metadata=metadata
                )
                
                doc_chunks.append(doc_chunk)
            
            logger.info(f"Created {len(doc_chunks)} chunks from {file_path}")
            return doc_chunks
        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return []
    
    def _process_json_file(self, file_path: Path) -> str:
        """Process JSON/JSONL files and convert to text"""
        content_parts = []
        
        try:
            if file_path.suffix == '.jsonl':
                # Process JSONL line by line
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if line.strip():
                            try:
                                data = json.loads(line)
                                content_parts.append(self._json_to_text(data, f"Line {line_num}"))
                            except json.JSONDecodeError as e:
                                logger.warning(f"Invalid JSON on line {line_num} in {file_path}: {e}")
            else:
                # Process regular JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content_parts.append(self._json_to_text(data, "JSON Data"))
        
        except Exception as e:
            logger.error(f"Error processing JSON file {file_path}: {e}")
            return ""
        
        return "\n\n".join(content_parts)
    
    def _json_to_text(self, data: Any, prefix: str = "") -> str:
        """Convert JSON data to readable text"""
        if isinstance(data, dict):
            parts = []
            if prefix:
                parts.append(f"{prefix}:")
            
            for key, value in data.items():
                if isinstance(value, (str, int, float, bool)):
                    parts.append(f"{key}: {value}")
                elif isinstance(value, list):
                    parts.append(f"{key}: {', '.join(map(str, value))}")
                elif isinstance(value, dict):
                    parts.append(self._json_to_text(value, key))
            
            return "\n".join(parts)
        
        elif isinstance(data, list):
            return "\n".join([self._json_to_text(item, f"Item {i+1}") for i, item in enumerate(data)])
        
        else:
            return str(data)
    
    def _extract_metadata(self, file_path: Path, chunk_text: str) -> Dict[str, Any]:
        """Extract metadata from file and chunk"""
        metadata = {
            'file_name': file_path.name,
            'file_type': file_path.suffix.lower(),
            'file_size': file_path.stat().st_size if file_path.exists() else 0,
            'chunk_length': len(chunk_text)
        }
        
        # Add content-based metadata
        text_lower = chunk_text.lower()
        
        # Identify content type
        if any(keyword in text_lower for keyword in ['rule', 'section', 'act', 'regulation']):
            metadata['content_type'] = 'legal_rule'
        elif any(keyword in text_lower for keyword in ['faq', 'question', 'answer', 'q:', 'a:']):
            metadata['content_type'] = 'faq'
        elif any(keyword in text_lower for keyword in ['mrp', 'price', 'quantity', 'manufacturer']):
            metadata['content_type'] = 'compliance_field'
        elif any(keyword in text_lower for keyword in ['penalty', 'fine', 'violation']):
            metadata['content_type'] = 'enforcement'
        else:
            metadata['content_type'] = 'general'
        
        # Extract key topics
        topics = []
        topic_keywords = {
            'mrp': ['mrp', 'maximum retail price', 'price'],
            'quantity': ['quantity', 'weight', 'net quantity', 'volume'],
            'manufacturer': ['manufacturer', 'packer', 'importer'],
            'country_origin': ['country of origin', 'made in', 'origin'],
            'penalties': ['penalty', 'fine', 'violation', 'punishment'],
            'ecommerce': ['e-commerce', 'platform', 'marketplace', 'online'],
            'compliance': ['compliance', 'validation', 'checking']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        metadata['topics'] = topics
        
        return metadata
    
    def build_index(self, force_rebuild: bool = False) -> None:
        """Build the FAISS index from knowledge base files"""
        index_file = Path(self.settings.index_path) / "faiss.index"
        metadata_file = Path(self.settings.index_path) / "metadata.pkl"
        
        # Check if index already exists and is recent
        if not force_rebuild and index_file.exists() and metadata_file.exists():
            logger.info("Index already exists. Use force_rebuild=True to rebuild.")
            return
        
        logger.info("Building FAISS index...")
        
        # Get all knowledge files
        knowledge_files = self.settings.get_knowledge_files()
        if not knowledge_files:
            raise ValueError(f"No knowledge files found in {self.settings.kb_dir}")
        
        # Process all files
        all_chunks = []
        for file_path in knowledge_files:
            file_chunks = self._process_file(file_path)
            all_chunks.extend(file_chunks)
        
        if not all_chunks:
            raise ValueError("No content chunks created from knowledge files")
        
        logger.info(f"Created {len(all_chunks)} total chunks")
        
        # Generate embeddings for all chunks
        logger.info("Generating embeddings...")
        embeddings = []
        
        for i, chunk in enumerate(all_chunks):
            if i % 10 == 0:
                logger.info(f"Processing chunk {i+1}/{len(all_chunks)}")
            
            try:
                embedding = self._get_embedding(chunk.content)
                chunk.embedding = embedding
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error generating embedding for chunk {chunk.id}: {e}")
                continue
        
        if not embeddings:
            raise ValueError("No embeddings generated successfully")
        
        # Create FAISS index
        logger.info("Creating FAISS index...")
        embeddings_matrix = np.vstack(embeddings).astype(np.float32)
        
        # Use IndexFlatIP for cosine similarity (after normalization)
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings_matrix)
        
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings_matrix)
        
        # Save index and metadata
        os.makedirs(self.settings.index_path, exist_ok=True)
        
        faiss.write_index(index, str(index_file))
        
        with open(metadata_file, 'wb') as f:
            pickle.dump(all_chunks, f)
        
        # Update instance variables
        self.index = index
        self.chunks = all_chunks
        
        logger.info(f"Index built successfully with {len(all_chunks)} chunks")
        logger.info(f"Index saved to: {index_file}")
    
    def load_index(self) -> None:
        """Load the FAISS index from disk"""
        index_file = Path(self.settings.index_path) / "faiss.index"
        metadata_file = Path(self.settings.index_path) / "metadata.pkl"
        
        if not index_file.exists() or not metadata_file.exists():
            raise FileNotFoundError(
                f"Index files not found. Please build the index first using build_rag_index.py"
            )
        
        logger.info("Loading FAISS index...")
        
        # Load index
        self.index = faiss.read_index(str(index_file))
        
        # Load metadata
        with open(metadata_file, 'rb') as f:
            self.chunks = pickle.load(f)
        
        # Set embedding dimension
        self.embedding_dim = self.index.d
        
        logger.info(f"Index loaded successfully with {len(self.chunks)} chunks")
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Tuple[DocChunk, float]]:
        """Search for relevant chunks using the query"""
        if self.index is None:
            raise ValueError("Index not loaded. Please load or build the index first.")
        
        if top_k is None:
            top_k = self.settings.top_k_results
        
        # Generate query embedding
        query_embedding = self._get_embedding(query)
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Return results with chunks and scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):  # Valid index
                chunk = self.chunks[idx]
                results.append((chunk, float(score)))
        
        logger.debug(f"Found {len(results)} results for query: {query[:50]}...")
        return results
    
    def get_context(self, query: str, max_length: Optional[int] = None) -> str:
        """Get context for a query, truncated to max_length"""
        if max_length is None:
            max_length = self.settings.max_context_length
        
        # Search for relevant chunks
        results = self.search(query)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        # Build context from results
        context_parts = []
        current_length = 0
        
        for chunk, score in results:
            # Add source information
            source_info = f"[Source: {chunk.source_file}, Score: {score:.3f}]"
            chunk_text = f"{source_info}\n{chunk.content}\n"
            
            # Check if adding this chunk would exceed max_length
            if current_length + len(chunk_text) > max_length:
                # Try to add a truncated version
                remaining_length = max_length - current_length - len(source_info) - 10
                if remaining_length > 100:  # Only add if meaningful content can fit
                    truncated_content = chunk.content[:remaining_length] + "..."
                    chunk_text = f"{source_info}\n{truncated_content}\n"
                    context_parts.append(chunk_text)
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        context = "\n".join(context_parts)
        
        if current_length >= max_length:
            context += f"\n[Context truncated at {max_length} characters]"
        
        logger.debug(f"Generated context of {len(context)} characters from {len(context_parts)} chunks")
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if not self.chunks:
            return {"status": "Index not loaded"}
        
        # Count by content type
        content_types = {}
        topics_count = {}
        source_files = set()
        
        for chunk in self.chunks:
            # Content types
            content_type = chunk.metadata.get('content_type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Topics
            for topic in chunk.metadata.get('topics', []):
                topics_count[topic] = topics_count.get(topic, 0) + 1
            
            # Source files
            source_files.add(chunk.source_file)
        
        return {
            "status": "Index loaded",
            "total_chunks": len(self.chunks),
            "total_source_files": len(source_files),
            "embedding_dimension": self.embedding_dim,
            "content_types": content_types,
            "top_topics": dict(sorted(topics_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            "source_files": sorted(list(source_files))
        }


# Global RAG index instance
rag_index = None

def get_rag_index() -> RAGIndex:
    """Get or create global RAG index instance"""
    global rag_index
    
    if rag_index is None:
        rag_index = RAGIndex()
        try:
            rag_index.load_index()
        except FileNotFoundError:
            logger.warning("FAISS index not found. Please build it first using build_rag_index.py")
            raise
    
    return rag_index
