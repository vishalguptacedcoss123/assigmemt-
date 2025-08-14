"""
Test Data Manager for Rudderstack Test Framework
Follows SOLID principles for maintainable and extensible test data management.
"""

import json
import random
import string
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from faker import Faker

from .config_manager import config_manager


@dataclass
class TestUser:
    """Test user data class"""
    email: str
    password: str
    name: str
    company: str


@dataclass
class TestEvent:
    """Test event data class"""
    event_name: str
    user_id: str
    properties: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: int


@dataclass
class TestSource:
    """Test source data class"""
    name: str
    type: str
    write_key: str
    data_plane_url: str


@dataclass
class TestDestination:
    """Test destination data class"""
    name: str
    type: str
    webhook_url: str
    config: Dict[str, Any]


class TestDataGenerator:
    """
    Test Data Generator following Single Responsibility Principle
    Generates various types of test data
    """
    
    def __init__(self):
        """Initialize test data generator"""
        self.fake = Faker()
        self.fake.seed_instance(42)  # For reproducible data
    
    def generate_user(self, **kwargs) -> TestUser:
        """Generate test user data"""
        return TestUser(
            email=kwargs.get('email', self.fake.company_email()),
            password=kwargs.get('password', self.fake.password()),
            name=kwargs.get('name', self.fake.name()),
            company=kwargs.get('company', self.fake.company())
        )
    
    def generate_event(self, **kwargs) -> TestEvent:
        """Generate test event data"""
        return TestEvent(
            event_name=kwargs.get('event_name', 'test_event'),
            user_id=kwargs.get('user_id', self.fake.uuid4()),
            properties=kwargs.get('properties', self._generate_properties()),
            context=kwargs.get('context', self._generate_context()),
            timestamp=kwargs.get('timestamp', int(datetime.now().timestamp() * 1000))
        )
    
    def generate_source(self, **kwargs) -> TestSource:
        """Generate test source data"""
        return TestSource(
            name=kwargs.get('name', f"Test HTTP Source {self.fake.word()}"),
            type=kwargs.get('type', 'HTTP'),
            write_key=kwargs.get('write_key', self._generate_write_key()),
            data_plane_url=kwargs.get('data_plane_url', config_manager.get_environment_url())
        )
    
    def generate_destination(self, **kwargs) -> TestDestination:
        """Generate test destination data"""
        return TestDestination(
            name=kwargs.get('name', f"Test Webhook Destination {self.fake.word()}"),
            type=kwargs.get('type', 'Webhook'),
            webhook_url=kwargs.get('webhook_url', config_manager.get_webhook_url()),
            config=kwargs.get('config', self._generate_webhook_config())
        )
    
    def _generate_properties(self) -> Dict[str, Any]:
        """Generate random event properties"""
        return {
            'product_id': self.fake.uuid4(),
            'product_name': self.fake.product_name(),
            'price': round(random.uniform(10.0, 1000.0), 2),
            'quantity': random.randint(1, 10),
            'category': self.fake.word(),
            'brand': self.fake.company(),
            'color': self.fake.color_name(),
            'size': random.choice(['S', 'M', 'L', 'XL']),
            'currency': 'USD',
            'discount': round(random.uniform(0.0, 0.5), 2)
        }
    
    def _generate_context(self) -> Dict[str, Any]:
        """Generate random event context"""
        return {
            'page': {
                'url': self.fake.url(),
                'title': self.fake.sentence(),
                'referrer': self.fake.url()
            },
            'user_agent': self.fake.user_agent(),
            'ip': self.fake.ipv4(),
            'locale': self.fake.locale(),
            'timezone': self.fake.timezone(),
            'screen': {
                'width': random.randint(800, 2560),
                'height': random.randint(600, 1440)
            },
            'campaign': {
                'name': self.fake.word(),
                'source': self.fake.word(),
                'medium': self.fake.word(),
                'term': self.fake.word()
            }
        }
    
    def _generate_write_key(self) -> str:
        """Generate random write key"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def _generate_webhook_config(self) -> Dict[str, Any]:
        """Generate webhook configuration"""
        return {
            'url': config_manager.get_webhook_url(),
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': 'Rudderstack-SDET-TestFramework'
            },
            'timeout': 30,
            'retry_count': 3
        }


class TestScenarioManager:
    """
    Test Scenario Manager following Single Responsibility Principle
    Manages test scenarios and their data
    """
    
    def __init__(self):
        """Initialize test scenario manager"""
        self.data_generator = TestDataGenerator()
        self.scenarios = self._load_scenarios()
    
    def _load_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined test scenarios"""
        return {
            'basic_flow': {
                'name': 'Basic Rudderstack Flow',
                'description': 'Complete flow from login to event verification',
                'steps': [
                    'login_to_rudderstack',
                    'navigate_to_connections',
                    'extract_data_plane_url',
                    'extract_write_key',
                    'send_test_event',
                    'verify_webhook_delivery'
                ],
                'expected_results': {
                    'login_successful': True,
                    'data_plane_url_extracted': True,
                    'write_key_extracted': True,
                    'event_sent_successfully': True,
                    'webhook_delivery_verified': True
                }
            },
            'event_tracking': {
                'name': 'Event Tracking Test',
                'description': 'Test various event types and properties',
                'steps': [
                    'setup_test_environment',
                    'send_multiple_events',
                    'verify_event_delivery',
                    'check_event_properties'
                ],
                'expected_results': {
                    'all_events_sent': True,
                    'events_delivered_correctly': True,
                    'properties_preserved': True
                }
            },
            'error_handling': {
                'name': 'Error Handling Test',
                'description': 'Test error scenarios and edge cases',
                'steps': [
                    'test_invalid_credentials',
                    'test_invalid_write_key',
                    'test_network_timeout',
                    'test_malformed_event'
                ],
                'expected_results': {
                    'errors_handled_gracefully': True,
                    'appropriate_error_messages': True,
                    'no_system_crashes': True
                }
            }
        }
    
    def get_scenario(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """Get test scenario by name"""
        return self.scenarios.get(scenario_name)
    
    def get_all_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Get all available test scenarios"""
        return self.scenarios.copy()
    
    def create_test_data_for_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Create test data for specific scenario"""
        scenario = self.get_scenario(scenario_name)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        return {
            'scenario': scenario,
            'user': self.data_generator.generate_user(),
            'source': self.data_generator.generate_source(),
            'destination': self.data_generator.generate_destination(),
            'events': [
                self.data_generator.generate_event(event_name='page_view'),
                self.data_generator.generate_event(event_name='product_viewed'),
                self.data_generator.generate_event(event_name='add_to_cart'),
                self.data_generator.generate_event(event_name='purchase')
            ]
        }


class TestDataValidator:
    """
    Test Data Validator following Single Responsibility Principle
    Validates test data and results
    """
    
    @staticmethod
    def validate_user(user: TestUser) -> bool:
        """Validate test user data"""
        return all([
            user.email and '@' in user.email,
            user.password and len(user.password) >= 8,
            user.name and len(user.name) > 0,
            user.company and len(user.company) > 0
        ])
    
    @staticmethod
    def validate_event(event: TestEvent) -> bool:
        """Validate test event data"""
        return all([
            event.event_name and len(event.event_name) > 0,
            event.user_id and len(event.user_id) > 0,
            isinstance(event.properties, dict),
            isinstance(event.context, dict),
            event.timestamp > 0
        ])
    
    @staticmethod
    def validate_source(source: TestSource) -> bool:
        """Validate test source data"""
        return all([
            source.name and len(source.name) > 0,
            source.type in ['HTTP', 'Webhook', 'SDK'],
            source.write_key and len(source.write_key) > 0,
            source.data_plane_url and source.data_plane_url.startswith('http')
        ])
    
    @staticmethod
    def validate_destination(destination: TestDestination) -> bool:
        """Validate test destination data"""
        return all([
            destination.name and len(destination.name) > 0,
            destination.type in ['Webhook', 'HTTP'],
            destination.webhook_url and destination.webhook_url.startswith('http'),
            isinstance(destination.config, dict)
        ])
    
    @staticmethod
    def validate_api_response(response: Dict[str, Any]) -> bool:
        """Validate API response"""
        return all([
            isinstance(response, dict),
            'success' in response,
            response.get('success') is True,
            'status_code' in response,
            response.get('status_code') == 200
        ])
    
    @staticmethod
    def validate_webhook_stats(stats: Dict[str, int]) -> bool:
        """Validate webhook statistics"""
        return all([
            isinstance(stats, dict),
            'delivered' in stats,
            'failed' in stats,
            'total' in stats,
            isinstance(stats['delivered'], int),
            isinstance(stats['failed'], int),
            isinstance(stats['total'], int),
            stats['total'] == stats['delivered'] + stats['failed']
        ])


class TestDataFactory:
    """
    Test Data Factory following Factory Pattern
    Creates appropriate test data instances
    """
    
    @staticmethod
    def create_data_generator() -> TestDataGenerator:
        """Create test data generator"""
        return TestDataGenerator()
    
    @staticmethod
    def create_scenario_manager() -> TestScenarioManager:
        """Create test scenario manager"""
        return TestScenarioManager()
    
    @staticmethod
    def create_validator() -> TestDataValidator:
        """Create test data validator"""
        return TestDataValidator()


# Global test data instances
test_data_generator = TestDataFactory.create_data_generator()
test_scenario_manager = TestDataFactory.create_scenario_manager()
test_data_validator = TestDataFactory.create_validator() 