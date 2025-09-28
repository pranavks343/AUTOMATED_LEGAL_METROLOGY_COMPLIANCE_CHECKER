#!/usr/bin/env python3
"""
Quick setup script for RAG chatbot
Helps users get started with the RAG system
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description} exists")
        return True
    else:
        print(f"❌ {description} not found")
        return False

def main():
    print("🚀 RAG Chatbot Quick Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app/streamlit_app.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    print("\n1. 📋 Checking project structure...")
    required_files = [
        ("app/config.py", "Configuration module"),
        ("app/services/rag_index.py", "RAG index service"),
        ("app/services/compliance_chatbot.py", "Compliance chatbot"),
        ("app/data/knowledge/seed_rules.md", "Legal Metrology rules"),
        ("app/data/knowledge/seed_faq.jsonl", "FAQ knowledge base"),
        ("scripts/build_rag_index.py", "Index builder script"),
        (".env.example", "Environment template")
    ]
    
    all_files_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Some required files are missing. Please check the project structure.")
        sys.exit(1)
    
    print("\n2. 📦 Installing required dependencies...")
    dependencies = [
        "openai>=1.0.0",
        "faiss-cpu>=1.7.0", 
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"\n❌ Failed to install {dep}")
            print("Please install manually and try again.")
            sys.exit(1)
    
    print("\n3. ⚙️ Setting up environment...")
    if not Path(".env").exists():
        if Path(".env.example").exists():
            run_command("cp .env.example .env", "Copying environment template")
            print("📝 Please edit .env file and add your OPENAI_API_KEY")
            print("   Get your API key from: https://platform.openai.com/api-keys")
        else:
            print("❌ .env.example not found")
            sys.exit(1)
    else:
        print("✅ .env file already exists")
    
    # Check if OpenAI API key is set
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.startswith("sk-"):
            print("✅ OpenAI API key found in .env")
        else:
            print("⚠️ OpenAI API key not set or invalid in .env file")
            print("   Please edit .env and add: OPENAI_API_KEY=sk-your-key-here")
    except ImportError:
        print("⚠️ Could not check API key (python-dotenv not available)")
    
    print("\n4. 🔧 Building RAG index...")
    if run_command("python scripts/build_rag_index.py", "Building RAG index"):
        print("✅ RAG index built successfully!")
    else:
        print("❌ Failed to build RAG index")
        print("Please check your OpenAI API key and try manually:")
        print("   python scripts/build_rag_index.py --check")
        sys.exit(1)
    
    print("\n5. 🧪 Testing RAG system...")
    if run_command("python scripts/build_rag_index.py --test", "Testing RAG system"):
        print("✅ RAG system test passed!")
    else:
        print("⚠️ RAG system test failed, but setup may still work")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the application: streamlit run app/streamlit_app.py")
    print("2. Navigate to the 🤖 AI Assistant page")
    print("3. Ask questions about Legal Metrology compliance")
    print("\n💡 Example questions:")
    print("   - 'Is MRP mandatory for e-commerce products?'")
    print("   - 'What units should be used for net quantity?'")
    print("   - 'How to improve OCR extraction accuracy?'")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
