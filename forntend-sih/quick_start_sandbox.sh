#!/bin/bash

# Quick Start Script for Sandbox API Testing
# Legal Metrology Compliance System

echo "🚀 Quick Start: Sandbox API Testing"
echo "===================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "app/streamlit_app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_info "Starting sandbox environment setup..."

# Step 1: Check Python version
echo -e "\n📋 Step 1: Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    print_status "Python detected: $python_version"
else
    print_error "Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi

# Step 2: Check virtual environment
echo -e "\n📋 Step 2: Checking virtual environment..."
if [ -d "venv" ]; then
    print_status "Virtual environment found"
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        source venv/Scripts/activate
    else
        # Unix/Linux/macOS
        source venv/bin/activate
    fi
    print_status "Virtual environment activated"
else
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv venv
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    print_status "Virtual environment created and activated"
fi

# Step 3: Install dependencies
echo -e "\n📋 Step 3: Installing dependencies..."
if [ -f "requirements.txt" ]; then
    print_info "Installing packages from requirements.txt..."
    pip install -r requirements.txt > /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        print_status "Dependencies installed successfully"
    else
        print_warning "Some dependencies may have failed to install"
        print_info "Running pip install anyway..."
        pip install streamlit pandas numpy pillow requests beautifulsoup4 selenium
    fi
else
    print_error "requirements.txt not found"
    exit 1
fi

# Step 4: Check data directories
echo -e "\n📋 Step 4: Checking data directories..."
directories=("app/data" "app/data/uploads" "app/data/reports" "app/data/crawled")

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        print_status "Directory exists: $dir"
    else
        print_warning "Creating directory: $dir"
        mkdir -p "$dir"
    fi
done

# Step 5: Set environment variables
echo -e "\n📋 Step 5: Setting environment variables..."
export SANDBOX_MODE=true
export PYTHONPATH="$PWD/app:$PYTHONPATH"
print_status "Environment variables set"

# Step 6: Start Streamlit application in background
echo -e "\n📋 Step 6: Starting Streamlit application..."
print_info "Launching Streamlit on http://localhost:8501"

# Kill any existing Streamlit processes
pkill -f streamlit > /dev/null 2>&1

# Start Streamlit in background
nohup streamlit run app/streamlit_app.py --server.port=8501 --server.address=localhost > streamlit.log 2>&1 &
STREAMLIT_PID=$!

print_status "Streamlit started (PID: $STREAMLIT_PID)"
print_info "Waiting for application to start..."

# Wait for Streamlit to start
sleep 10

# Check if Streamlit is running
if curl -s http://localhost:8501 > /dev/null; then
    print_status "Streamlit application is running"
else
    print_error "Failed to start Streamlit application"
    print_info "Check streamlit.log for details"
    exit 1
fi

# Step 7: Run API tests
echo -e "\n📋 Step 7: Running API tests..."
print_info "Executing comprehensive API tests..."

python3 test_sandbox_api.py

TEST_EXIT_CODE=$?

# Step 8: Show results
echo -e "\n📋 Step 8: Test Results"
echo "======================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_status "All tests completed successfully!"
    echo -e "\n🎉 ${GREEN}Your sandbox API is ready for testing!${NC}"
    
    echo -e "\n📱 Quick Access Links:"
    echo "• Main Application: http://localhost:8501"
    echo "• Dashboard: http://localhost:8501/📊_Dashboard"
    echo "• API Testing: http://localhost:8501/🔍_Extraction"
    echo "• Web Crawler: http://localhost:8501/🌐_Web_Crawler"
    echo "• Help: http://localhost:8501/❓_Help"
    
else
    print_warning "Some tests failed. Check the output above for details."
    echo -e "\n🔧 ${YELLOW}Your system needs some attention before full testing.${NC}"
fi

# Step 9: Provide next steps
echo -e "\n📋 Next Steps:"
echo "=============="
echo "1. Open your browser to http://localhost:8501"
echo "2. Navigate to different pages to test functionality"
echo "3. Upload test images in the Extraction page"
echo "4. Try the Web Crawler with sample queries"
echo "5. Check the Dashboard for analytics"
echo "6. Use the AI Assistant for compliance questions"

echo -e "\n📖 Documentation:"
echo "• Full Testing Guide: SANDBOX_API_TESTING_GUIDE.md"
echo "• Technical Docs: TECHNICAL_DOCUMENTATION.md"
echo "• Setup Guide: FINAL_SETUP_GUIDE.md"

echo -e "\n🛑 To Stop the Server:"
echo "• Kill Streamlit process: kill $STREAMLIT_PID"
echo "• Or use: pkill -f streamlit"

echo -e "\n🔍 Troubleshooting:"
echo "• Check logs: tail -f streamlit.log"
echo "• Test connectivity: curl http://localhost:8501"
echo "• Restart: ./quick_start_sandbox.sh"

print_status "Sandbox setup complete!"

# Keep the script running to show PID
echo -e "\n⏳ Streamlit is running in background (PID: $STREAMLIT_PID)"
echo "Press Ctrl+C to stop this script (Streamlit will continue running)"

# Wait for user to stop
trap "print_info 'Script stopped. Streamlit is still running.'; exit 0" INT
while true; do
    sleep 1
done
