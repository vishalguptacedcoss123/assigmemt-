# Automation Framework Usage Guide

This document provides comprehensive guidance on using the automation frameworks available in this codebase and how to run the automation scripts.

## 📁 Framework Overview

This repository contains two main automation frameworks:

### 1. **Rudderstack SDET Assignment Framework** (`assigment/`)
- **Type**: Hybrid automation framework (WebdriverIO + Playwright + Python/Pytest)
- **Purpose**: Testing Rudderstack flows and API integrations
- **Technologies**: Python, Selenium, Playwright, WebdriverIO, Node.js

### 2. **UI Automation Framework** (`ui_automation/`)
- **Type**: Playwright-based UI automation framework
- **Purpose**: General UI testing with Playwright TypeScript
- **Technologies**: Playwright, TypeScript, Node.js

---

## 🚀 Rudderstack SDET Assignment Framework

### Framework Architecture

```
assigment/
├── config/                 # Framework configuration files
│   ├── playwright.config.js
│   └── wdio.conf.js
├── src/
│   ├── pages/              # Page Object Model classes
│   │   ├── LoginPage.py
│   │   ├── ConnectionsPage.py
│   │   └── WebhookDestinationPage.py
│   ├── utils/              # Utility modules
│   │   ├── api_client.py
│   │   ├── config_manager.py
│   │   └── test_data.py
│   ├── tests/              # Test implementations
│   │   └── test_rudderstack_flows.py
│   └── main.py             # CLI entry point
├── scripts/
│   └── setup.sh            # Framework setup script
└── Configuration files
```

### Key Features

- **Multi-browser support** (Chrome, Firefox, Safari)
- **Environment management** (Dev, QA, Prod)
- **Page Object Model** implementation
- **API testing capabilities**
- **Comprehensive reporting** (HTML, Allure)
- **CI/CD integration** with GitHub Actions
- **SOLID design principles** implementation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Chrome/Firefox browser

### Setup Instructions

#### Method 1: Using Setup Script (Recommended)
```bash
cd assigment
chmod +x scripts/setup.sh
./scripts/setup.sh
```

#### Method 2: Manual Setup
```bash
# 1. Navigate to the project directory
cd assigment

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Node.js dependencies
npm install

# 4. Install Playwright browsers
npx playwright install --with-deps

# 5. Setup environment configuration
cp env.example .env
# Edit .env with your credentials
```

### Environment Configuration

Create a `.env` file with the following variables:

```env
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
```

### Running Tests

#### Using the CLI Framework (Recommended)
```bash
# Run all tests
python src/main.py run-tests

# Run smoke tests only
python src/main.py run-tests --smoke

# Run integration tests
python src/main.py run-tests --integration

# Run tests against specific environment
python src/main.py run-tests --env qa

# Run tests in headless mode
python src/main.py run-tests --headless

# Run tests with specific browser
python src/main.py run-tests --browser firefox

# Run tests in parallel
python src/main.py run-tests --parallel

# Run specific test scenario
python src/main.py run-tests --scenario "test_basic_flow"
```

#### Using Pytest Directly
```bash
# Run all tests
pytest src/tests/ -v

# Run with HTML report
pytest src/tests/ -v --html=reports/report.html --self-contained-html

# Run with Allure report
pytest src/tests/ -v --alluredir=allure-results
allure serve allure-results

# Run specific test
pytest src/tests/test_rudderstack_flows.py::test_rudderstack_basic_flow -v
```

#### Using WebdriverIO
```bash
# Run all WebdriverIO tests
npm run test

# Run tests in parallel
npm run test:parallel

# Run headless tests
npm run test:headless

# Run with specific browser
npm run test:chrome
npm run test:firefox
```

#### Using Playwright
```bash
# Run Playwright tests
npm run test:playwright

# Run with UI mode
npm run test:playwright:ui

# Run in headed mode
npm run test:playwright:headed
```

### Framework Utilities

#### Validate Configuration
```bash
python src/main.py validate-config
```

#### List Available Scenarios
```bash
python src/main.py list-scenarios
```

#### Framework Setup
```bash
python src/main.py setup
```

---

## 🎭 UI Automation Framework (Playwright)

### Framework Architecture

```
ui_automation/
├── tests/                  # Test files
│   └── example.spec.ts
├── test_sctipt_ui/        # Python UI tests
│   └── test_AddToCart.py
├── ui_pages/              # Page object files
├── playwright.config.ts   # Playwright configuration
└── package.json
```

### Prerequisites

- Node.js 16+
- Python 3.8+ (for Python tests)

### Setup Instructions

```bash
# 1. Navigate to the project directory
cd ui_automation

# 2. Install dependencies
npm install

# 3. Install Playwright browsers
npx playwright install
```

### Running Tests

#### TypeScript/JavaScript Tests
```bash
# Run all tests
npx playwright test

# Run tests in headed mode
npx playwright test --headed

# Run tests with UI mode
npx playwright test --ui

# Run specific test file
npx playwright test tests/example.spec.ts

# Run tests in specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Generate report
npx playwright show-report
```

#### Python Tests (e.g., Amazon Add to Cart)
```bash
# Set up Python environment (if not already done)
pip install pytest selenium

# Run Python UI tests
pytest test_sctipt_ui/test_AddToCart.py -v
```

### Playwright Configuration

The framework supports:
- **Multi-browser testing** (Chromium, Firefox, WebKit)
- **Parallel test execution**
- **HTML reporting**
- **Trace collection on failures**
- **Screenshot and video capture**

---

## 🛠 Automation Scripts

### Main Automation Scripts

#### 1. Framework Setup Script (`assigment/scripts/setup.sh`)
**Purpose**: Complete framework setup and validation

**Usage**:
```bash
cd assigment
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**What it does**:
- Checks Python and Node.js installation
- Creates necessary directories
- Installs Python dependencies
- Installs Node.js dependencies
- Installs Playwright browsers
- Sets up environment configuration
- Runs initial validation tests

#### 2. CLI Framework (`assigment/src/main.py`)
**Purpose**: Command-line interface for test execution and framework management

**Key Commands**:
```bash
# Test execution with various options
python src/main.py run-tests [OPTIONS]

# Configuration validation
python src/main.py validate-config

# List available scenarios
python src/main.py list-scenarios

# Framework setup
python src/main.py setup
```

#### 3. Package Scripts (npm)
**Rudderstack Framework** (`assigment/package.json`):
```bash
npm run test                 # Run WebdriverIO tests
npm run test:parallel        # Run tests in parallel
npm run test:headless        # Run headless tests
npm run test:playwright      # Run Playwright tests
npm run test:playwright:ui   # Run Playwright with UI
npm run install:browsers     # Install Playwright browsers
npm run report               # Generate Allure report
npm run lint                 # Run ESLint
```

**UI Automation** (`ui_automation/package.json`):
- Basic Playwright setup (scripts can be added as needed)

---

## 📊 Test Reports and Artifacts

### Available Report Types

1. **HTML Reports** (pytest)
   - Location: `reports/pytest-report.html`
   - Generated with: `pytest --html=reports/report.html`

2. **Allure Reports**
   - Location: `allure-results/`
   - Generated with: `pytest --alluredir=allure-results`
   - View with: `allure serve allure-results`

3. **Playwright Reports**
   - Generated automatically after test runs
   - View with: `npx playwright show-report`

### Artifacts

- **Screenshots**: Captured on test failures
- **Videos**: Available for Playwright tests
- **Traces**: Available for Playwright debugging
- **Logs**: Comprehensive logging with loguru

---

## 🔧 Advanced Usage

### Running Tests in Different Environments

```bash
# Development environment
python src/main.py run-tests --env dev

# QA environment
python src/main.py run-tests --env qa

# Production environment
python src/main.py run-tests --env prod
```

### Custom Test Execution

```bash
# Run specific test markers
pytest src/tests/ -m smoke
pytest src/tests/ -m integration
pytest src/tests/ -m regression

# Run tests with custom configuration
pytest src/tests/ --browser firefox --headless

# Run tests with parallel execution
pytest src/tests/ -n auto
```

### Debugging

```bash
# Run Playwright with debug mode
npx playwright test --debug

# Run single test with debugging
npx playwright test tests/example.spec.ts --debug

# Generate and view trace
npx playwright test --trace on
```

---

## 🚀 CI/CD Integration

The framework includes GitHub Actions workflow for:
- **Automated daily test execution**
- **Multi-environment testing**
- **Parallel test execution**
- **Test report generation**
- **Failure notifications**

Location: `.github/workflows/daily-tests.yml`

---

## 📝 Best Practices

1. **Environment Management**
   - Always use environment variables for sensitive data
   - Maintain separate configurations for different environments

2. **Test Data Management**
   - Use the test data generator for consistent test data
   - Implement data cleanup after tests

3. **Page Object Model**
   - Follow the existing POM structure
   - Keep page objects focused on single responsibility

4. **Error Handling**
   - Implement proper retry mechanisms
   - Use explicit waits instead of implicit waits
   - Capture screenshots on failures

5. **Reporting**
   - Use both HTML and Allure reports for comprehensive analysis
   - Include test artifacts (screenshots, videos, logs)

---

## 🤝 Support and Troubleshooting

### Common Issues

1. **Browser Installation Issues**
   ```bash
   npx playwright install --with-deps
   ```

2. **Python Dependencies Issues**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Node.js Dependencies Issues**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

### Validation Commands

```bash
# Validate framework configuration
python src/main.py validate-config

# Test Python imports
python -c "import pytest, selenium, requests, playwright"

# Test Node.js setup
node -e "console.log('Node.js is working')"

# Test Playwright installation
npx playwright test --list
```

### Getting Help

- Check the existing README files in each framework directory
- Use the validate-config command to identify configuration issues
- Review log files in the `logs/` directory
- Check test reports for detailed error information

This framework provides a robust foundation for automation testing with multiple technologies and comprehensive reporting capabilities.