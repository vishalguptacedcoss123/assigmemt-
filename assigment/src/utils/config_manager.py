"""
Configuration Manager for Rudderstack Test Framework
Follows SOLID principles for maintainable and extensible configuration management.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic import BaseSettings, validator


@dataclass
class BrowserConfig:
    """Browser configuration data class"""
    name: str
    version: str
    headless: bool
    window_width: int
    window_height: int
    timeout: int
    implicit_wait: int
    page_load_timeout: int


@dataclass
class APIConfig:
    """API configuration data class"""
    base_url: str
    timeout: int
    retry_attempts: int
    max_retries: int
    retry_delay: int


@dataclass
class TestConfig:
    """Test configuration data class"""
    parallel_mode: bool
    max_workers: int
    generate_html_report: bool
    generate_allure_report: bool
    screenshot_on_failure: bool
    video_recording: bool


class EnvironmentSettings(BaseSettings):
    """Environment settings using Pydantic for validation"""
    
    # Rudderstack Credentials
    rudderstack_email: str
    rudderstack_password: str
    
    # Environment URLs
    dev_url: str = "https://app.rudderstack.com"
    qa_url: str = "https://app.rudderstack.com"
    prod_url: str = "https://app.rudderstack.com"
    current_env: str = "dev"
    
    # API Configuration
    api_timeout: int = 30
    api_retry_attempts: int = 3
    api_base_url: str = "https://api.rudderstack.com"
    
    # Test Configuration
    headless_mode: bool = True
    browser_timeout: int = 10000
    implicit_wait: int = 10
    page_load_timeout: int = 30
    
    # Browser Configuration
    browser_name: str = "chrome"
    browser_version: str = "latest"
    window_width: int = 1920
    window_height: int = 1080
    
    # Webhook Configuration
    webhook_url: Optional[str] = None
    webhook_timeout: int = 60
    
    # Reporting Configuration
    generate_html_report: bool = True
    generate_allure_report: bool = True
    screenshot_on_failure: bool = True
    video_recording: bool = False
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "test_execution.log"
    
    # Parallel Execution
    max_workers: int = 2
    parallel_mode: bool = False
    
    # Retry Configuration
    max_retries: int = 3
    retry_delay: int = 2
    
    # Notification Configuration
    slack_webhook_url: Optional[str] = None
    email_notifications: bool = False
    email_smtp_server: Optional[str] = None
    email_smtp_port: Optional[int] = None
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    
    @validator('current_env')
    def validate_environment(cls, v):
        """Validate environment value"""
        if v not in ['dev', 'qa', 'prod']:
            raise ValueError('Environment must be dev, qa, or prod')
        return v
    
    @validator('browser_name')
    def validate_browser(cls, v):
        """Validate browser name"""
        valid_browsers = ['chrome', 'firefox', 'safari', 'edge']
        if v not in valid_browsers:
            raise ValueError(f'Browser must be one of: {valid_browsers}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class ConfigurationManager:
    """
    Configuration Manager following Single Responsibility Principle
    Handles all configuration-related operations
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            env_file: Path to environment file
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        self._settings = EnvironmentSettings()
        self._browser_config = None
        self._api_config = None
        self._test_config = None
    
    @property
    def settings(self) -> EnvironmentSettings:
        """Get environment settings"""
        return self._settings
    
    @property
    def browser_config(self) -> BrowserConfig:
        """Get browser configuration"""
        if not self._browser_config:
            self._browser_config = BrowserConfig(
                name=self._settings.browser_name,
                version=self._settings.browser_version,
                headless=self._settings.headless_mode,
                window_width=self._settings.window_width,
                window_height=self._settings.window_height,
                timeout=self._settings.browser_timeout,
                implicit_wait=self._settings.implicit_wait,
                page_load_timeout=self._settings.page_load_timeout
            )
        return self._browser_config
    
    @property
    def api_config(self) -> APIConfig:
        """Get API configuration"""
        if not self._api_config:
            self._api_config = APIConfig(
                base_url=self._settings.api_base_url,
                timeout=self._settings.api_timeout,
                retry_attempts=self._settings.api_retry_attempts,
                max_retries=self._settings.max_retries,
                retry_delay=self._settings.retry_delay
            )
        return self._api_config
    
    @property
    def test_config(self) -> TestConfig:
        """Get test configuration"""
        if not self._test_config:
            self._test_config = TestConfig(
                parallel_mode=self._settings.parallel_mode,
                max_workers=self._settings.max_workers,
                generate_html_report=self._settings.generate_html_report,
                generate_allure_report=self._settings.generate_allure_report,
                screenshot_on_failure=self._settings.screenshot_on_failure,
                video_recording=self._settings.video_recording
            )
        return self._test_config
    
    def get_environment_url(self) -> str:
        """Get current environment URL"""
        env_mapping = {
            'dev': self._settings.dev_url,
            'qa': self._settings.qa_url,
            'prod': self._settings.prod_url
        }
        return env_mapping.get(self._settings.current_env, self._settings.dev_url)
    
    def get_credentials(self) -> Dict[str, str]:
        """Get Rudderstack credentials"""
        return {
            'email': self._settings.rudderstack_email,
            'password': self._settings.rudderstack_password
        }
    
    def is_production(self) -> bool:
        """Check if current environment is production"""
        return self._settings.current_env == 'prod'
    
    def get_webhook_url(self) -> Optional[str]:
        """Get webhook URL"""
        return self._settings.webhook_url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'environment': self._settings.current_env,
            'base_url': self.get_environment_url(),
            'browser': self.browser_config.__dict__,
            'api': self.api_config.__dict__,
            'test': self.test_config.__dict__,
            'credentials': {
                'email': self._settings.rudderstack_email,
                'password': '***'  # Mask password for security
            }
        }
    
    def apply_overrides(
        self,
        *,
        current_env: Optional[str] = None,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        Apply runtime overrides from CLI args (pytest options).
        This updates the underlying settings and clears cached configs.
        """
        updated = False
        if current_env:
            self._settings.current_env = current_env
            updated = True
        if email:
            self._settings.rudderstack_email = email
            updated = True
        if password:
            self._settings.rudderstack_password = password
            updated = True
        if base_url:
            # Apply base URL to the selected environment if provided
            env_key = (current_env or self._settings.current_env or 'dev').lower()
            if env_key == 'dev':
                self._settings.dev_url = base_url
            elif env_key == 'qa':
                self._settings.qa_url = base_url
            elif env_key == 'prod':
                self._settings.prod_url = base_url
            updated = True
        # Clear cached composed configs so subsequent accesses reflect overrides
        if updated:
            self._browser_config = None
            self._api_config = None
            self._test_config = None


# Global configuration instance
config_manager = ConfigurationManager() 