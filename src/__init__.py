"""
Rudderstack SDET Assignment Framework
A comprehensive test automation framework for Rudderstack flows.
"""

__version__ = "1.0.0"
__author__ = "SDET Candidate"
__email__ = "candidate@example.com"

from .utils.config_manager import config_manager
from .utils.api_client import api_client
from .utils.test_data import test_data_generator, test_scenario_manager, test_data_validator

__all__ = [
    'config_manager',
    'api_client', 
    'test_data_generator',
    'test_scenario_manager',
    'test_data_validator'
] 