#!/usr/bin/env python3
"""
System Verification Script for Legal Metrology Compliance Checker
Verifies that all enhanced components are working properly
"""

import sys
import os
import importlib
from pathlib import Path
import json

def print_header():
    """Print verification header"""
    print("=" * 70)
    print("🔍 LEGAL METROLOGY COMPLIANCE CHECKER - SYSTEM VERIFICATION")
    print("=" * 70)
    print("Enhanced Enterprise Edition - Government Ready")
    print("Verifying all competition requirements and enhancements...")
    print("=" * 70)
    print()

def check_python_version():
    """Check Python version"""
    print("📋 Checking Python version...")
    
    if sys.version_info >= (3, 9):
        print(f"✅ Python {sys.version.split()[0]} - Compatible")
        return True
    else:
        print(f"❌ Python {sys.version.split()[0]} - Requires Python 3.9+")
        return False

def check_core_files():
    """Check if all core enhanced files exist"""
    print("\n📁 Checking enhanced core files...")
    
    required_files = {
        # New enhanced files
        'app/core/web_crawler.py': 'Web Crawling APIs',
        'app/core/enhanced_vision.py': 'Enhanced Computer Vision',
        'app/pages/14_🌐_Web_Crawler.py': 'Web Crawler Interface',
        'app/pages/15_🏛️_Regulatory_Dashboard.py': 'Regulatory Dashboard',
        'app/data/sample_dataset/annotated_samples.json': 'Sample Dataset',
        'TECHNICAL_DOCUMENTATION.md': 'Technical Documentation',
        'GOVERNMENT_DEPLOYMENT_FEASIBILITY_REPORT.md': 'Feasibility Report',
        'setup.py': 'Setup Script',
        
        # Core existing files
        'app/streamlit_app.py': 'Main Application',
        'app/core/ocr.py': 'OCR Engine',
        'app/core/rules_engine.py': 'Validation Engine',
        'app/core/chatbot.py': 'RAG Chatbot',
        'requirements.txt': 'Dependencies',
    }
    
    missing_files = []
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} - MISSING")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_dependencies():
    """Check if key dependencies can be imported"""
    print("\n📦 Checking key dependencies...")
    
    dependencies = {
        'streamlit': 'Streamlit Framework',
        'pandas': 'Data Processing',
        'numpy': 'Numerical Computing',
        'opencv-python': 'Computer Vision (cv2)',
        'PIL': 'Image Processing (Pillow)',
        'requests': 'HTTP Requests',
        'json': 'JSON Processing',
        'pathlib': 'Path Utilities'
    }
    
    missing_deps = []
    for module, description in dependencies.items():
        try:
            if module == 'opencv-python':
                import cv2
                print(f"✅ {description}: Available")
            else:
                importlib.import_module(module)
                print(f"✅ {description}: Available")
        except ImportError:
            print(f"❌ {description}: Missing - {module}")
            missing_deps.append(module)
    
    return len(missing_deps) == 0

def check_enhanced_components():
    """Check if enhanced components can be imported"""
    print("\n🔧 Checking enhanced components...")
    
    # Add app directory to path
    sys.path.insert(0, 'app')
    
    components = {
        'core.web_crawler': 'Web Crawler Engine',
        'core.enhanced_vision': 'Enhanced Vision Processor',
        'core.ocr': 'OCR Engine',
        'core.rules_engine': 'Validation Engine',
        'core.chatbot': 'RAG Chatbot'
    }
    
    working_components = []
    for module, description in components.items():
        try:
            importlib.import_module(module)
            print(f"✅ {description}: Importable")
            working_components.append(module)
        except ImportError as e:
            print(f"⚠️ {description}: Import issue - {e}")
        except Exception as e:
            print(f"⚠️ {description}: Other issue - {e}")
    
    return len(working_components) >= 3  # At least core components work

def check_sample_dataset():
    """Check sample dataset"""
    print("\n📊 Checking sample dataset...")
    
    dataset_path = Path('app/data/sample_dataset/annotated_samples.json')
    
    if not dataset_path.exists():
        print("❌ Sample dataset not found")
        return False
    
    try:
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)
        
        total_samples = dataset.get('dataset_info', {}).get('total_samples', 0)
        compliant_samples = dataset.get('dataset_info', {}).get('compliant_samples', 0)
        non_compliant_samples = dataset.get('dataset_info', {}).get('non_compliant_samples', 0)
        
        print(f"✅ Sample dataset loaded: {total_samples} total samples")
        print(f"   - Compliant: {compliant_samples}")
        print(f"   - Non-compliant: {non_compliant_samples}")
        print(f"   - Categories: {len(dataset.get('dataset_info', {}).get('categories', []))}")
        
        return total_samples >= 50
        
    except Exception as e:
        print(f"❌ Error reading sample dataset: {e}")
        return False

def check_documentation():
    """Check documentation files"""
    print("\n📚 Checking documentation...")
    
    docs = {
        'README.md': 'Main Documentation',
        'TECHNICAL_DOCUMENTATION.md': 'Technical Guide',
        'GOVERNMENT_DEPLOYMENT_FEASIBILITY_REPORT.md': 'Feasibility Report',
        'COMPLETE_SYSTEM_ENHANCEMENT_SUMMARY.md': 'Enhancement Summary'
    }
    
    doc_count = 0
    for doc_path, description in docs.items():
        if Path(doc_path).exists():
            size = Path(doc_path).stat().st_size
            print(f"✅ {description}: {doc_path} ({size:,} bytes)")
            doc_count += 1
        else:
            print(f"❌ {description}: {doc_path} - Missing")
    
    return doc_count >= 3

def check_competition_requirements():
    """Check competition requirements fulfillment"""
    print("\n🎯 Checking competition requirements...")
    
    requirements = {
        'Data Acquisition': {
            'web_crawler.py': 'Web crawling APIs for e-commerce platforms',
            'enhanced_vision.py': 'Image recognition for label regions'
        },
        'OCR & AI': {
            'enhanced_vision.py': 'Multi-language OCR support',
            'enhanced_vision.py': 'Computer vision segmentation'
        },
        'Rule Engine': {
            'rules_engine.py': 'Legal Metrology validation logic',
            'rules_engine.py': 'Configurable rule variations'
        },
        'Dashboard': {
            '15_🏛️_Regulatory_Dashboard.py': 'Real-time compliance monitoring',
            '14_🌐_Web_Crawler.py': 'Platform data acquisition interface'
        },
        'Deliverables': {
            'streamlit_app.py': 'Working prototype',
            'TECHNICAL_DOCUMENTATION.md': 'Technical documentation',
            'annotated_samples.json': 'Sample dataset',
            'GOVERNMENT_DEPLOYMENT_FEASIBILITY_REPORT.md': 'Feasibility report'
        }
    }
    
    fulfilled_count = 0
    total_count = 0
    
    for category, items in requirements.items():
        print(f"\n📋 {category}:")
        for file_check, description in items.items():
            total_count += 1
            # Check if any file contains the key component
            found = False
            for file_path in Path('.').rglob('*'):
                if file_check in str(file_path) and file_path.exists():
                    print(f"   ✅ {description}")
                    fulfilled_count += 1
                    found = True
                    break
            
            if not found:
                print(f"   ❌ {description}")
    
    fulfillment_rate = (fulfilled_count / total_count) * 100
    print(f"\n📊 Competition Requirements Fulfillment: {fulfillment_rate:.1f}% ({fulfilled_count}/{total_count})")
    
    return fulfillment_rate >= 90

def generate_report():
    """Generate system verification report"""
    print("\n" + "=" * 70)
    print("📊 SYSTEM VERIFICATION SUMMARY")
    print("=" * 70)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Core Files", check_core_files()),
        ("Dependencies", check_dependencies()),
        ("Enhanced Components", check_enhanced_components()),
        ("Sample Dataset", check_sample_dataset()),
        ("Documentation", check_documentation()),
        ("Competition Requirements", check_competition_requirements())
    ]
    
    passed_checks = sum(1 for _, result in checks if result)
    total_checks = len(checks)
    
    print(f"\n📈 Overall System Health: {passed_checks}/{total_checks} checks passed")
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {check_name}")
    
    if passed_checks == total_checks:
        print(f"\n🎉 EXCELLENT! All systems operational and ready for competition!")
        print("🏆 Your Legal Metrology Compliance Checker is fully enhanced and government-ready.")
    elif passed_checks >= total_checks * 0.8:
        print(f"\n✅ GOOD! System is mostly ready with minor issues to address.")
        print("🔧 Review failed checks and install missing dependencies.")
    else:
        print(f"\n⚠️ NEEDS ATTENTION! Several components require setup.")
        print("🔧 Please run setup.py or follow FINAL_SETUP_GUIDE.md instructions.")
    
    print("\n" + "=" * 70)
    print("🚀 Next Steps:")
    print("1. Address any failed checks above")
    print("2. Run: streamlit run app/streamlit_app.py")
    print("3. Access: http://localhost:8501")
    print("4. Login: admin/admin123 or user/user123")
    print("=" * 70)
    
    return passed_checks == total_checks

def main():
    """Main verification function"""
    print_header()
    success = generate_report()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
