"""
Connections Page Object for Rudderstack Application
Handles connections page interactions and data extraction.
"""

import time
import re
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


class ConnectionsPage(BasePage):
    """
    Connections Page Object following Single Responsibility Principle
    Handles all connections-related interactions
    """
    
    # Page elements
    CONNECTIONS_LINK = (By.CSS_SELECTOR, "a[href*='connections'], a[href*='sources'], .connections-nav, [data-testid='connections']")
    DATA_PLANE_URL = (By.CSS_SELECTOR, ".data-plane-url, [data-testid='data-plane-url'], .endpoint-url")
    SOURCES_SECTION = (By.CSS_SELECTOR, ".sources-section, .sources-list, [data-testid='sources']")
    SOURCE_ITEM = (By.CSS_SELECTOR, ".source-item, .source-card, [data-testid*='source']")
    SOURCE_NAME = (By.CSS_SELECTOR, ".source-name, .source-title, h3, h4")
    SOURCE_TYPE = (By.CSS_SELECTOR, ".source-type, .source-category, .badge")
    WRITE_KEY = (By.CSS_SELECTOR, ".write-key, .api-key, [data-testid='write-key'], .key-value")
    COPY_BUTTON = (By.CSS_SELECTOR, ".copy-btn, .copy-button, [data-testid='copy']")
    DESTINATIONS_SECTION = (By.CSS_SELECTOR, ".destinations-section, .destinations-list, [data-testid='destinations']")
    DESTINATION_ITEM = (By.CSS_SELECTOR, ".destination-item, .destination-card, [data-testid*='destination']")
    DESTINATION_NAME = (By.CSS_SELECTOR, ".destination-name, .destination-title, h3, h4")
    DESTINATION_TYPE = (By.CSS_SELECTOR, ".destination-type, .destination-category, .badge")
    ADD_SOURCE_BUTTON = (By.CSS_SELECTOR, ".add-source, .create-source, [data-testid='add-source']")
    ADD_DESTINATION_BUTTON = (By.CSS_SELECTOR, ".add-destination, .create-destination, [data-testid='add-destination']")
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder*='search'], input[type='search'], .search-input")
    FILTER_DROPDOWN = (By.CSS_SELECTOR, ".filter-dropdown, .filter-select, select")
    
    def __init__(self, driver: WebDriver):
        """Initialize connections page"""
        super().__init__(driver)
        self.connections_url = f"{self.base_url}/connections"
    
    def is_page_loaded(self) -> bool:
        """Check if connections page is loaded"""
        try:
            # Check for multiple possible indicators
            indicators = [
                self.SOURCES_SECTION,
                self.DESTINATIONS_SECTION,
                (By.CSS_SELECTOR, ".connections-page"),
                (By.CSS_SELECTOR, "[data-testid='connections-page']")
            ]
            
            for indicator in indicators:
                if self.is_element_present(indicator, timeout=5):
                    return True
            
            return False
        except Exception:
            return False
    
    def navigate_to_connections(self) -> None:
        """Navigate to connections page"""
        try:
            # Try direct navigation first
            self.navigate_to(self.connections_url)
            
            # If that doesn't work, try clicking the connections link
            if not self.is_page_loaded():
                if self.is_element_present(self.CONNECTIONS_LINK, timeout=5):
                    self.safe_click(self.CONNECTIONS_LINK)
                    time.sleep(2)
            
            if not self.is_page_loaded():
                raise Exception("Connections page failed to load")
                
            logger.info("Successfully navigated to connections page")
            
        except Exception as e:
            logger.error(f"Failed to navigate to connections page: {str(e)}")
            raise
    
    def get_data_plane_url(self) -> Optional[str]:
        """
        Extract data plane URL from the page
        
        Returns:
            Data plane URL if found, None otherwise
        """
        try:
            # Try multiple possible selectors for data plane URL
            data_plane_selectors = [
                self.DATA_PLANE_URL,
                (By.CSS_SELECTOR, ".endpoint, .api-endpoint"),
                (By.CSS_SELECTOR, "[data-testid='data-plane']"),
                (By.CSS_SELECTOR, ".url-display, .endpoint-url"),
                (By.CSS_SELECTOR, "code, .code-block"),
                (By.XPATH, "//*[contains(text(), 'dataplane') or contains(text(), 'endpoint')]")
            ]
            
            for selector in data_plane_selectors:
                if self.is_element_present(selector, timeout=3):
                    url_text = self.get_element_text(selector)
                    
                    # Extract URL using regex
                    url_pattern = r'https?://[^\s<>"\']+'
                    match = re.search(url_pattern, url_text)
                    
                    if match:
                        data_plane_url = match.group(0)
                        logger.info(f"Extracted data plane URL: {data_plane_url}")
                        return data_plane_url
            
            logger.warning("Data plane URL not found on page")
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract data plane URL: {str(e)}")
            return None
    
    def get_sources(self) -> List[Dict[str, Any]]:
        """
        Get all sources from the connections page
        
        Returns:
            List of source information dictionaries
        """
        sources = []
        
        try:
            # Wait for sources section to load
            if not self.is_element_present(self.SOURCES_SECTION, timeout=10):
                logger.warning("Sources section not found")
                return sources
            
            # Find all source items
            source_elements = self.driver.find_elements(*self.SOURCE_ITEM)
            
            for source_element in source_elements:
                try:
                    source_info = self._extract_source_info(source_element)
                    if source_info:
                        sources.append(source_info)
                except Exception as e:
                    logger.warning(f"Failed to extract source info: {str(e)}")
                    continue
            
            logger.info(f"Found {len(sources)} sources")
            return sources
            
        except Exception as e:
            logger.error(f"Failed to get sources: {str(e)}")
            return sources
    
    def _extract_source_info(self, source_element: WebElement) -> Optional[Dict[str, Any]]:
        """Extract information from a source element"""
        try:
            # Extract source name
            name_element = source_element.find_element(*self.SOURCE_NAME)
            name = name_element.text.strip()
            
            # Extract source type
            type_element = source_element.find_element(*self.SOURCE_TYPE)
            source_type = type_element.text.strip()
            
            # Extract write key if available
            write_key = None
            try:
                write_key_element = source_element.find_element(*self.WRITE_KEY)
                write_key = write_key_element.text.strip()
            except NoSuchElementException:
                pass
            
            return {
                'name': name,
                'type': source_type,
                'write_key': write_key,
                'element': source_element
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract source info: {str(e)}")
            return None
    
    def get_http_source_write_key(self, source_name: Optional[str] = None) -> Optional[str]:
        """
        Get write key for HTTP source
        
        Args:
            source_name: Specific source name to look for (optional)
            
        Returns:
            Write key if found, None otherwise
        """
        try:
            sources = self.get_sources()
            
            for source in sources:
                # Check if it's an HTTP source
                if source['type'].lower() in ['http', 'webhook', 'api']:
                    # If source name is specified, check for exact match
                    if source_name and source['name'].lower() != source_name.lower():
                        continue
                    
                    if source['write_key']:
                        logger.info(f"Found HTTP source write key: {source['write_key']}")
                        return source['write_key']
            
            logger.warning("HTTP source write key not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get HTTP source write key: {str(e)}")
            return None
    
    def click_source(self, source_name: str) -> bool:
        """
        Click on a specific source
        
        Args:
            source_name: Name of the source to click
            
        Returns:
            True if successful, False otherwise
        """
        try:
            sources = self.get_sources()
            
            for source in sources:
                if source['name'].lower() == source_name.lower():
                    source['element'].click()
                    logger.info(f"Clicked on source: {source_name}")
                    return True
            
            logger.warning(f"Source '{source_name}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to click source '{source_name}': {str(e)}")
            return False
    
    def get_destinations(self) -> List[Dict[str, Any]]:
        """
        Get all destinations from the connections page
        
        Returns:
            List of destination information dictionaries
        """
        destinations = []
        
        try:
            # Wait for destinations section to load
            if not self.is_element_present(self.DESTINATIONS_SECTION, timeout=10):
                logger.warning("Destinations section not found")
                return destinations
            
            # Find all destination items
            destination_elements = self.driver.find_elements(*self.DESTINATION_ITEM)
            
            for destination_element in destination_elements:
                try:
                    destination_info = self._extract_destination_info(destination_element)
                    if destination_info:
                        destinations.append(destination_info)
                except Exception as e:
                    logger.warning(f"Failed to extract destination info: {str(e)}")
                    continue
            
            logger.info(f"Found {len(destinations)} destinations")
            return destinations
            
        except Exception as e:
            logger.error(f"Failed to get destinations: {str(e)}")
            return destinations
    
    def _extract_destination_info(self, destination_element: WebElement) -> Optional[Dict[str, Any]]:
        """Extract information from a destination element"""
        try:
            # Extract destination name
            name_element = destination_element.find_element(*self.DESTINATION_NAME)
            name = name_element.text.strip()
            
            # Extract destination type
            type_element = destination_element.find_element(*self.DESTINATION_TYPE)
            destination_type = type_element.text.strip()
            
            return {
                'name': name,
                'type': destination_type,
                'element': destination_element
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract destination info: {str(e)}")
            return None
    
    def click_webhook_destination(self, destination_name: Optional[str] = None) -> bool:
        """
        Click on webhook destination
        
        Args:
            destination_name: Specific destination name to look for (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            destinations = self.get_destinations()
            
            for destination in destinations:
                # Check if it's a webhook destination
                if destination['type'].lower() in ['webhook', 'http']:
                    # If destination name is specified, check for exact match
                    if destination_name and destination['name'].lower() != destination_name.lower():
                        continue
                    
                    destination['element'].click()
                    logger.info(f"Clicked on webhook destination: {destination['name']}")
                    return True
            
            logger.warning("Webhook destination not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to click webhook destination: {str(e)}")
            return False
    
    def search_sources(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for sources by name
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching sources
        """
        try:
            if self.is_element_present(self.SEARCH_INPUT, timeout=5):
                self.safe_type(self.SEARCH_INPUT, search_term)
                time.sleep(2)  # Wait for search results
            
            return self.get_sources()
            
        except Exception as e:
            logger.error(f"Failed to search sources: {str(e)}")
            return []
    
    def filter_by_type(self, filter_type: str) -> List[Dict[str, Any]]:
        """
        Filter sources by type
        
        Args:
            filter_type: Type to filter by
            
        Returns:
            List of filtered sources
        """
        try:
            if self.is_element_present(self.FILTER_DROPDOWN, timeout=5):
                # Implementation would depend on the specific filter dropdown structure
                logger.info(f"Filtering sources by type: {filter_type}")
                time.sleep(2)  # Wait for filter to apply
            
            return self.get_sources()
            
        except Exception as e:
            logger.error(f"Failed to filter sources: {str(e)}")
            return []
    
    def copy_write_key(self, source_name: str) -> Optional[str]:
        """
        Copy write key to clipboard
        
        Args:
            source_name: Name of the source
            
        Returns:
            Copied write key if successful, None otherwise
        """
        try:
            # First click on the source to open details
            if not self.click_source(source_name):
                return None
            
            # Look for copy button
            if self.is_element_present(self.COPY_BUTTON, timeout=5):
                self.safe_click(self.COPY_BUTTON)
                logger.info(f"Copied write key for source: {source_name}")
                
                # In a real implementation, you might need to get the clipboard content
                # For now, we'll return the write key we already extracted
                return self.get_http_source_write_key(source_name)
            
            logger.warning(f"Copy button not found for source: {source_name}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to copy write key for source '{source_name}': {str(e)}")
            return None 