"""Utility classes for PyAndroid library.

This module provides helper classes for common Android development tasks
like logging, file management, and networking.
"""

import logging
import os
import json
from typing import Any, Dict, Optional, List
from urllib.request import urlopen, Request
from urllib.error import URLError


class Logger:
    """Enhanced logging utility for Android applications."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """Initialize logger.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
    def debug(self, message: str, **kwargs):
        """Log debug message.
        
        Args:
            message: Debug message
            **kwargs: Additional context
        """
        self.logger.debug(f"{message} {kwargs if kwargs else ''}")
        
    def info(self, message: str, **kwargs):
        """Log info message.
        
        Args:
            message: Info message
            **kwargs: Additional context
        """
        self.logger.info(f"{message} {kwargs if kwargs else ''}")
        
    def warning(self, message: str, **kwargs):
        """Log warning message.
        
        Args:
            message: Warning message
            **kwargs: Additional context
        """
        self.logger.warning(f"{message} {kwargs if kwargs else ''}")
        
    def error(self, message: str, **kwargs):
        """Log error message.
        
        Args:
            message: Error message
            **kwargs: Additional context
        """
        self.logger.error(f"{message} {kwargs if kwargs else ''}")
        
    def critical(self, message: str, **kwargs):
        """Log critical message.
        
        Args:
            message: Critical message
            **kwargs: Additional context
        """
        self.logger.critical(f"{message} {kwargs if kwargs else ''}")


class FileManager:
    """File and storage management utility."""
    
    def __init__(self, app_name: str):
        """Initialize file manager.
        
        Args:
            app_name: Application name for creating app-specific directories
        """
        self.app_name = app_name
        self.app_dir = os.path.expanduser(f"~/.{app_name.lower()}")
        self.logger = Logger(f"FileManager.{app_name}")
        
        # Create app directory if it doesn't exist
        self._ensure_app_directory()
        
    def _ensure_app_directory(self):
        """Ensure app directory exists."""
        try:
            os.makedirs(self.app_dir, exist_ok=True)
            self.logger.info(f"App directory ready: {self.app_dir}")
        except OSError as e:
            self.logger.error(f"Failed to create app directory: {e}")
            
    def get_app_directory(self) -> str:
        """Get application directory path.
        
        Returns:
            Path to application directory
        """
        return self.app_dir
        
    def write_file(self, filename: str, content: str, subdir: str = "") -> bool:
        """Write content to file.
        
        Args:
            filename: Name of file to write
            content: Content to write
            subdir: Subdirectory within app directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if subdir:
                file_dir = os.path.join(self.app_dir, subdir)
                os.makedirs(file_dir, exist_ok=True)
                filepath = os.path.join(file_dir, filename)
            else:
                filepath = os.path.join(self.app_dir, filename)
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.logger.info(f"File written successfully: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write file {filename}: {e}")
            return False
            
    def read_file(self, filename: str, subdir: str = "") -> Optional[str]:
        """Read content from file.
        
        Args:
            filename: Name of file to read
            subdir: Subdirectory within app directory
            
        Returns:
            File content or None if failed
        """
        try:
            if subdir:
                filepath = os.path.join(self.app_dir, subdir, filename)
            else:
                filepath = os.path.join(self.app_dir, filename)
                
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.logger.info(f"File read successfully: {filepath}")
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read file {filename}: {e}")
            return None
            
    def delete_file(self, filename: str, subdir: str = "") -> bool:
        """Delete file.
        
        Args:
            filename: Name of file to delete
            subdir: Subdirectory within app directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if subdir:
                filepath = os.path.join(self.app_dir, subdir, filename)
            else:
                filepath = os.path.join(self.app_dir, filename)
                
            os.remove(filepath)
            self.logger.info(f"File deleted successfully: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {filename}: {e}")
            return False
            
    def list_files(self, subdir: str = "") -> List[str]:
        """List files in directory.
        
        Args:
            subdir: Subdirectory to list
            
        Returns:
            List of filenames
        """
        try:
            if subdir:
                directory = os.path.join(self.app_dir, subdir)
            else:
                directory = self.app_dir
                
            if os.path.exists(directory):
                files = [f for f in os.listdir(directory) 
                        if os.path.isfile(os.path.join(directory, f))]
                return files
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return []
            
    def save_json(self, filename: str, data: Dict[str, Any], 
                  subdir: str = "") -> bool:
        """Save data as JSON file.
        
        Args:
            filename: JSON filename
            data: Data to save
            subdir: Subdirectory within app directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            return self.write_file(filename, json_content, subdir)
        except Exception as e:
            self.logger.error(f"Failed to save JSON {filename}: {e}")
            return False
            
    def load_json(self, filename: str, subdir: str = "") -> Optional[Dict[str, Any]]:
        """Load data from JSON file.
        
        Args:
            filename: JSON filename
            subdir: Subdirectory within app directory
            
        Returns:
            Loaded data or None if failed
        """
        try:
            content = self.read_file(filename, subdir)
            if content:
                return json.loads(content)
            return None
        except Exception as e:
            self.logger.error(f"Failed to load JSON {filename}: {e}")
            return None


class NetworkManager:
    """Network and HTTP utility for Android applications."""
    
    def __init__(self, app_name: str, timeout: int = 30):
        """Initialize network manager.
        
        Args:
            app_name: Application name for logging
            timeout: Request timeout in seconds
        """
        self.app_name = app_name
        self.timeout = timeout
        self.logger = Logger(f"NetworkManager.{app_name}")
        self.default_headers = {
            'User-Agent': f'PyAndroid-{app_name}/1.0.0'
        }
        
    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Make HTTP GET request.
        
        Args:
            url: URL to request
            headers: Optional additional headers
            
        Returns:
            Response content or None if failed
        """
        try:
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)
                
            request = Request(url, headers=request_headers)
            
            with urlopen(request, timeout=self.timeout) as response:
                content = response.read().decode('utf-8')
                
            self.logger.info(f"GET request successful: {url}")
            return content
            
        except URLError as e:
            self.logger.error(f"GET request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in GET request: {e}")
            return None
            
    def post(self, url: str, data: str, 
             headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Make HTTP POST request.
        
        Args:
            url: URL to request
            data: Data to send in request body
            headers: Optional additional headers
            
        Returns:
            Response content or None if failed
        """
        try:
            request_headers = self.default_headers.copy()
            request_headers['Content-Type'] = 'application/json'
            
            if headers:
                request_headers.update(headers)
                
            request = Request(url, 
                            data=data.encode('utf-8'), 
                            headers=request_headers,
                            method='POST')
            
            with urlopen(request, timeout=self.timeout) as response:
                content = response.read().decode('utf-8')
                
            self.logger.info(f"POST request successful: {url}")
            return content
            
        except URLError as e:
            self.logger.error(f"POST request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in POST request: {e}")
            return None
            
    def post_json(self, url: str, data: Dict[str, Any], 
                  headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP POST request with JSON data.
        
        Args:
            url: URL to request
            data: Data dictionary to send as JSON
            headers: Optional additional headers
            
        Returns:
            Response data as dictionary or None if failed
        """
        try:
            json_data = json.dumps(data)
            response = self.post(url, json_data, headers)
            
            if response:
                return json.loads(response)
            return None
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in POST JSON request: {e}")
            return None
            
    def is_connected(self, test_url: str = "https://www.google.com") -> bool:
        """Check if internet connection is available.
        
        Args:
            test_url: URL to test connectivity
            
        Returns:
            True if connected, False otherwise
        """
        try:
            request = Request(test_url, headers=self.default_headers)
            with urlopen(request, timeout=5) as response:
                return response.getcode() == 200
        except:
            return False
