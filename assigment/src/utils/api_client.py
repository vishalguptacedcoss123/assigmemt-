"""
API Client for Rudderstack HTTP API
Follows SOLID principles for maintainable and extensible API interactions.
"""

import json
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger

from .config_manager import config_manager


class APIClientInterface(ABC):
    """Abstract base class for API clients following Interface Segregation Principle"""
    
    @abstractmethod
    def send_event(self, event_data: Dict[str, Any], write_key: str, data_plane_url: str) -> Dict[str, Any]:
        """Send event to Rudderstack"""
        pass
    
    @abstractmethod
    def get_webhook_events(self, webhook_url: str) -> List[Dict[str, Any]]:
        """Get events from webhook destination"""
        pass


class RudderstackAPIClient(APIClientInterface):
    """
    Rudderstack API Client following Single Responsibility Principle
    Handles all Rudderstack API interactions
    """
    
    def __init__(self):
        """Initialize API client with configuration"""
        self.config = config_manager.api_config
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.retry_attempts,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=self.config.retry_delay
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Rudderstack-SDET-TestFramework/1.0'
        })
        
        return session
    
    def send_event(self, event_data: Dict[str, Any], write_key: str, data_plane_url: str) -> Dict[str, Any]:
        """
        Send event to Rudderstack HTTP API
        
        Args:
            event_data: Event data to send
            write_key: HTTP source write key
            data_plane_url: Data plane URL
            
        Returns:
            API response
        """
        try:
            url = f"{data_plane_url}/v1/track"
            
            payload = {
                "event": event_data.get("event", "test_event"),
                "userId": event_data.get("userId", "test_user"),
                "properties": event_data.get("properties", {}),
                "context": event_data.get("context", {}),
                "timestamp": event_data.get("timestamp", int(time.time() * 1000))
            }
            
            headers = {
                'Authorization': f'Basic {write_key}',
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Sending event to Rudderstack: {payload['event']}")
            
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            
            logger.info(f"Event sent successfully. Status: {response.status_code}")
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if response.content else {},
                'event_id': response.headers.get('X-Event-ID')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send event: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def get_webhook_events(self, webhook_url: str) -> List[Dict[str, Any]]:
        """
        Get events from webhook destination (RequestCatcher)
        
        Args:
            webhook_url: Webhook URL to fetch events from
            
        Returns:
            List of webhook events
        """
        try:
            logger.info(f"Fetching webhook events from: {webhook_url}")
            
            response = self.session.get(
                webhook_url,
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            
            events = response.json() if response.content else []
            logger.info(f"Retrieved {len(events)} webhook events")
            
            return events
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch webhook events: {str(e)}")
            return []
    
    def get_webhook_stats(self, webhook_url: str) -> Dict[str, int]:
        """
        Get webhook delivery statistics
        
        Args:
            webhook_url: Webhook URL to fetch stats from
            
        Returns:
            Dictionary with delivered and failed event counts
        """
        events = self.get_webhook_events(webhook_url)
        
        delivered_count = 0
        failed_count = 0
        
        for event in events:
            # Check if event was delivered successfully
            if event.get('status', 200) == 200:
                delivered_count += 1
            else:
                failed_count += 1
        
        return {
            'delivered': delivered_count,
            'failed': failed_count,
            'total': len(events)
        }


class EventBuilder:
    """
    Event Builder following Builder Pattern
    Helps construct Rudderstack events
    """
    
    def __init__(self):
        """Initialize event builder"""
        self.event_data = {
            'event': 'test_event',
            'userId': 'test_user',
            'properties': {},
            'context': {},
            'timestamp': int(time.time() * 1000)
        }
    
    def set_event_name(self, event_name: str) -> 'EventBuilder':
        """Set event name"""
        self.event_data['event'] = event_name
        return self
    
    def set_user_id(self, user_id: str) -> 'EventBuilder':
        """Set user ID"""
        self.event_data['userId'] = user_id
        return self
    
    def add_property(self, key: str, value: Any) -> 'EventBuilder':
        """Add property to event"""
        self.event_data['properties'][key] = value
        return self
    
    def add_properties(self, properties: Dict[str, Any]) -> 'EventBuilder':
        """Add multiple properties to event"""
        self.event_data['properties'].update(properties)
        return self
    
    def add_context(self, key: str, value: Any) -> 'EventBuilder':
        """Add context to event"""
        self.event_data['context'][key] = value
        return self
    
    def set_timestamp(self, timestamp: int) -> 'EventBuilder':
        """Set event timestamp"""
        self.event_data['timestamp'] = timestamp
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return event data"""
        return self.event_data.copy()


class APIFactory:
    """
    API Factory following Factory Pattern
    Creates appropriate API client instances
    """
    
    @staticmethod
    def create_rudderstack_client() -> RudderstackAPIClient:
        """Create Rudderstack API client"""
        return RudderstackAPIClient()
    
    @staticmethod
    def create_event_builder() -> EventBuilder:
        """Create event builder"""
        return EventBuilder()


# Global API client instance
api_client = APIFactory.create_rudderstack_client() 