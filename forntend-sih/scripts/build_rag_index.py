#!/usr/bin/env python3
"""
RAG Index Builder CLI for Legal Metrology Compliance Chatbot
Builds FAISS vector index from knowledge base files
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.services.rag_index import RAGIndex
    from app.config import settings
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this script from the project root directory")
    print("and that all dependencies are installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import faiss
    except ImportError:
        missing_deps.append("faiss-cpu")
    
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstall missing dependencies with:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    
    return True

def check_environment():
    """Check environment configuration"""
    if not settings:
        print("❌ Configuration error: Settings not properly loaded")
        print("Make sure you have:")
        print("1. Created a .env file with OPENAI_API_KEY")
        print("2. Set all required environment variables")
        print("3. Check the .env.example file for reference")
        return False
    
    # Check OpenAI API key
    if not settings.openai_api_key or settings.openai_api_key.startswith("sk-") == False:
        print("❌ Invalid or missing OpenAI API key")
        print("Set OPENAI_API_KEY in your .env file")
        return False
    
    return True

def check_knowledge_base():
    """Check if knowledge base files exist"""
    if not settings:
        return False
    
    kb_path = Path(settings.kb_dir)
    if not kb_path.exists():
        print(f"❌ Knowledge base directory not found: {kb_path}")
        print("Create the directory and add knowledge files (.md, .txt, .yaml, .jsonl)")
        return False
    
    knowledge_files = settings.get_knowledge_files()
    if not knowledge_files:
        print(f"❌ No knowledge files found in: {kb_path}")
        print("Add knowledge files with extensions: .md, .txt, .yaml, .yml, .jsonl, .json")
        return False
    
    print(f"✅ Found {len(knowledge_files)} knowledge files:")
    for file in knowledge_files:
        print(f"   - {file.name} ({file.stat().st_size} bytes)")
    
    return True

def build_index(force_rebuild=False, verbose=False):
    """Build the RAG index"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🔧 Building RAG index...")
    print(f"📁 Knowledge base: {settings.kb_dir}")
    print(f"💾 Index output: {settings.index_path}")
    print(f"🤖 OpenAI model: {settings.openai_embedding_model}")
    
    try:
        # Create RAG index
        rag_index = RAGIndex()
        
        # Build index
        rag_index.build_index(force_rebuild=force_rebuild)
        
        # Get statistics
        stats = rag_index.get_stats()
        
        print("\n✅ Index built successfully!")
        print(f"📊 Total chunks: {stats.get('total_chunks', 0)}")
        print(f"📁 Source files: {stats.get('total_source_files', 0)}")
        print(f"🔍 Embedding dimension: {stats.get('embedding_dimension', 0)}")
        
        # Show content breakdown
        content_types = stats.get('content_types', {})
        if content_types:
            print("\n📋 Content breakdown:")
            for content_type, count in content_types.items():
                print(f"   - {content_type}: {count} chunks")
        
        # Show top topics
        top_topics = stats.get('top_topics', {})
        if top_topics:
            print("\n🏷️ Top topics:")
            for topic, count in list(top_topics.items())[:5]:
                print(f"   - {topic}: {count} chunks")
        
        print(f"\n💾 Index saved to: {Path(settings.index_path).absolute()}")
        print("\n🚀 Ready to use! Start the Streamlit app to test the RAG chatbot.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error building index: {e}")
        logger.exception("Detailed error information:")
        return False

def test_index():
    """Test the built index with a sample query"""
    print("🧪 Testing the RAG index...")
    
    try:
        rag_index = RAGIndex()
        rag_index.load_index()
        
        # Test query
        test_query = "What is MRP and is it mandatory for e-commerce?"
        print(f"🔍 Test query: {test_query}")
        
        # Get context
        context = rag_index.get_context(test_query, max_length=500)
        
        print(f"\n📄 Retrieved context ({len(context)} characters):")
        print("-" * 50)
        print(context[:500] + "..." if len(context) > 500 else context)
        print("-" * 50)
        
        # Get search results
        results = rag_index.search(test_query, top_k=3)
        
        print(f"\n🔍 Top {len(results)} search results:")
        for i, (chunk, score) in enumerate(results, 1):
            print(f"{i}. Score: {score:.3f} | Source: {Path(chunk.source_file).name}")
            print(f"   Content: {chunk.content[:100]}...")
        
        print("\n✅ Index test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing index: {e}")
        logger.exception("Detailed error information:")
        return False

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Build RAG index for Legal Metrology Compliance Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build_rag_index.py                    # Build index
  python scripts/build_rag_index.py --force            # Force rebuild
  python scripts/build_rag_index.py --test             # Test existing index
  python scripts/build_rag_index.py --check            # Check setup only
  python scripts/build_rag_index.py --verbose          # Verbose output
        """
    )
    
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Force rebuild even if index exists'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test the existing index instead of building'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check setup and configuration only'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    print("🤖 Legal Metrology RAG Index Builder")
    print("=" * 50)
    
    # Check dependencies
    print("\n1. 🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies available")
    
    # Check environment
    print("\n2. ⚙️ Checking environment...")
    if not check_environment():
        sys.exit(1)
    print("✅ Environment configured correctly")
    
    # Check knowledge base
    print("\n3. 📚 Checking knowledge base...")
    if not check_knowledge_base():
        sys.exit(1)
    print("✅ Knowledge base ready")
    
    if args.check:
        print("\n✅ All checks passed! Ready to build index.")
        return
    
    if args.test:
        print("\n4. 🧪 Testing existing index...")
        if test_index():
            print("\n🎉 RAG system is working correctly!")
        else:
            print("\n❌ Index test failed. Try rebuilding with --force")
            sys.exit(1)
        return
    
    # Build index
    print("\n4. 🔧 Building index...")
    if build_index(force_rebuild=args.force, verbose=args.verbose):
        print("\n🎉 RAG index built successfully!")
        
        # Offer to test
        try:
            response = input("\n🧪 Would you like to test the index? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                print()
                test_index()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
    else:
        print("\n❌ Failed to build index. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("Detailed error information:")
        sys.exit(1)
