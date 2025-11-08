"""
Authentication module for LeetCode
Handles cookie management and session persistence
"""

import json
from pathlib import Path
from typing import Optional, Dict, List

from core.logger import logger
from core.utils import load_json_file, save_json_file
from config import settings


class LeetCodeAuth:
    """Manages LeetCode authentication and cookies"""
    
    def __init__(self, cookies_path: Optional[Path] = None):
        self.cookies_path = cookies_path or settings.COOKIES_PATH
        # Ensure parent directory exists for cookies
        try:
            self.cookies_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
    
    def load_cookies(self) -> Optional[List[Dict]]:
        """
        Load cookies from file
        
        Returns:
            List of cookie dictionaries or None if error
        """
        if not self.cookies_path.exists():
            logger.warning(f"Cookie file not found: {self.cookies_path}")
            return None
        
        try:
            cookies = load_json_file(self.cookies_path)
            
            if not cookies:
                logger.error("Failed to parse cookies file")
                return None
            
            # Handle both list and dict formats
            if isinstance(cookies, dict):
                # Convert dict format to list format
                cookies = [cookies]
            
            logger.info(f"Loaded {len(cookies)} cookies from file")
            return cookies
            
        except Exception as e:
            logger.error(f"Error loading cookies: {e}")
            return None
    
    def save_cookies(self, cookies: List[Dict]) -> bool:
        """
        Save cookies to file
        
        Args:
            cookies: List of cookie dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = save_json_file(cookies, self.cookies_path)
            
            if success:
                logger.info(f"Saved {len(cookies)} cookies to file")
            else:
                logger.error("Failed to save cookies")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving cookies: {e}")
            return False
    
    def apply_cookies_to_driver(self, driver, cookies: Optional[List[Dict]] = None) -> bool:
        """
        Apply cookies to Selenium WebDriver
        
        Args:
            driver: Selenium WebDriver instance
            cookies: Optional cookie list (loads from file if None)
            
        Returns:
            bool: True if cookies applied successfully, False otherwise
            
        Raises:
            Exception: If no cookies available or all cookies fail to load
        """
        if cookies is None:
            cookies = self.load_cookies()
        
        if not cookies:
            error_msg = "❌ No cookies available! Please login to LeetCode first and save cookies."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            # Navigate to LeetCode first (required for setting cookies)
            driver.get(settings.LEETCODE_BASE_URL)
            
            # Track success/failure
            added_cookies = 0
            failed_cookies = 0
            critical_cookies = ['LEETCODE_SESSION', 'csrftoken']
            critical_missing = []
            
            # Add each cookie
            for cookie in cookies:
                try:
                    # Selenium requires specific cookie format - clean the cookie
                    if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                        # Only include fields that Selenium accepts
                        clean_cookie = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', '.leetcode.com'),
                            'path': cookie.get('path', '/'),
                        }
                        
                        # Add optional fields if present
                        if 'secure' in cookie:
                            clean_cookie['secure'] = cookie['secure']
                        if 'httpOnly' in cookie:
                            clean_cookie['httpOnly'] = cookie['httpOnly']
                        if 'expiry' in cookie:
                            clean_cookie['expiry'] = int(cookie['expiry'])
                        elif 'expirationDate' in cookie:
                            # Convert expirationDate to expiry (integer timestamp)
                            clean_cookie['expiry'] = int(cookie['expirationDate'])
                        
                        # Add sameSite if it's a valid value
                        if 'sameSite' in cookie and cookie['sameSite'] in ['Strict', 'Lax', 'None']:
                            clean_cookie['sameSite'] = cookie['sameSite']
                        
                        driver.add_cookie(clean_cookie)
                        added_cookies += 1
                        logger.debug(f"✅ Added cookie: {cookie['name']}")
                except Exception as e:
                    failed_cookies += 1
                    cookie_name = cookie.get('name', 'unknown')
                    logger.warning(f"⚠️ Failed to add cookie {cookie_name}: {e}")
                    
                    # Track if critical cookie failed
                    if cookie_name in critical_cookies:
                        critical_missing.append(cookie_name)
            
            # Check if critical cookies were added
            if critical_missing:
                error_msg = f"❌ Critical cookies failed to load: {', '.join(critical_missing)}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            if added_cookies == 0:
                error_msg = f"❌ All {failed_cookies} cookies failed to load!"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            logger.info(f"✅ Cookies applied: {added_cookies} successful, {failed_cookies} failed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error applying cookies: {e}")
            raise
    
    def extract_cookies_from_driver(self, driver) -> List[Dict]:
        """
        Extract cookies from Selenium WebDriver
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            List of cookie dictionaries
        """
        try:
            cookies = driver.get_cookies()
            logger.info(f"Extracted {len(cookies)} cookies from driver")
            return cookies
        except Exception as e:
            logger.error(f"Error extracting cookies: {e}")
            return []
    
    def validate_cookies(self, cookies: List[Dict]) -> bool:
        """
        Validate cookie structure
        
        Args:
            cookies: List of cookie dictionaries
            
        Returns:
            True if valid, False otherwise
        """
        if not cookies or not isinstance(cookies, list):
            return False
        
        # Check that essential fields exist in at least one cookie
        for cookie in cookies:
            if not isinstance(cookie, dict):
                continue
            
            if 'name' in cookie and 'value' in cookie:
                return True
        
        return False
    
    def is_authenticated(self, driver) -> bool:
        """
        Check if user is authenticated on LeetCode
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            # Navigate to LeetCode and check for user profile elements
            driver.get(settings.LEETCODE_BASE_URL)
            
            # Look for authenticated user indicators
            # This is a placeholder - actual implementation would check specific elements
            cookies = driver.get_cookies()
            
            # Check for session-related cookies
            session_cookies = ['LEETCODE_SESSION', 'csrftoken']
            has_session = any(
                cookie.get('name') in session_cookies 
                for cookie in cookies
            )
            
            return has_session
            
        except Exception as e:
            logger.error(f"Error checking authentication: {e}")
            return False
    
    def cookies_exist(self) -> bool:
        """
        Check if cookies file exists
        
        Returns:
            bool: True if cookies file exists, False otherwise
        """
        return self.cookies_path.exists() and self.cookies_path.is_file()
    
    def get_cookie_path(self) -> Path:
        """
        Get the path to the cookies file
        
        Returns:
            Path: Path object pointing to cookies.json
        """
        return self.cookies_path
    
    def extract_and_save_cookies(self, driver) -> bool:
        """
        Extract cookies from Selenium WebDriver and save to file
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract cookies from driver
            cookies = self.extract_cookies_from_driver(driver)
            
            if not cookies:
                logger.error("No cookies extracted from browser")
                return False
            
            # Ensure cookies directory exists
            self.cookies_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save cookies to file
            success = self.save_cookies(cookies)
            
            if success:
                logger.info(f"✅ Successfully saved {len(cookies)} cookies to {self.cookies_path}")
            else:
                logger.error(f"❌ Failed to save cookies to {self.cookies_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error extracting and saving cookies: {e}")
            return False
    
    def logout(self) -> bool:
        """
        Delete saved cookies (logout user)
        
        Returns:
            bool: True if cookies deleted successfully, False otherwise
        """
        try:
            if not self.cookies_exist():
                logger.warning("No cookies to delete - already logged out")
                return True
            
            self.cookies_path.unlink()
            logger.info(f"✅ Cookies deleted: {self.cookies_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cookies: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """
        Check if user is logged in (has valid cookies)
        
        Returns:
            bool: True if valid session exists, False otherwise
        """
        if not self.cookies_exist():
            return False
        
        cookies = self.load_cookies()
        
        if not cookies:
            return False
        
        # Check for LEETCODE_SESSION cookie with valid value
        has_session = any(
            cookie.get('name') == 'LEETCODE_SESSION' and 
            cookie.get('value') and 
            len(cookie.get('value', '')) > 10
            for cookie in cookies
        )
        
        return has_session
