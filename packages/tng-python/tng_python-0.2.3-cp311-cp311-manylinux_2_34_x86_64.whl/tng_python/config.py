"""
TNG Python Configuration Manager
Centralized configuration loading and management
"""

import sys
from pathlib import Path
from typing import Optional, Any


class ConfigManager:
    """Centralized configuration manager for TNG Python"""

    _instance: Optional['ConfigManager'] = None
    _config: Optional[Any] = None

    def __new__(cls) -> 'ConfigManager':
        """Singleton pattern to ensure single config instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration manager"""
        if not hasattr(self, '_initialized'):
            self._initialized = True

    def load_config(self, config_path: Optional[Path] = None) -> Any:
        """
        Load configuration from tng_config.py
        
        Args:
            config_path: Optional path to config file (defaults to cwd/tng_config.py)
            
        Returns:
            TngConfig class instance
            
        Raises:
            FileNotFoundError: If tng_config.py is not found
            ImportError: If config cannot be imported
        """
        if self._config is not None:
            return self._config

        # Use provided path or default to current working directory
        if config_path is None:
            config_path = Path.cwd() / "tng_config.py"

        if not config_path.exists():
            raise FileNotFoundError(f"tng_config.py not found at {config_path}")

        # Add config directory to Python path temporarily
        config_dir = str(config_path.parent)
        if config_dir not in sys.path:
            sys.path.insert(0, config_dir)
            path_added = True
        else:
            path_added = False

        try:
            # Import the config module
            import tng_config

            # Reload module if it was already imported (for testing/development)
            if hasattr(tng_config, '__file__'):
                import importlib
                importlib.reload(tng_config)

            self._config = tng_config.TngConfig
            return self._config

        except ImportError as e:
            raise ImportError(f"Failed to import tng_config: {e}")

        finally:
            # Clean up Python path
            if path_added and config_dir in sys.path:
                sys.path.remove(config_dir)

    def get_config(self) -> Any:
        """
        Get current configuration instance
        
        Returns:
            TngConfig class instance
            
        Raises:
            RuntimeError: If config hasn't been loaded yet
        """
        if self._config is None:
            return self.load_config()

        return self._config

    def reload_config(self, config_path: Optional[Path] = None) -> Any:
        """
        Force reload configuration from file
        
        Args:
            config_path: Optional path to config file
            
        Returns:
            TngConfig class instance
        """
        self._config = None  # Clear cached config
        return self.load_config(config_path)

    def get_base_url(self) -> str:
        """
        Get base URL from configuration
        
        Returns:
            Base URL string with trailing slash removed
        """
        config = self.get_config()
        return config.BASE_URL.rstrip('/')

    def get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration
        
        Returns:
            API key string or None if not set
        """
        config = self.get_config()
        return getattr(config, 'API_KEY', None)

    def get_enabled_config(self) -> dict:
        """
        Extract only enabled/configured settings from user's tng_config.py
        
        Returns:
            Dictionary with only non-default/enabled configuration values
        """
        config = self.get_config()
        enabled_config = {}

        # Framework settings (always include framework, even if generic)
        if hasattr(config, 'FRAMEWORK') and config.FRAMEWORK:
            enabled_config['framework'] = config.FRAMEWORK

        if hasattr(config, 'TEST_FRAMEWORK') and config.TEST_FRAMEWORK:
            enabled_config['test_framework'] = config.TEST_FRAMEWORK

        if hasattr(config, 'TEST_DIRECTORY') and config.TEST_DIRECTORY:
            # Convert to absolute path
            test_dir = Path(config.TEST_DIRECTORY)
            if not test_dir.is_absolute():
                test_dir = Path.cwd() / test_dir
            enabled_config['test_directory'] = str(test_dir)

        # Database settings (always include ORM, even if none)
        if hasattr(config, 'ORM') and config.ORM:
            enabled_config['orm'] = config.ORM

        if hasattr(config, 'DATABASES') and config.DATABASES:
            enabled_config['databases'] = config.DATABASES

        if hasattr(config, 'ASYNC_DATABASE_SUPPORT') and config.ASYNC_DATABASE_SUPPORT:
            enabled_config['async_db'] = True

        # Authentication settings (only if enabled)
        if hasattr(config, 'AUTHENTICATION_ENABLED') and config.AUTHENTICATION_ENABLED:
            enabled_config['authentication_enabled'] = True

            if hasattr(config, 'AUTHENTICATION_LIBRARY') and config.AUTHENTICATION_LIBRARY:
                enabled_config['auth_library'] = config.AUTHENTICATION_LIBRARY

            if hasattr(config, 'AUTHORIZATION_LIBRARY') and config.AUTHORIZATION_LIBRARY:
                enabled_config['authz_library'] = config.AUTHORIZATION_LIBRARY

            # Include auth methods if configured
            if hasattr(config, 'AUTHENTICATION_METHODS') and config.AUTHENTICATION_METHODS:
                auth_methods_with_content = []

                for auth_method in config.AUTHENTICATION_METHODS:
                    method_info = auth_method.copy()

                    # Load the authentication file content
                    file_location = auth_method.get('file_location')
                    if file_location:
                        try:
                            # Convert relative path to absolute
                            auth_file_path = Path(file_location)
                            if not auth_file_path.is_absolute():
                                auth_file_path = Path.cwd() / auth_file_path

                            # Read the file content
                            if auth_file_path.exists():
                                with open(auth_file_path, 'r', encoding='utf-8') as f:
                                    method_info['file_content'] = f.read()
                            else:
                                method_info['file_content'] = None
                                method_info['file_error'] = f"File not found: {auth_file_path}"
                        except Exception as e:
                            method_info['file_content'] = None
                            method_info['file_error'] = f"Error reading file: {str(e)}"

                    auth_methods_with_content.append(method_info)

                enabled_config['auth_methods'] = auth_methods_with_content

        # Testing libraries (only if not default/none)
        if hasattr(config, 'MOCK_LIBRARY') and config.MOCK_LIBRARY not in ["none", "unittest.mock"]:
            enabled_config['mock_library'] = config.MOCK_LIBRARY

        if hasattr(config, 'HTTP_MOCK_LIBRARY') and config.HTTP_MOCK_LIBRARY:
            enabled_config['http_mock_library'] = config.HTTP_MOCK_LIBRARY

        if hasattr(config, 'FACTORY_LIBRARY') and config.FACTORY_LIBRARY:
            enabled_config['factory_library'] = config.FACTORY_LIBRARY

        # Email settings (always include, even if none)
        if hasattr(config, 'EMAIL_BACKEND') and config.EMAIL_BACKEND:
            enabled_config['email_backend'] = config.EMAIL_BACKEND

        # Job queue settings (always include, even if none)
        if hasattr(config, 'JOB_QUEUE') and config.JOB_QUEUE:
            enabled_config['job_queue'] = config.JOB_QUEUE

        # ML/AI settings (only if enabled)
        if hasattr(config, 'EXPERIMENT_TRACKING') and config.EXPERIMENT_TRACKING:
            enabled_config['ml_tracking'] = True

        if hasattr(config, 'MODEL_REGISTRY') and config.MODEL_REGISTRY:
            enabled_config['model_registry'] = config.MODEL_REGISTRY

        # Dependency file (if specified)
        if hasattr(config, 'DEPENDENCY_FILE') and config.DEPENDENCY_FILE:
            enabled_config['dependency_file'] = config.DEPENDENCY_FILE

        if hasattr(config, 'TEST_EXAMPLES') and config.TEST_EXAMPLES:
            enabled_config['test_examples'] = config.TEST_EXAMPLES

        # Source code reading settings (only if enabled)
        if hasattr(config, 'READ_FILE_SOURCE_CODE') and config.READ_FILE_SOURCE_CODE:
            enabled_config['read_file_source_code'] = True

        # FastAPI app location (for dynamic loading)
        if hasattr(config, 'FASTAPI_APP_PATH') and config.FASTAPI_APP_PATH:
            enabled_config['fastapi_app_path'] = config.FASTAPI_APP_PATH

        return enabled_config

    def display_config_summary(self) -> None:
        """Display a summary of current configuration settings"""
        try:
            config = self.get_config()

            print("\nConfiguration Summary:")
            print(f"  Base URL: {config.BASE_URL}")

            # Mask API key for security
            api_key = getattr(config, 'API_KEY', 'Not set')
            if api_key and api_key != 'Not set':
                masked_key = f"{api_key[:8]}...{api_key[-8:]}" if len(api_key) > 16 else "***"
                print(f"  API Key: {masked_key}")
            else:
                print("  API Key: Not set")

            # Display other settings
            other_settings = ['FRAMEWORK', 'TEST_FRAMEWORK', 'ORM', 'EMAIL_BACKEND', 'JOB_QUEUE', 'FASTAPI_APP_PATH']
            for setting in other_settings:
                value = getattr(config, setting, 'Not set')
                print(f"  {setting}: {value}")

        except Exception as e:
            print(f"Failed to display config summary: {e}")


config_manager = ConfigManager()


def get_config() -> Any:
    """
    Convenience function to get configuration
    
    Returns:
        TngConfig class instance
    """
    return config_manager.get_config()


def get_base_url() -> str:
    """
    Convenience function to get base URL
    
    Returns:
        Base URL string
    """
    return config_manager.get_base_url()


def get_api_key() -> Optional[str]:
    """
    Convenience function to get API key
    
    Returns:
        API key string or None
    """
    return config_manager.get_api_key()


def get_enabled_config() -> dict:
    """
    Convenience function to get enabled configuration
    
    Returns:
        Dictionary with only non-default/enabled configuration values
    """
    return config_manager.get_enabled_config()
