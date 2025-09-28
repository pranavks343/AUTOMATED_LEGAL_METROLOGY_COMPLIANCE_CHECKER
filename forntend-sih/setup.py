"""
Setup script for Legal Metrology Compliance Checker
Automated system setup and configuration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("🏛️ LEGAL METROLOGY COMPLIANCE CHECKER - SYSTEM SETUP")
    print("=" * 70)
    print("Enhanced Enterprise Edition - Government Ready")
    print("Version: 2.0")
    print("Date: September 2025")
    print("=" * 70)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9+ is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]} (Compatible)")
    return True

def check_system_dependencies():
    """Check for system dependencies"""
    print("\n📋 Checking system dependencies...")
    
    dependencies = {
        'tesseract': 'Tesseract OCR',
        'chromium': 'Chromium browser (for web crawling)',
        'git': 'Git version control'
    }
    
    missing_deps = []
    
    for cmd, desc in dependencies.items():
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {desc}: Available")
            else:
                missing_deps.append((cmd, desc))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing_deps.append((cmd, desc))
    
    if missing_deps:
        print("\n⚠️ Missing system dependencies:")
        for cmd, desc in missing_deps:
            print(f"   - {desc} ({cmd})")
        
        print("\nInstallation instructions:")
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            print("macOS (using Homebrew):")
            print("  brew install tesseract tesseract-lang")
            print("  brew install --cask google-chrome")
            print("  brew install chromedriver")
        elif system == 'linux':  # Linux
            print("Ubuntu/Debian:")
            print("  sudo apt-get update")
            print("  sudo apt-get install tesseract-ocr tesseract-ocr-hin tesseract-ocr-ben")
            print("  sudo apt-get install chromium-browser chromium-chromedriver")
        elif system == 'windows':  # Windows
            print("Windows:")
            print("  1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("  2. Install Chrome browser")
            print("  3. Download ChromeDriver and add to PATH")
        
        return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, timeout=300)
        
        # Install requirements
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, timeout=600)
        
        print("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out. Please try again.")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directory structure...")
    
    directories = [
        'app/data/uploads',
        'app/data/reports',
        'app/data/crawled',
        'app/data/processed',
        'app/data/faiss_index',
        'app/data/sample_dataset/images',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def setup_environment():
    """Setup environment configuration"""
    print("\n⚙️ Setting up environment configuration...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("📄 Copying .env.example to .env")
            env_file.write_text(env_example.read_text())
        else:
            print("📄 Creating default .env file")
            env_content = """# Legal Metrology Compliance Checker Configuration
OPENAI_API_KEY=your-openai-api-key-here
DEBUG=false
LOG_LEVEL=INFO
"""
            env_file.write_text(env_content)
        
        print("✅ Environment file created")
        print("⚠️ Please edit .env file with your actual configuration values")
    else:
        print("✅ Environment file already exists")

def initialize_rag_system():
    """Initialize RAG system"""
    print("\n🤖 Initializing RAG system...")
    
    try:
        # Check if FAISS index exists
        faiss_path = Path('app/data/faiss_index/faiss.index')
        
        if not faiss_path.exists():
            print("📚 Building RAG knowledge index...")
            subprocess.run([sys.executable, 'scripts/build_rag_index.py'], 
                          check=True, timeout=300)
            print("✅ RAG system initialized")
        else:
            print("✅ RAG system already initialized")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ RAG initialization failed: {e}")
        print("You can manually run: python scripts/build_rag_index.py")
        return False
    except FileNotFoundError:
        print("⚠️ RAG build script not found, skipping...")
        return False

def run_system_test():
    """Run basic system test"""
    print("\n🧪 Running system tests...")
    
    try:
        # Test configuration
        result = subprocess.run([sys.executable, 'test_secrets_config.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ System configuration test passed")
            return True
        else:
            print("⚠️ System configuration test failed")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("⚠️ Test script not found, skipping...")
        return True
    except subprocess.TimeoutExpired:
        print("⚠️ Test timed out, skipping...")
        return True

def print_next_steps():
    """Print next steps for user"""
    print("\n" + "=" * 70)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. 🔑 Configure your API keys in the .env file:")
    print("   - Add your OpenAI API key for the RAG chatbot")
    print("   - Add barcode API keys if needed (optional)")
    print()
    print("2. 🚀 Start the application:")
    print("   streamlit run app/streamlit_app.py")
    print()
    print("3. 🌐 Access the application:")
    print("   Open your browser to: http://localhost:8501")
    print()
    print("4. 🔐 Login credentials:")
    print("   Admin: admin / admin123")
    print("   User: user / user123")
    print()
    print("📚 DOCUMENTATION:")
    print("   - Technical Documentation: TECHNICAL_DOCUMENTATION.md")
    print("   - Feasibility Report: GOVERNMENT_DEPLOYMENT_FEASIBILITY_REPORT.md")
    print("   - System Summary: COMPLETE_SYSTEM_ENHANCEMENT_SUMMARY.md")
    print()
    print("🆘 SUPPORT:")
    print("   - Check the Help page in the application")
    print("   - Review troubleshooting section in technical docs")
    print()
    print("=" * 70)
    print("✨ Ready for Legal Metrology Compliance Checking! ✨")
    print("=" * 70)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check system dependencies
    if not check_system_dependencies():
        print("\n⚠️ Please install missing system dependencies and run setup again.")
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("\n❌ Failed to install Python dependencies.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Initialize RAG system
    initialize_rag_system()
    
    # Run system test
    run_system_test()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
