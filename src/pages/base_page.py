from playwright.sync_api import Page, expect, Locator
from typing import Optional, List, Dict, Any
from src.config.settings import Settings
from src.utils.logger import Logger
import time

class BasePage:
    """
    Base Page Object class that provides common functionality for all pages.
    This class implements the foundation for the Page Object Model pattern.
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.config = Settings.get_env_config()
        self.base_url = self.config['base_url']
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.timeout = self.config.get('timeouts', {}).get('element_wait', 10000)
        
        # Common selectors that appear across multiple pages
        self.loading_spinner = ".loading, .spinner"
        self.error_message = ".error, .alert-danger"
        self.success_message = ".success, .alert-success"
        self.modal_dialog = ".modal, .dialog"
        self.modal_close_button = ".modal-close, .close"
    
    # ==================== NAVIGATION METHODS ====================
    
    def navigate_to(self, path: str = "") -> None:
        """Navigate to a specific path relative to base URL"""
        full_url = f"{self.base_url}{path}"
        self.logger.info(f"Navigating to: {full_url}")
        self.page.goto(full_url)
        self.wait_for_page_load()
    
    def go_back(self) -> None:
        """Navigate back in browser history"""
        self.page.go_back()
        self.wait_for_page_load()
    
    def refresh_page(self) -> None:
        """Refresh the current page"""
        self.page.reload()
        self.wait_for_page_load()
    
    def get_current_url(self) -> str:
        """Get the current page URL"""
        return self.page.url
    
    def get_page_title(self) -> str:
        """Get the current page title"""
        return self.page.title()
    
    # ==================== ELEMENT INTERACTION METHODS ====================
    
    def find_element(self, selector: str, timeout: Optional[int] = None) -> Locator:
        """Find a single element with optional timeout"""
        timeout = timeout or self.timeout
        return self.page.locator(selector)
    
    def find_elements(self, selector: str) -> List[Locator]:
        """Find multiple elements"""
        return self.page.locator(selector).all()
    
    def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """Click an element with enhanced error handling"""
        timeout = timeout or self.timeout
        try:
            element = self.find_element(selector, timeout)
            element.wait_for(state="visible", timeout=timeout)
            element.click()
            self.logger.info(f"Clicked element: {selector}")
        except Exception as e:
            self.logger.error(f"Failed to click element {selector}: {str(e)}")
            raise
    
    def double_click(self, selector: str, timeout: Optional[int] = None) -> None:
        """Double click an element"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        element.dblclick()
        self.logger.info(f"Double-clicked element: {selector}")
    
    def right_click(self, selector: str, timeout: Optional[int] = None) -> None:
        """Right click an element"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        element.click(button="right")
        self.logger.info(f"Right-clicked element: {selector}")
    
    def fill_text(self, selector: str, text: str, clear_first: bool = True, timeout: Optional[int] = None) -> None:
        """Fill text into an input field"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        
        if clear_first:
            element.clear()
        
        element.fill(text)
        self.logger.info(f"Filled text '{text}' into element: {selector}")
    
    def type_text(self, selector: str, text: str, delay: int = 100, timeout: Optional[int] = None) -> None:
        """Type text with delay between characters (simulates human typing)"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        element.type(text, delay=delay)
        self.logger.info(f"Typed text '{text}' into element: {selector}")
    
    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """Get text content of an element"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        text = element.inner_text()
        self.logger.info(f"Retrieved text '{text}' from element: {selector}")
        return text
    
    def get_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """Get attribute value of an element"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        value = element.get_attribute(attribute)
        self.logger.info(f"Retrieved attribute '{attribute}' = '{value}' from element: {selector}")
        return value
    
    def select_dropdown_option(self, selector: str, option_value: str, timeout: Optional[int] = None) -> None:
        """Select option from dropdown by value"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        element.select_option(value=option_value)
        self.logger.info(f"Selected option '{option_value}' from dropdown: {selector}")
    
    def select_dropdown_by_text(self, selector: str, option_text: str, timeout: Optional[int] = None) -> None:
        """Select option from dropdown by visible text"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        element.select_option(label=option_text)
        self.logger.info(f"Selected option with text '{option_text}' from dropdown: {selector}")
    
    def upload_file(self, selector: str, file_path: str, timeout: Optional[int] = None) -> None:
        """Upload file to file input"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        element.set_input_files(file_path)
        self.logger.info(f"Uploaded file '{file_path}' to element: {selector}")
    
    # ==================== WAIT METHODS ====================
    
    def wait_for_element_visible(self, selector: str, timeout: Optional[int] = None) -> Locator:
        """Wait for element to be visible"""
        timeout = timeout or self.timeout
        element = self.find_element(selector)
        element.wait_for(state="visible", timeout=timeout)
        return element
    
    def wait_for_element_hidden(self, selector: str, timeout: Optional[int] = None) -> None:
        """Wait for element to be hidden"""
        timeout = timeout or self.timeout
        element = self.find_element(selector)
        element.wait_for(state="hidden", timeout=timeout)
    
    def wait_for_element_enabled(self, selector: str, timeout: Optional[int] = None) -> Locator:
        """Wait for element to be enabled"""
        timeout = timeout or self.timeout
        element = self.find_element(selector)
        element.wait_for(state="visible", timeout=timeout)
        expect(element).to_be_enabled(timeout=timeout)
        return element
    
    def wait_for_text_present(self, selector: str, expected_text: str, timeout: Optional[int] = None) -> None:
        """Wait for specific text to appear in element"""
        timeout = timeout or self.timeout
        element = self.find_element(selector)
        expect(element).to_contain_text(expected_text, timeout=timeout)
    
    def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """Wait for page to fully load"""
        timeout = timeout or 30000
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        self.wait_for_loading_to_complete()
    
    def wait_for_loading_to_complete(self, timeout: Optional[int] = None) -> None:
        """Wait for any loading spinners to disappear"""
        timeout = timeout or self.timeout
        try:
            self.page.wait_for_selector(self.loading_spinner, state="hidden", timeout=timeout)
        except:
            # Loading spinner might not be present, which is fine
            pass
    
    # ==================== VALIDATION METHODS ====================
    
    def is_element_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if element is visible"""
        timeout = timeout or 5000
        try:
            element = self.find_element(selector)
            element.wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False
    
    def is_element_enabled(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if element is enabled"""
        timeout = timeout or 5000
        try:
            element = self.find_element(selector)
            element.wait_for(state="visible", timeout=timeout)
            return element.is_enabled()
        except:
            return False
    
    def is_text_present(self, selector: str, expected_text: str, timeout: Optional[int] = None) -> bool:
        """Check if text is present in element"""
        timeout = timeout or 5000
        try:
            element = self.find_element(selector)
            element.wait_for(state="visible", timeout=timeout)
            return expected_text in element.inner_text()
        except:
            return False
    
    # ==================== VERIFICATION METHODS ====================
    
    def verify_element_visible(self, selector: str, timeout: Optional[int] = None) -> None:
        """Verify element is visible (assertion)"""
        timeout = timeout or self.timeout
        element = self.find_element(selector)
        expect(element).to_be_visible(timeout=timeout)
        self.logger.info(f"Verified element is visible: {selector}")
    
    def verify_element_hidden(self, selector: str, timeout: Optional[int] = None) -> None:
        """Verify element is hidden (assertion)"""
        timeout = timeout or self.timeout
        element = self.find_element(selector)
        expect(element).to_be_hidden(timeout=timeout)
        self.logger.info(f"Verified element is hidden: {selector}")
    
    def verify_text_equals(self, selector: str, expected_text: str, timeout: Optional[int] = None) -> None:
        """Verify element text equals expected value"""
        timeout = timeout or self.timeout
        element = self.find_element(selector)
        expect(element).to_have_text(expected_text, timeout=timeout)
        self.logger.info(f"Verified text equals '{expected_text}' in element: {selector}")
    
    def verify_text_contains(self, selector: str, expected_text: str, timeout: Optional[int] = None) -> None:
        """Verify element text contains expected value"""
        timeout = timeout or self.timeout
        element = self.find_element(selector)
        expect(element).to_contain_text(expected_text, timeout=timeout)
        self.logger.info(f"Verified text contains '{expected_text}' in element: {selector}")
    
    def verify_attribute_equals(self, selector: str, attribute: str, expected_value: str, timeout: Optional[int] = None) -> None:
        """Verify element attribute equals expected value"""
        timeout = timeout or self.timeout
        element = self.find_element(selector)
        expect(element).to_have_attribute(attribute, expected_value, timeout=timeout)
        self.logger.info(f"Verified attribute '{attribute}' equals '{expected_value}' in element: {selector}")
    
    def verify_url_contains(self, expected_url_part: str) -> None:
        """Verify current URL contains expected part"""
        expect(self.page).to_have_url(f"*{expected_url_part}*")
        self.logger.info(f"Verified URL contains: {expected_url_part}")
    
    def verify_page_title(self, expected_title: str) -> None:
        """Verify page title equals expected value"""
        expect(self.page).to_have_title(expected_title)
        self.logger.info(f"Verified page title: {expected_title}")
    
    # ==================== UTILITY METHODS ====================
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot of the current page"""
        if not filename:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        screenshot_path = f"reports/screenshots/{filename}"
        self.page.screenshot(path=screenshot_path)
        self.logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
    
    def scroll_to_element(self, selector: str, timeout: Optional[int] = None) -> None:
        """Scroll element into view"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.scroll_into_view_if_needed()
        self.logger.info(f"Scrolled to element: {selector}")
    
    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page"""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.logger.info("Scrolled to bottom of page")
    
    def scroll_to_top(self) -> None:
        """Scroll to top of page"""
        self.page.evaluate("window.scrollTo(0, 0)")
        self.logger.info("Scrolled to top of page")
    
    def get_element_count(self, selector: str) -> int:
        """Get count of elements matching selector"""
        return self.page.locator(selector).count()
    
    def hover_over_element(self, selector: str, timeout: Optional[int] = None) -> None:
        """Hover over an element"""
        timeout = timeout or self.timeout
        element = self.find_element(selector, timeout)
        element.wait_for(state="visible", timeout=timeout)
        element.hover()
        self.logger.info(f"Hovered over element: {selector}")
    
    def press_key(self, key: str) -> None:
        """Press a keyboard key"""
        self.page.keyboard.press(key)
        self.logger.info(f"Pressed key: {key}")
    
    def press_key_combination(self, keys: str) -> None:
        """Press key combination (e.g., 'Control+C')"""
        self.page.keyboard.press(keys)
        self.logger.info(f"Pressed key combination: {keys}")
    
    # ==================== COMMON UI PATTERNS ====================
    
    def handle_alert(self, accept: bool = True) -> Optional[str]:
        """Handle JavaScript alert dialog"""
        def handle_dialog(dialog):
            message = dialog.message
            if accept:
                dialog.accept()
            else:
                dialog.dismiss()
            return message
        
        self.page.on("dialog", handle_dialog)
        return None
    
    def close_modal(self) -> None:
        """Close any open modal dialog"""
        if self.is_element_visible(self.modal_dialog):
            self.click(self.modal_close_button)
            self.wait_for_element_hidden(self.modal_dialog)
            self.logger.info("Closed modal dialog")
    
    def get_error_message(self) -> str:
        """Get error message text if present"""
        if self.is_element_visible(self.error_message):
            return self.get_text(self.error_message)
        return ""
    
    def get_success_message(self) -> str:
        """Get success message text if present"""
        if self.is_element_visible(self.success_message):
            return self.get_text(self.success_message)
        return ""
    
    def verify_no_errors(self) -> None:
        """Verify no error messages are displayed"""
        if self.is_element_visible(self.error_message):
            error_text = self.get_text(self.error_message)
            raise AssertionError(f"Unexpected error message displayed: {error_text}")
        self.logger.info("Verified no error messages are displayed")
    
    # ==================== EXTENSIBILITY HOOKS ====================
    
    def setup_page_specific_elements(self) -> None:
        """Hook for child classes to define page-specific elements"""
        pass
    
    def validate_page_loaded(self) -> None:
        """Hook for child classes to validate page has loaded correctly"""
        pass
    
    def get_page_identifier(self) -> str:
        """Hook for child classes to return unique page identifier"""
        return self.__class__.__name__
    
    def cleanup(self) -> None:
        """Hook for child classes to perform cleanup actions"""
        pass