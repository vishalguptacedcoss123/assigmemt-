"""
Webhook Destination Page Object for Rudderstack Application
Handles webhook destination page interactions and event verification.
"""

import time
from typing import Optional, Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger

from .LoginPage import BasePage
from ..utils.config_manager import config_manager


class WebhookDestinationPage(BasePage):
    """
    Webhook Destination Page Object following Single Responsibility Principle
    Handles all webhook destination-related interactions
    """
    
    # Page elements
    EVENTS_TAB = (By.CSS_SELECTOR, "a[href*='events'], .events-tab, [data-testid='events-tab']")
    EVENTS_SECTION = (By.CSS_SELECTOR, ".events-section, .events-list, [data-testid='events']")
    EVENT_ITEM = (By.CSS_SELECTOR, ".event-item, .event-card, [data-testid*='event']")
    EVENT_STATUS = (By.CSS_SELECTOR, ".event-status, .status-badge, .delivery-status")
    EVENT_TIMESTAMP = (By.CSS_SELECTOR, ".event-timestamp, .event-time, .timestamp")
    EVENT_PAYLOAD = (By.CSS_SELECTOR, ".event-payload, .event-data, .payload")
    DELIVERED_COUNT = (By.CSS_SELECTOR, ".delivered-count, .success-count, [data-testid='delivered-count']")
    FAILED_COUNT = (By.CSS_SELECTOR, ".failed-count, .error-count, [data-testid='failed-count']")
    TOTAL_COUNT = (By.CSS_SELECTOR, ".total-count, .events-count, [data-testid='total-count']")
    REFRESH_BUTTON = (By.CSS_SELECTOR, ".refresh-btn, .refresh-button, [data-testid='refresh']")
    FILTER_BUTTON = (By.CSS_SELECTOR, ".filter-btn, .filter-button, [data-testid='filter']")
    SEARCH_EVENTS = (By.CSS_SELECTOR, "input[placeholder*='search events'], .search-events")
    STATUS_FILTER = (By.CSS_SELECTOR, ".status-filter, select[name='status']")
    DATE_FILTER = (By.CSS_SELECTOR, ".date-filter, input[type='date']")
    PAGINATION = (By.CSS_SELECTOR, ".pagination, .page-nav")
    NEXT_PAGE = (By.CSS_SELECTOR, ".next-page, .pagination-next")
    PREV_PAGE = (By.CSS_SELECTOR, ".prev-page, .pagination-prev")
    EVENTS_PER_PAGE = (By.CSS_SELECTOR, ".per-page, select[name='per_page']")
    
    def __init__(self, driver: WebDriver):
        """Initialize webhook destination page"""
        super().__init__(driver)
    
    def is_page_loaded(self) -> bool:
        """Check if webhook destination page is loaded"""
        try:
            # Check for multiple possible indicators
            indicators = [
                self.EVENTS_SECTION,
                (By.CSS_SELECTOR, ".webhook-destination-page"),
                (By.CSS_SELECTOR, "[data-testid='webhook-destination']"),
                (By.CSS_SELECTOR, ".destination-details")
            ]
            
            for indicator in indicators:
                if self.is_element_present(indicator, timeout=5):
                    return True
            
            return False
        except Exception:
            return False
    
    def click_events_tab(self) -> bool:
        """Click on events tab"""
        try:
            if self.is_element_present(self.EVENTS_TAB, timeout=5):
                self.safe_click(self.EVENTS_TAB)
                time.sleep(2)  # Wait for events to load
                logger.info("Clicked on events tab")
                return True
            
            logger.warning("Events tab not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to click events tab: {str(e)}")
            return False
    
    def get_event_counts(self) -> Dict[str, int]:
        """
        Get delivered and failed event counts
        
        Returns:
            Dictionary with delivered, failed, and total counts
        """
        counts = {
            'delivered': 0,
            'failed': 0,
            'total': 0
        }
        
        try:
            # Try to get counts from summary elements
            if self.is_element_present(self.DELIVERED_COUNT, timeout=5):
                delivered_text = self.get_element_text(self.DELIVERED_COUNT)
                counts['delivered'] = self._extract_number(delivered_text)
            
            if self.is_element_present(self.FAILED_COUNT, timeout=5):
                failed_text = self.get_element_text(self.FAILED_COUNT)
                counts['failed'] = self._extract_number(failed_text)
            
            if self.is_element_present(self.TOTAL_COUNT, timeout=5):
                total_text = self.get_element_text(self.TOTAL_COUNT)
                counts['total'] = self._extract_number(total_text)
            
            # If we couldn't get counts from summary, count from event list
            if counts['total'] == 0:
                events = self.get_events()
                counts['total'] = len(events)
                
                for event in events:
                    if event.get('status', '').lower() in ['delivered', 'success', '200']:
                        counts['delivered'] += 1
                    else:
                        counts['failed'] += 1
            
            logger.info(f"Event counts - Delivered: {counts['delivered']}, Failed: {counts['failed']}, Total: {counts['total']}")
            return counts
            
        except Exception as e:
            logger.error(f"Failed to get event counts: {str(e)}")
            return counts
    
    def _extract_number(self, text: str) -> int:
        """Extract number from text"""
        try:
            import re
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else 0
        except Exception:
            return 0
    
    def get_events(self) -> List[Dict[str, Any]]:
        """
        Get all events from the events tab
        
        Returns:
            List of event information dictionaries
        """
        events = []
        
        try:
            # Make sure we're on the events tab
            if not self.click_events_tab():
                return events
            
            # Wait for events section to load
            if not self.is_element_present(self.EVENTS_SECTION, timeout=10):
                logger.warning("Events section not found")
                return events
            
            # Find all event items
            event_elements = self.driver.find_elements(*self.EVENT_ITEM)
            
            for event_element in event_elements:
                try:
                    event_info = self._extract_event_info(event_element)
                    if event_info:
                        events.append(event_info)
                except Exception as e:
                    logger.warning(f"Failed to extract event info: {str(e)}")
                    continue
            
            logger.info(f"Found {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events: {str(e)}")
            return events
    
    def _extract_event_info(self, event_element: WebElement) -> Optional[Dict[str, Any]]:
        """Extract information from an event element"""
        try:
            # Extract event status
            status_element = event_element.find_element(*self.EVENT_STATUS)
            status = status_element.text.strip()
            
            # Extract timestamp
            timestamp = None
            try:
                timestamp_element = event_element.find_element(*self.EVENT_TIMESTAMP)
                timestamp = timestamp_element.text.strip()
            except NoSuchElementException:
                pass
            
            # Extract payload (if available)
            payload = None
            try:
                payload_element = event_element.find_element(*self.EVENT_PAYLOAD)
                payload = payload_element.text.strip()
            except NoSuchElementException:
                pass
            
            return {
                'status': status,
                'timestamp': timestamp,
                'payload': payload,
                'element': event_element
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract event info: {str(e)}")
            return None
    
    def wait_for_event(self, timeout: int = 60) -> bool:
        """
        Wait for a new event to appear
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if event appeared, False otherwise
        """
        try:
            logger.info(f"Waiting for new event (timeout: {timeout}s)")
            
            initial_count = self.get_event_counts()['total']
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                current_count = self.get_event_counts()['total']
                
                if current_count > initial_count:
                    logger.info(f"New event detected! Count increased from {initial_count} to {current_count}")
                    return True
                
                time.sleep(2)  # Check every 2 seconds
            
            logger.warning(f"No new event appeared within {timeout} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Failed to wait for event: {str(e)}")
            return False
    
    def refresh_events(self) -> bool:
        """Refresh the events list"""
        try:
            if self.is_element_present(self.REFRESH_BUTTON, timeout=5):
                self.safe_click(self.REFRESH_BUTTON)
                time.sleep(2)  # Wait for refresh
                logger.info("Refreshed events list")
                return True
            
            # If no refresh button, try to reload the page
            self.driver.refresh()
            time.sleep(3)  # Wait for page to reload
            logger.info("Reloaded page to refresh events")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh events: {str(e)}")
            return False
    
    def filter_events_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Filter events by status
        
        Args:
            status: Status to filter by (e.g., 'delivered', 'failed')
            
        Returns:
            List of filtered events
        """
        try:
            if self.is_element_present(self.STATUS_FILTER, timeout=5):
                # Implementation would depend on the specific filter structure
                logger.info(f"Filtering events by status: {status}")
                time.sleep(2)  # Wait for filter to apply
            
            return self.get_events()
            
        except Exception as e:
            logger.error(f"Failed to filter events by status: {str(e)}")
            return []
    
    def search_events(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for events
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching events
        """
        try:
            if self.is_element_present(self.SEARCH_EVENTS, timeout=5):
                self.safe_type(self.SEARCH_EVENTS, search_term)
                time.sleep(2)  # Wait for search results
            
            return self.get_events()
            
        except Exception as e:
            logger.error(f"Failed to search events: {str(e)}")
            return []
    
    def get_latest_event(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent event
        
        Returns:
            Latest event information or None
        """
        try:
            events = self.get_events()
            
            if not events:
                logger.warning("No events found")
                return None
            
            # Return the first event (assuming they're ordered by timestamp)
            latest_event = events[0]
            logger.info(f"Latest event status: {latest_event.get('status')}")
            return latest_event
            
        except Exception as e:
            logger.error(f"Failed to get latest event: {str(e)}")
            return None
    
    def verify_event_delivery(self, expected_count: int = 1, timeout: int = 60) -> bool:
        """
        Verify that events were delivered successfully
        
        Args:
            expected_count: Expected number of delivered events
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if verification successful, False otherwise
        """
        try:
            logger.info(f"Verifying event delivery (expected: {expected_count}, timeout: {timeout}s)")
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                counts = self.get_event_counts()
                
                if counts['delivered'] >= expected_count:
                    logger.info(f"Event delivery verified! Delivered: {counts['delivered']}")
                    return True
                
                time.sleep(2)  # Check every 2 seconds
            
            logger.warning(f"Event delivery verification failed. Expected: {expected_count}, Actual: {counts['delivered']}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to verify event delivery: {str(e)}")
            return False
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive delivery statistics
        
        Returns:
            Dictionary with delivery statistics
        """
        try:
            counts = self.get_event_counts()
            events = self.get_events()
            
            # Calculate additional stats
            recent_events = [e for e in events if e.get('timestamp')]  # Events with timestamps
            success_rate = (counts['delivered'] / counts['total'] * 100) if counts['total'] > 0 else 0
            
            stats = {
                'total_events': counts['total'],
                'delivered_events': counts['delivered'],
                'failed_events': counts['failed'],
                'success_rate': round(success_rate, 2),
                'recent_events_count': len(recent_events),
                'last_event_status': events[0].get('status') if events else None
            }
            
            logger.info(f"Delivery stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get delivery stats: {str(e)}")
            return {
                'total_events': 0,
                'delivered_events': 0,
                'failed_events': 0,
                'success_rate': 0,
                'recent_events_count': 0,
                'last_event_status': None
            } 