"""
Comprehensive helper utilities for Parabank automation framework.
Provides reusable functions for common automation tasks and patterns.
"""

import os
import json
import time
import random
import string
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from contextlib import contextmanager
import yaml

from playwright.sync_api import Page, Locator, BrowserContext, expect
from playwright.async_api import Page as AsyncPage

from logger import get_logger

logger = get_logger("helpers")


@dataclass
class TestData:
    """Container for test data with validation."""
    username: str
    password: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.username or not self.password:
            raise ValueError("Username and password are required")


class ConfigManager:
    """
    Centralized configuration management for the automation framework.
    Supports multiple environments and configuration sources.
    """
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables."""
        # Load from YAML file if exists
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        
        # Override with environment variables
        env_overrides = {
            'base_url': os.getenv('BASE_URL'),
            'browser': os.getenv('BROWSER', 'chromium'),
            'headless': os.getenv('HEADLESS', 'true').lower() == 'true',
            'timeout': int(os.getenv('TIMEOUT', '30000')),
            'environment': os.getenv('TEST_ENV', 'dev'),
            'parallel_workers': int(os.getenv('PARALLEL_WORKERS', '1')),
            'video_recording': os.getenv('VIDEO_RECORDING', 'false').lower() == 'true',
            'screenshot_on_failure': os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
        }
        
        # Update config with non-None environment values
        for key, value in env_overrides.items():
            if value is not None:
                self.config[key] = value
    
    def get(self, key: str, default=None):
        """Get configuration value with dot notation support."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_environment_config(self, env: str = None) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        env = env or self.get('environment', 'dev')
        return self.get(f'environments.{env}', {})


class DataGenerator:
    """
    Generate test data for various scenarios.
    Useful for creating realistic test datasets.
    """
    
    @staticmethod
    def random_string(length: int = 8, include_numbers: bool = True) -> str:
        """Generate random string."""
        chars = string.ascii_lowercase
        if include_numbers:
            chars += string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def random_email(domain: str = "testmail.com") -> str:
        """Generate random email address."""
        username = DataGenerator.random_string(8)
        return f"{username}@{domain}"
    
    @staticmethod
    def random_phone() -> str:
        """Generate random US phone number."""
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        return f"({area_code}) {exchange}-{number}"
    
    @staticmethod
    def random_amount(min_amount: float = 1.0, max_amount: float = 1000.0) -> float:
        """Generate random monetary amount."""
        return round(random.uniform(min_amount, max_amount), 2)
    
    @staticmethod
    def create_test_user(username_prefix: str = "testuser") -> TestData:
        """Create complete test user data."""
        username = f"{username_prefix}_{DataGenerator.random_string(6)}"
        return TestData(
            username=username,
            password="TestPass123!",
            first_name="Test",
            last_name="User",
            email=DataGenerator.random_email(),
            phone=DataGenerator.random_phone(),
            address="123 Test Street",
            city="Test City",
            state="CA",
            zip_code="12345"
        )


class PageHelpers:
    """
    Enhanced page interaction helpers for Playwright.
    Provides robust element interaction with built-in waiting and error handling.
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.default_timeout = 30000
    
    def safe_click(self, selector: str, timeout: int = None) -> bool:
        """
        Safely click an element with error handling and logging.
        
        Args:
            selector: Element selector
            timeout: Wait timeout in milliseconds
            
        Returns:
            True if click succeeded, False otherwise
        """
        timeout = timeout or self.default_timeout
        try:
            logger.info(f"Attempting to click element: {selector}")
            element = self.page.locator(selector)
            element.wait_for(state="visible", timeout=timeout)
            element.click(timeout=timeout)
            logger.debug(f"Successfully clicked: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {str(e)}")
            return False
    
    def safe_fill(self, selector: str, value: str, timeout: int = None, clear_first: bool = True) -> bool:
        """
        Safely fill an input field with error handling.
        
        Args:
            selector: Element selector
            value: Text to fill
            timeout: Wait timeout in milliseconds
            clear_first: Clear field before filling
            
        Returns:
            True if fill succeeded, False otherwise
        """
        timeout = timeout or self.default_timeout
        try:
            logger.info(f"Attempting to fill element {selector} with value: {value}")
            element = self.page.locator(selector)
            element.wait_for(state="visible", timeout=timeout)
            
            if clear_first:
                element.clear()
            
            element.fill(value, timeout=timeout)
            logger.debug(f"Successfully filled {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to fill element {selector}: {str(e)}")
            return False
    
    def wait_for_element(self, selector: str, state: str = "visible", timeout: int = None) -> Optional[Locator]:
        """
        Wait for element to reach specified state.
        
        Args:
            selector: Element selector
            state: Element state (visible, hidden, attached, detached)
            timeout: Wait timeout in milliseconds
            
        Returns:
            Locator if found, None otherwise
        """
        timeout = timeout or self.default_timeout
        try:
            logger.debug(f"Waiting for element {selector} to be {state}")
            element = self.page.locator(selector)
            element.wait_for(state=state, timeout=timeout)
            return element
        except Exception as e:
            logger.warning(f"Element {selector} did not reach state {state}: {str(e)}")
            return None
    
    def get_text_content(self, selector: str, timeout: int = None) -> Optional[str]:
        """
        Get text content of an element.
        
        Args:
            selector: Element selector
            timeout: Wait timeout in milliseconds
            
        Returns:
            Text content or None if not found
        """
        element = self.wait_for_element(selector, timeout=timeout)
        if element:
            try:
                return element.text_content()
            except Exception as e:
                logger.error(f"Failed to get text content from {selector}: {str(e)}")
        return None
    
    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Check if element is visible on page.
        
        Args:
            selector: Element selector
            timeout: Wait timeout in milliseconds
            
        Returns:
            True if visible, False otherwise
        """
        try:
            element = self.page.locator(selector)
            element.wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False
    
    def scroll_to_element(self, selector: str) -> bool:
        """
        Scroll element into view.
        
        Args:
            selector: Element selector
            
        Returns:
            True if successful, False otherwise
        """
        try:
            element = self.page.locator(selector)
            element.scroll_into_view_if_needed()
            logger.debug(f"Scrolled to element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to scroll to element {selector}: {str(e)}")
            return False
    
    def select_dropdown_option(self, selector: str, option_value: str = None, 
                             option_text: str = None, timeout: int = None) -> bool:
        """
        Select option from dropdown by value or text.
        
        Args:
            selector: Dropdown selector
            option_value: Option value to select
            option_text: Option text to select
            timeout: Wait timeout in milliseconds
            
        Returns:
            True if successful, False otherwise
        """
        timeout = timeout or self.default_timeout
        try:
            element = self.wait_for_element(selector, timeout=timeout)
            if not element:
                return False
            
            if option_value:
                element.select_option(value=option_value)
                logger.debug(f"Selected option by value: {option_value}")
            elif option_text:
                element.select_option(label=option_text)
                logger.debug(f"Selected option by text: {option_text}")
            else:
                logger.error("Either option_value or option_text must be provided")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to select dropdown option: {str(e)}")
            return False


class WaitHelpers:
    """
    Advanced waiting utilities for dynamic content and async operations.
    """
    
    def __init__(self, page: Page):
        self.page = page
    
    def wait_for_url_change(self, current_url: str, timeout: int = 30000) -> bool:
        """
        Wait for URL to change from current URL.
        
        Args:
            current_url: Current page URL
            timeout: Wait timeout in milliseconds
            
        Returns:
            True if URL changed, False if timeout
        """
        try:
            self.page.wait_for_url(lambda url: url != current_url, timeout=timeout)
            logger.debug(f"URL changed from: {current_url}")
            return True
        except Exception as e:
            logger.warning(f"URL did not change within timeout: {str(e)}")
            return False
    
    def wait_for_page_load(self, timeout: int = 30000) -> bool:
        """
        Wait for page to fully load (networkidle).
        
        Args:
            timeout: Wait timeout in milliseconds
            
        Returns:
            True if loaded, False if timeout
        """
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("Page fully loaded (networkidle)")
            return True
        except Exception as e:
            logger.warning(f"Page did not reach networkidle state: {str(e)}")
            return False
    
    def wait_for_condition(self, condition_func: Callable[[], bool], 
                          timeout: int = 30000, poll_interval: float = 0.5) -> bool:
        """
        Wait for custom condition to be met.
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Wait timeout in milliseconds
            poll_interval: Polling interval in seconds
            
        Returns:
            True if condition met, False if timeout
        """
        start_time = time.time()
        timeout_seconds = timeout / 1000
        
        while time.time() - start_time < timeout_seconds:
            try:
                if condition_func():
                    logger.debug("Custom condition met")
                    return True
            except Exception as e:
                logger.debug(f"Condition check failed: {str(e)}")
            
            time.sleep(poll_interval)
        
        logger.warning(f"Custom condition not met within {timeout}ms")
        return False


class ScreenshotHelper:
    """
    Enhanced screenshot capabilities for test documentation and debugging.
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def take_screenshot(self, name: str = None, full_page: bool = True) -> Path:
        """
        Take screenshot with automatic naming and organization.
        
        Args:
            name: Screenshot name (auto-generated if None)
            full_page: Capture full page or just viewport
            
        Returns:
            Path to saved screenshot
        """
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"screenshot_{timestamp}"
        
        # Ensure proper file extension
        if not name.endswith('.png'):
            name += '.png'
        
        screenshot_path = self.screenshots_dir / name
        
        try:
            self.page.screenshot(path=screenshot_path, full_page=full_page)
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return None
    
    def take_element_screenshot(self, selector: str, name: str = None) -> Path:
        """
        Take screenshot of specific element.
        
        Args:
            selector: Element selector
            name: Screenshot name
            
        Returns:
            Path to saved screenshot
        """
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"element_{timestamp}.png"
        
        screenshot_path = self.screenshots_dir / name
        
        try:
            element = self.page.locator(selector)
            element.screenshot(path=screenshot_path)
            logger.info(f"Element screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to take element screenshot: {str(e)}")
            return None


@contextmanager
def performance_monitor(page: Page, operation_name: str):
    """
    Context manager for monitoring page performance during operations.
    
    Args:
        page: Playwright page instance
        operation_name: Name of operation being monitored
    """
    logger.info(f"Starting performance monitoring for: {operation_name}")
    start_time = time.time()
    
    # Start performance monitoring
    page.evaluate("performance.mark('operation-start')")
    
    try:
        yield
    finally:
        # End performance monitoring
        page.evaluate("performance.mark('operation-end')")
        page.evaluate("performance.measure('operation-duration', 'operation-start', 'operation-end')")
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Get navigation timing if available
        try:
            navigation_timing = page.evaluate("""
                () => {
                    const timing = performance.getEntriesByType('navigation')[0];
                    return timing ? {
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart,
                        loadComplete: timing.loadEventEnd - timing.loadEventStart,
                        pageLoad: timing.loadEventEnd - timing.navigationStart
                    } : null;
                }
            """)
            
            if navigation_timing:
                logger.info(f"Performance metrics for {operation_name}:")
                logger.info(f"  Total duration: {duration:.2f}ms")
                logger.info(f"  DOM Content Loaded: {navigation_timing['domContentLoaded']:.2f}ms")
                logger.info(f"  Load Complete: {navigation_timing['loadComplete']:.2f}ms")
                logger.info(f"  Page Load: {navigation_timing['pageLoad']:.2f}ms")
        except Exception as e:
            logger.warning(f"Could not retrieve navigation timing: {str(e)}")
            logger.info(f"Operation {operation_name} completed in {duration:.2f}ms")


class DatabaseHelper:
    """
    Database utility functions for test data management.
    Supports common database operations for test setup and cleanup.
    """
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv('DB_CONNECTION_STRING')
        # Note: Add actual database connection logic based on your needs
        # This is a placeholder for common patterns
    
    def setup_test_data(self, test_data: Dict[str, Any]) -> bool:
        """
        Setup test data in database.
        
        Args:
            test_data: Dictionary of test data to insert
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("Setting up test data in database")
        # Implement actual database setup logic
        return True
    
    def cleanup_test_data(self, identifier: str) -> bool:
        """
        Clean up test data after test execution.
        
        Args:
            identifier: Unique identifier for test data
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Cleaning up test data for: {identifier}")
        # Implement actual database cleanup logic
        return True


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, 
                    exceptions: tuple = (Exception,)):
    """
    Decorator for retrying operations that may fail transiently.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between attempts in seconds
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {delay}s...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


# Initialize global instances
config = ConfigManager()
data_generator = DataGenerator()