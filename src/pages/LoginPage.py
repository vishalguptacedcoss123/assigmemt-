"""
Login Page Object for Rudderstack Application
Follows Page Object Model pattern and SOLID principles.
"""

import time
from typing import Optional
from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger

from ..utils.config_manager import config_manager


class BasePage(ABC):
    """Abstract base page class following Template Method Pattern"""
    
    def __init__(self, driver: WebDriver):
        """
        Initialize base page
        
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, config_manager.browser_config.timeout)
        self.base_url = config_manager.get_environment_url()
    
    @abstractmethod
    def is_page_loaded(self) -> bool:
        """Check if page is loaded"""
        pass
    
    def navigate_to(self, url: str) -> None:
        """Navigate to specific URL"""
        try:
            self.driver.get(url)
            logger.info(f"Navigated to: {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            raise
    
    def wait_for_element(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        """Wait for element to be present and visible"""
        wait_time = timeout or config_manager.browser_config.timeout
        wait = WebDriverWait(self.driver, wait_time)
        
        try:
            element = wait.until(EC.presence_of_element_located(locator))
            wait.until(EC.visibility_of(element))
            return element
        except TimeoutException:
            logger.error(f"Element not found within {wait_time} seconds: {locator}")
            raise
    
    def wait_for_element_clickable(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        """Wait for element to be clickable"""
        wait_time = timeout or config_manager.browser_config.timeout
        wait = WebDriverWait(self.driver, wait_time)
        
        try:
            return wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            logger.error(f"Element not clickable within {wait_time} seconds: {locator}")
            raise
    
    def safe_click(self, locator: tuple, timeout: Optional[int] = None) -> None:
        """Safely click on element with retry mechanism"""
        max_retries = config_manager.api_config.max_retries
        
        for attempt in range(max_retries):
            try:
                element = self.wait_for_element_clickable(locator, timeout)
                element.click()
                logger.info(f"Successfully clicked element: {locator}")
                return
            except Exception as e:
                logger.warning(f"Click attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(config_manager.api_config.retry_delay)
    
    def safe_type(self, locator: tuple, text: str, clear_first: bool = True, timeout: Optional[int] = None) -> None:
        """Safely type text into element"""
        try:
            element = self.wait_for_element(locator, timeout)
            
            if clear_first:
                element.clear()
            
            element.send_keys(text)
            logger.info(f"Successfully typed text into element: {locator}")
        except Exception as e:
            logger.error(f"Failed to type text into element {locator}: {str(e)}")
            raise
    
    def get_element_text(self, locator: tuple, timeout: Optional[int] = None) -> str:
        """Get text from element"""
        try:
            element = self.wait_for_element(locator, timeout)
            text = element.text.strip()
            logger.info(f"Retrieved text from element {locator}: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to get text from element {locator}: {str(e)}")
            raise
    
    def is_element_present(self, locator: tuple, timeout: int = 5) -> bool:
        """Check if element is present on page"""
        try:
            self.wait_for_element(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def take_screenshot(self, filename: str) -> None:
        """Take screenshot of current page"""
        try:
            self.driver.save_screenshot(f"screenshots/{filename}")
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")


class LoginPage(BasePage):
    """
    Login Page Object following Single Responsibility Principle
    Handles all login-related interactions
    """
    
    # Page elements
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email'], input[name='email'], #email")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password'], input[name='password'], #password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .login-btn, #login")
    FORGOT_PASSWORD_LINK = (By.CSS_SELECTOR, "a[href*='forgot'], .forgot-password")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message, .alert-danger, .invalid-feedback")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".success-message, .alert-success")
    LOGIN_FORM = (By.CSS_SELECTOR, "form, .login-form")
    
    def __init__(self, driver: WebDriver):
        """Initialize login page"""
        super().__init__(driver)
        self.login_url = f"{self.base_url}/login"
    
    def is_page_loaded(self) -> bool:
        """Check if login page is loaded"""
        try:
            return self.is_element_present(self.LOGIN_FORM, timeout=10)
        except Exception:
            return False
    
    def navigate_to_login(self) -> None:
        """Navigate to login page"""
        self.navigate_to(self.login_url)
        if not self.is_page_loaded():
            raise Exception("Login page failed to load")
    
    def enter_email(self, email: str) -> None:
        """Enter email address"""
        self.safe_type(self.EMAIL_INPUT, email)
    
    def enter_password(self, password: str) -> None:
        """Enter password"""
        self.safe_type(self.PASSWORD_INPUT, password)
    
    def click_login_button(self) -> None:
        """Click login button"""
        self.safe_click(self.LOGIN_BUTTON)
    
    def login(self, email: str, password: str) -> bool:
        """
        Perform complete login process
        
        Args:
            email: User email
            password: User password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info(f"Attempting login for user: {email}")
            
            # Navigate to login page
            self.navigate_to_login()
            
            # Enter credentials
            self.enter_email(email)
            self.enter_password(password)
            
            # Submit login form
            self.click_login_button()
            
            # Wait for navigation or error
            time.sleep(2)
            
            # Check for success (redirected away from login page)
            if not self.is_page_loaded():
                logger.info("Login successful - redirected from login page")
                return True
            
            # Check for error message
            if self.is_element_present(self.ERROR_MESSAGE, timeout=5):
                error_text = self.get_element_text(self.ERROR_MESSAGE)
                logger.error(f"Login failed with error: {error_text}")
                return False
            
            logger.warning("Login status unclear - page still on login form")
            return False
            
        except Exception as e:
            logger.error(f"Login process failed: {str(e)}")
            self.take_screenshot(f"login_failure_{int(time.time())}.png")
            return False
    
    def get_error_message(self) -> Optional[str]:
        """Get error message if present"""
        try:
            if self.is_element_present(self.ERROR_MESSAGE, timeout=5):
                return self.get_element_text(self.ERROR_MESSAGE)
        except Exception as e:
            logger.error(f"Failed to get error message: {str(e)}")
        return None
    
    def get_success_message(self) -> Optional[str]:
        """Get success message if present"""
        try:
            if self.is_element_present(self.SUCCESS_MESSAGE, timeout=5):
                return self.get_element_text(self.SUCCESS_MESSAGE)
        except Exception as e:
            logger.error(f"Failed to get success message: {str(e)}")
        return None
    
    def click_forgot_password(self) -> None:
        """Click forgot password link"""
        self.safe_click(self.FORGOT_PASSWORD_LINK)
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        try:
            # Check if we're still on login page
            if self.is_page_loaded():
                return False
            
            # Check for common logged-in indicators
            logged_in_indicators = [
                (By.CSS_SELECTOR, ".user-menu, .profile-menu, .account-menu"),
                (By.CSS_SELECTOR, "[data-testid='user-menu']"),
                (By.CSS_SELECTOR, ".dashboard, .home-page"),
                (By.CSS_SELECTOR, "[href*='logout']")
            ]
            
            for indicator in logged_in_indicators:
                if self.is_element_present(indicator, timeout=3):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check login status: {str(e)}")
            return False
    
    def logout(self) -> bool:
        """Perform logout if logged in"""
        try:
            if not self.is_logged_in():
                logger.info("User not logged in, no logout needed")
                return True
            
            # Look for logout elements
            logout_selectors = [
                (By.CSS_SELECTOR, "[href*='logout']"),
                (By.CSS_SELECTOR, ".logout-btn"),
                (By.CSS_SELECTOR, "[data-testid='logout']"),
                (By.CSS_SELECTOR, "button[onclick*='logout']")
            ]
            
            for selector in logout_selectors:
                if self.is_element_present(selector, timeout=3):
                    self.safe_click(selector)
                    time.sleep(2)
                    
                    # Verify logout
                    if not self.is_logged_in():
                        logger.info("Logout successful")
                        return True
            
            logger.warning("Logout elements not found")
            return False
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False 