# Rudderstack SDET Assignment Framework

This repository contains a comprehensive test automation framework for testing Rudderstack flows using WebdriverIO with Playwright, Python, and Selenium.

## 🚀 Features

- **Multi-browser support** with WebdriverIO and Playwright
- **Environment management** with .env files for dev, qa, and production
- **SOLID design principles** implementation
- **Comprehensive test coverage** for Rudderstack flows
- **GitHub Actions** for automated daily test execution
- **Proper project structure** with configuration files
- **Edge case handling** and error management

## 📁 Project Structure

```
assigment/
├── .github/
│   └── workflows/
│       └── daily-tests.yml
├── config/
│   ├── wdio.conf.js
│   └── playwright.config.js
├── src/
│   ├── pages/
│   │   ├── LoginPage.py
│   │   ├── DashboardPage.py
│   │   ├── ConnectionsPage.py
│   │   └── WebhookDestinationPage.py
│   ├── utils/
│   │   ├── api_client.py
│   │   ├── config_manager.py
│   │   └── test_data.py
│   └── tests/
│       ├── test_rudderstack_flows.py
│       └── conftest.py
├── .env.example
├── requirements.txt
├── package.json
├── tsconfig.json
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- Chrome/Firefox browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd assigment
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your Rudderstack credentials
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Rudderstack Credentials
RUDDERSTACK_EMAIL=your-business-email@domain.com
RUDDERSTACK_PASSWORD=your-password

# Environment URLs
DEV_URL=https://app.rudderstack.com
QA_URL=https://app.rudderstack.com
PROD_URL=https://app.rudderstack.com

# API Configuration
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3

# Test Configuration
HEADLESS_MODE=true
BROWSER_TIMEOUT=10000
```

## 🧪 Running Tests

### WebdriverIO Tests
```bash
# Run all tests
npm run test

# Run specific test file
npm run test -- --spec src/tests/test_rudderstack_flows.py

# Run tests in parallel
npm run test:parallel
```

### Python Tests with pytest
```bash
# Run all tests
pytest src/tests/

# Run with verbose output
pytest -v src/tests/

# Run specific test
pytest src/tests/test_rudderstack_flows.py::test_rudderstack_basic_flow
```

### Playwright Tests
```bash
# Run Playwright tests
npx playwright test

# Run with UI mode
npx playwright test --ui
```

## 📋 Test Scenarios

### 1. Manual Setup Verification
- [x] Rudderstack account signup with business email
- [x] HTTP source creation
- [x] Webhook destination creation
- [x] RequestCatcher webhook URL setup

### 2. Automation Test Cases
- [x] Login to Rudderstack application
- [x] Navigate to connections page
- [x] Extract data plane URL
- [x] Extract HTTP source write key
- [x] Send API event to HTTP source
- [x] Navigate to webhook destination
- [x] Verify event delivery counts

## 🔧 Framework Components

### Page Object Model
- **LoginPage**: Handles authentication
- **DashboardPage**: Main dashboard interactions
- **ConnectionsPage**: Source and destination management
- **WebhookDestinationPage**: Webhook-specific operations

### Utilities
- **APIClient**: HTTP API interactions
- **ConfigManager**: Environment configuration
- **TestData**: Test data management

### Configuration
- **WebdriverIO**: Browser automation setup
- **Playwright**: Alternative browser automation
- **Pytest**: Test execution framework

## 🚀 GitHub Actions

The framework includes a GitHub Actions workflow that:
- Runs tests daily at 2:00 AM UTC
- Supports multiple environments (dev, qa, prod)
- Generates test reports
- Sends notifications on failures

## 📊 Test Reports

Test execution generates:
- HTML test reports
- Screenshots on failures
- Console logs
- Performance metrics

## 🛡️ Error Handling

- **Retry mechanisms** for flaky tests
- **Screenshot capture** on failures
- **Detailed logging** for debugging
- **Graceful degradation** for API failures

## 🔍 Edge Cases Covered

- Network timeouts
- Invalid credentials
- Missing elements
- API rate limiting
- Browser compatibility issues

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🤝 Support

For questions or issues, please create an issue in the repository. 