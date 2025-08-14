#!/bin/bash

# Rudderstack SDET Assignment Framework Setup Script
# This script sets up the complete test automation framework

set -e  # Exit on any error

echo "🚀 Setting up Rudderstack SDET Assignment Framework..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p screenshots
    mkdir -p videos
    mkdir -p reports
    mkdir -p allure-results
    mkdir -p test-results
    
    print_success "Directories created successfully"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        print_success "Python dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    
    if [ -f "package.json" ]; then
        npm install
        print_success "Node.js dependencies installed successfully"
    else
        print_error "package.json not found"
        exit 1
    fi
}

# Install Playwright browsers
install_playwright() {
    print_status "Installing Playwright browsers..."
    
    if command -v npx &> /dev/null; then
        npx playwright install --with-deps
        print_success "Playwright browsers installed successfully"
    else
        print_warning "npx not found, skipping Playwright browser installation"
    fi
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success "Environment file created from template"
            print_warning "Please edit .env file with your Rudderstack credentials"
        else
            print_warning "env.example not found, creating basic .env file"
            cat > .env << EOF
# Rudderstack Credentials
RUDDERSTACK_EMAIL=your-business-email@domain.com
RUDDERSTACK_PASSWORD=your-password

# Environment URLs
DEV_URL=https://app.rudderstack.com
QA_URL=https://app.rudderstack.com
PROD_URL=https://app.rudderstack.com

# Current Environment
CURRENT_ENV=dev

# API Configuration
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3

# Test Configuration
HEADLESS_MODE=true
BROWSER_TIMEOUT=10000
EOF
        fi
    else
        print_warning ".env file already exists, skipping creation"
    fi
}

# Run initial tests
run_initial_tests() {
    print_status "Running initial test validation..."
    
    # Test Python imports
    if python3 -c "import pytest, selenium, requests" 2>/dev/null; then
        print_success "Python dependencies validation passed"
    else
        print_error "Python dependencies validation failed"
        exit 1
    fi
    
    # Test Node.js dependencies
    if node -e "console.log('Node.js is working')" 2>/dev/null; then
        print_success "Node.js validation passed"
    else
        print_error "Node.js validation failed"
        exit 1
    fi
}

# Display setup completion message
show_completion_message() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit the .env file with your Rudderstack credentials"
    echo "2. Create a Rudderstack account at https://app.rudderstack.com"
    echo "3. Set up an HTTP source and webhook destination"
    echo "4. Update the webhook URL in your .env file"
    echo ""
    echo "To run tests:"
    echo "  python3 -m pytest src/tests/ -v"
    echo "  npm run test"
    echo "  npx playwright test"
    echo ""
    echo "For more information, see the README.md file"
}

# Main setup function
main() {
    echo "=========================================="
    echo "  Rudderstack SDET Assignment Framework"
    echo "=========================================="
    echo ""
    
    check_python
    check_node
    create_directories
    install_python_deps
    install_node_deps
    install_playwright
    setup_env
    run_initial_tests
    show_completion_message
}

# Run main function
main "$@" 