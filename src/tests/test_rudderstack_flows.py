"""
Main test file for Rudderstack flows
Implements comprehensive test scenarios following pytest conventions and SOLID principles.
"""

import pytest
import time
from typing import Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger

from ..pages.LoginPage import LoginPage
from ..pages.ConnectionsPage import ConnectionsPage
from ..pages.WebhookDestinationPage import WebhookDestinationPage
from ..utils.config_manager import config_manager
from ..utils.api_client import api_client, APIFactory
from ..utils.test_data import test_data_generator, test_scenario_manager, test_data_validator


class TestRudderstackFlows:
    """
    Test class for Rudderstack flows
    Implements comprehensive test scenarios with proper setup and teardown
    """
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup WebDriver for all tests"""
        try:
            # Configure Chrome options
            chrome_options = Options()
            
            if config_manager.browser_config.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Setup Chrome driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configure timeouts
            driver.implicitly_wait(config_manager.browser_config.implicit_wait)
            driver.set_page_load_timeout(config_manager.browser_config.page_load_timeout)
            
            logger.info("WebDriver setup completed")
            yield driver
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            raise
        finally:
            try:
                driver.quit()
                logger.info("WebDriver cleanup completed")
            except Exception as e:
                logger.error(f"Failed to cleanup WebDriver: {str(e)}")
    
    @pytest.fixture(scope="class")
    def login_page(self, driver):
        """Setup login page object"""
        return LoginPage(driver)
    
    @pytest.fixture(scope="class")
    def connections_page(self, driver):
        """Setup connections page object"""
        return ConnectionsPage(driver)
    
    @pytest.fixture(scope="class")
    def webhook_page(self, driver):
        """Setup webhook destination page object"""
        return WebhookDestinationPage(driver)
    
    @pytest.fixture(scope="class")
    def test_data(self):
        """Setup test data for all tests"""
        return test_scenario_manager.create_test_data_for_scenario('basic_flow')
    
    def test_rudderstack_basic_flow(self, driver, login_page, connections_page, webhook_page, test_data):
        """
        Test the complete basic Rudderstack flow
        
        This test implements the complete automation flow as specified in the assignment:
        1. Login to Rudderstack application
        2. Navigate to connections page
        3. Extract data plane URL
        4. Extract HTTP source write key
        5. Send API event to HTTP source
        6. Navigate to webhook destination
        7. Verify event delivery counts
        """
        logger.info("Starting basic Rudderstack flow test")
        
        # Test data
        credentials = config_manager.get_credentials()
        webhook_url = config_manager.get_webhook_url()
        
        # Step 1: Login to Rudderstack application
        logger.info("Step 1: Logging in to Rudderstack application")
        assert login_page.login(credentials['email'], credentials['password']), \
            "Login to Rudderstack failed"
        
        # Verify login success
        assert login_page.is_logged_in(), "User is not logged in after login attempt"
        logger.info("✓ Login successful")
        
        # Step 2: Navigate to connections page
        logger.info("Step 2: Navigating to connections page")
        connections_page.navigate_to_connections()
        assert connections_page.is_page_loaded(), "Connections page failed to load"
        logger.info("✓ Successfully navigated to connections page")
        
        # Step 3: Extract data plane URL
        logger.info("Step 3: Extracting data plane URL")
        data_plane_url = connections_page.get_data_plane_url()
        assert data_plane_url is not None, "Failed to extract data plane URL"
        assert data_plane_url.startswith('http'), "Data plane URL is not a valid HTTP URL"
        logger.info(f"✓ Extracted data plane URL: {data_plane_url}")
        
        # Step 4: Extract HTTP source write key
        logger.info("Step 4: Extracting HTTP source write key")
        write_key = connections_page.get_http_source_write_key()
        assert write_key is not None, "Failed to extract HTTP source write key"
        assert len(write_key) > 0, "Write key is empty"
        logger.info(f"✓ Extracted write key: {write_key[:10]}...")
        
        # Step 5: Send API event to HTTP source
        logger.info("Step 5: Sending API event to HTTP source")
        
        # Create test event using EventBuilder
        event_builder = APIFactory.create_event_builder()
        test_event = event_builder \
            .set_event_name("test_event") \
            .set_user_id("test_user_123") \
            .add_property("test_property", "test_value") \
            .add_property("timestamp", int(time.time())) \
            .build()
        
        # Send event via API
        api_response = api_client.send_event(test_event, write_key, data_plane_url)
        assert api_response['success'], f"Failed to send event: {api_response.get('error', 'Unknown error')}"
        logger.info(f"✓ Event sent successfully. Status: {api_response['status_code']}")
        
        # Step 6: Navigate to webhook destination
        logger.info("Step 6: Navigating to webhook destination")
        assert connections_page.click_webhook_destination(), "Failed to click webhook destination"
        assert webhook_page.is_page_loaded(), "Webhook destination page failed to load"
        logger.info("✓ Successfully navigated to webhook destination")
        
        # Step 7: Verify event delivery counts
        logger.info("Step 7: Verifying event delivery counts")
        
        # Wait for event to be processed
        time.sleep(5)  # Give some time for event processing
        
        # Get event counts
        event_counts = webhook_page.get_event_counts()
        assert event_counts['total'] > 0, "No events found in webhook destination"
        
        # Verify delivery
        assert event_counts['delivered'] > 0, "No events were delivered successfully"
        logger.info(f"✓ Event delivery verified - Delivered: {event_counts['delivered']}, Failed: {event_counts['failed']}")
        
        # Additional verification: Check delivery stats
        delivery_stats = webhook_page.get_delivery_stats()
        assert delivery_stats['success_rate'] > 0, "Success rate should be greater than 0"
        logger.info(f"✓ Delivery stats - Success rate: {delivery_stats['success_rate']}%")
        
        logger.info("✓ Basic Rudderstack flow test completed successfully")
    
    def test_event_tracking_scenario(self, driver, login_page, connections_page, webhook_page, test_data):
        """
        Test event tracking with multiple events and properties
        """
        logger.info("Starting event tracking scenario test")
        
        # Login and setup
        credentials = config_manager.get_credentials()
        assert login_page.login(credentials['email'], credentials['password']), "Login failed"
        
        connections_page.navigate_to_connections()
        data_plane_url = connections_page.get_data_plane_url()
        write_key = connections_page.get_http_source_write_key()
        
        assert data_plane_url and write_key, "Failed to get required configuration"
        
        # Send multiple test events
        event_types = ['page_view', 'product_viewed', 'add_to_cart', 'purchase']
        sent_events = []
        
        for event_type in event_types:
            event_builder = APIFactory.create_event_builder()
            test_event = event_builder \
                .set_event_name(event_type) \
                .set_user_id(f"test_user_{int(time.time())}") \
                .add_properties(test_data_generator.generate_event(event_name=event_type).properties) \
                .build()
            
            api_response = api_client.send_event(test_event, write_key, data_plane_url)
            assert api_response['success'], f"Failed to send {event_type} event"
            sent_events.append(test_event)
            logger.info(f"✓ Sent {event_type} event")
        
        # Navigate to webhook and verify delivery
        connections_page.click_webhook_destination()
        webhook_page.click_events_tab()
        
        # Wait for events to be processed
        time.sleep(10)
        
        # Verify all events were delivered
        event_counts = webhook_page.get_event_counts()
        assert event_counts['delivered'] >= len(sent_events), \
            f"Expected {len(sent_events)} delivered events, got {event_counts['delivered']}"
        
        logger.info(f"✓ Event tracking test completed - {event_counts['delivered']} events delivered")
    
    def test_error_handling_scenarios(self, driver, login_page, connections_page, webhook_page, test_data):
        """
        Test error handling scenarios and edge cases
        """
        logger.info("Starting error handling scenarios test")
        
        # Test invalid credentials
        logger.info("Testing invalid credentials")
        invalid_login_result = login_page.login("invalid@email.com", "wrongpassword")
        assert not invalid_login_result, "Login should fail with invalid credentials"
        
        # Test with valid credentials
        credentials = config_manager.get_credentials()
        assert login_page.login(credentials['email'], credentials['password']), "Valid login failed"
        
        # Test invalid write key
        logger.info("Testing invalid write key")
        connections_page.navigate_to_connections()
        data_plane_url = connections_page.get_data_plane_url()
        
        if data_plane_url:
            invalid_event = {"event": "test_event", "userId": "test_user"}
            invalid_response = api_client.send_event(invalid_event, "invalid_write_key", data_plane_url)
            assert not invalid_response['success'], "API call should fail with invalid write key"
        
        # Test malformed event
        logger.info("Testing malformed event")
        if data_plane_url:
            write_key = connections_page.get_http_source_write_key()
            if write_key:
                malformed_event = {"invalid": "event"}
                malformed_response = api_client.send_event(malformed_event, write_key, data_plane_url)
                # Note: This might still succeed depending on API validation
                logger.info(f"Malformed event response: {malformed_response}")
        
        logger.info("✓ Error handling scenarios test completed")
    
    def test_webhook_delivery_verification(self, driver, login_page, connections_page, webhook_page, test_data):
        """
        Test comprehensive webhook delivery verification
        """
        logger.info("Starting webhook delivery verification test")
        
        # Setup
        credentials = config_manager.get_credentials()
        assert login_page.login(credentials['email'], credentials['password']), "Login failed"
        
        connections_page.navigate_to_connections()
        data_plane_url = connections_page.get_data_plane_url()
        write_key = connections_page.get_http_source_write_key()
        
        assert data_plane_url and write_key, "Failed to get required configuration"
        
        # Navigate to webhook destination
        connections_page.click_webhook_destination()
        webhook_page.click_events_tab()
        
        # Get initial counts
        initial_counts = webhook_page.get_event_counts()
        logger.info(f"Initial event counts: {initial_counts}")
        
        # Send test event
        event_builder = APIFactory.create_event_builder()
        test_event = event_builder \
            .set_event_name("webhook_test_event") \
            .set_user_id("webhook_test_user") \
            .add_property("test_type", "webhook_verification") \
            .build()
        
        api_response = api_client.send_event(test_event, write_key, data_plane_url)
        assert api_response['success'], "Failed to send test event"
        
        # Wait for event delivery
        delivery_verified = webhook_page.verify_event_delivery(expected_count=initial_counts['delivered'] + 1, timeout=30)
        assert delivery_verified, "Event delivery verification failed"
        
        # Get final counts and stats
        final_counts = webhook_page.get_event_counts()
        delivery_stats = webhook_page.get_delivery_stats()
        
        logger.info(f"Final event counts: {final_counts}")
        logger.info(f"Delivery stats: {delivery_stats}")
        
        # Verify counts increased
        assert final_counts['delivered'] > initial_counts['delivered'], "Delivered count should have increased"
        
        logger.info("✓ Webhook delivery verification test completed")
    
    @pytest.mark.parametrize("event_type", ["page_view", "product_viewed", "add_to_cart", "purchase"])
    def test_different_event_types(self, driver, login_page, connections_page, webhook_page, test_data, event_type):
        """
        Parameterized test for different event types
        """
        logger.info(f"Testing event type: {event_type}")
        
        # Setup
        credentials = config_manager.get_credentials()
        assert login_page.login(credentials['email'], credentials['password']), "Login failed"
        
        connections_page.navigate_to_connections()
        data_plane_url = connections_page.get_data_plane_url()
        write_key = connections_page.get_http_source_write_key()
        
        assert data_plane_url and write_key, "Failed to get required configuration"
        
        # Send specific event type
        event_builder = APIFactory.create_event_builder()
        test_event = event_builder \
            .set_event_name(event_type) \
            .set_user_id(f"user_{event_type}") \
            .add_property("event_type", event_type) \
            .add_property("test_timestamp", int(time.time())) \
            .build()
        
        api_response = api_client.send_event(test_event, write_key, data_plane_url)
        assert api_response['success'], f"Failed to send {event_type} event"
        
        # Navigate to webhook and verify
        connections_page.click_webhook_destination()
        webhook_page.click_events_tab()
        
        # Wait and verify delivery
        time.sleep(5)
        event_counts = webhook_page.get_event_counts()
        
        # Basic verification - at least one event should be delivered
        assert event_counts['delivered'] > 0, f"No events delivered for {event_type}"
        
        logger.info(f"✓ {event_type} event test completed successfully")


# Additional test utilities
class TestUtilities:
    """Utility class for test helpers"""
    
    @staticmethod
    def validate_test_data(test_data: Dict[str, Any]) -> bool:
        """Validate test data structure"""
        required_keys = ['scenario', 'user', 'source', 'destination', 'events']
        return all(key in test_data for key in required_keys)
    
    @staticmethod
    def cleanup_test_data():
        """Cleanup any test data created during tests"""
        logger.info("Cleaning up test data")
        # Implementation would depend on specific cleanup requirements


# Pytest hooks for additional functionality
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        if "test_rudderstack_basic_flow" in item.name:
            item.add_marker(pytest.mark.integration)
        if "test_event_tracking_scenario" in item.name:
            item.add_marker(pytest.mark.slow) 