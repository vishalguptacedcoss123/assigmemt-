"""
Pytest configuration file for Rudderstack test framework
Contains shared fixtures and configuration for all tests.
"""

import pytest
import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

# Configure logging
from loguru import logger
import logging

# Remove default handler and add custom one
logger.remove()
logger.add(
    "logs/test_execution.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)
logger.add(
    sys.stderr,
    level="INFO",
    format="{time:HH:mm:ss} | {level} | {message}"
)

# Suppress urllib3 warnings
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def test_environment():
    """Setup test environment configuration"""
    from utils.config_manager import config_manager
    
    # Validate environment configuration
    assert config_manager.settings.rudderstack_email, "Rudderstack email not configured"
    assert config_manager.settings.rudderstack_password, "Rudderstack password not configured"
    
    logger.info(f"Test environment: {config_manager.settings.current_env}")
    logger.info(f"Base URL: {config_manager.get_environment_url()}")
    
    return {
        'environment': config_manager.settings.current_env,
        'base_url': config_manager.get_environment_url(),
        'headless': config_manager.browser_config.headless,
        'timeout': config_manager.browser_config.timeout
    }


@pytest.fixture(scope="session")
def test_data_manager():
    """Setup test data manager"""
    from utils.test_data import test_scenario_manager, test_data_generator
    
    logger.info("Test data manager initialized")
    return {
        'scenario_manager': test_scenario_manager,
        'data_generator': test_data_generator
    }


@pytest.fixture(scope="session")
def api_client_instance():
    """Setup API client instance"""
    from utils.api_client import api_client
    
    logger.info("API client initialized")
    return api_client


@pytest.fixture(scope="function")
def test_logger():
    """Setup test-specific logger"""
    test_name = pytest.current_test.name if hasattr(pytest, 'current_test') else 'unknown'
    logger.info(f"Starting test: {test_name}")
    
    yield logger
    
    logger.info(f"Completed test: {test_name}")


@pytest.fixture(scope="function")
def screenshot_on_failure(request):
    """Take screenshot on test failure"""
    yield
    
    if request.node.rep_call.failed:
        try:
            from selenium import webdriver
            driver = request.getfixturevalue('driver')
            if driver:
                timestamp = int(time.time())
                screenshot_path = f"screenshots/failure_{request.node.name}_{timestamp}.png"
                driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")


# Pytest hooks
def pytest_runtest_setup(item):
    """Setup before each test"""
    logger.info(f"Setting up test: {item.name}")


def pytest_runtest_teardown(item, nextitem):
    """Cleanup after each test"""
    logger.info(f"Tearing down test: {item.name}")


def pytest_runtest_logreport(report):
    """Handle test report logging"""
    if report.when == 'call':
        if report.passed:
            logger.info(f"✓ Test passed: {report.nodeid}")
        elif report.failed:
            logger.error(f"✗ Test failed: {report.nodeid}")
            if report.longrepr:
                logger.error(f"Error details: {report.longrepr}")
        elif report.skipped:
            logger.warning(f"⚠ Test skipped: {report.nodeid}")


# Custom markers
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers and options"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "smoke: marks tests as smoke tests"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add markers based on test names
        if "basic_flow" in item.name:
            item.add_marker(pytest.mark.smoke)
            item.add_marker(pytest.mark.integration)
        elif "event_tracking" in item.name:
            item.add_marker(pytest.mark.regression)
        elif "error_handling" in item.name:
            item.add_marker(pytest.mark.regression)
        elif "webhook" in item.name:
            item.add_marker(pytest.mark.integration)


# Environment-specific configurations
def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Environment to test against (dev, qa, prod)"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run tests in headless mode"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to use for testing (chrome, firefox, safari)"
    )


@pytest.fixture(scope="session")
def cmdopt(request):
    """Get command line options"""
    return {
        'env': request.config.getoption("--env"),
        'headless': request.config.getoption("--headless"),
        'browser': request.config.getoption("--browser")
    } 