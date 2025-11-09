"""
Direct JSON-based configuration system.
Simple, explicit, and self-documenting - no indirection or resource resolution.
"""

import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Direct JSON-based configuration system.

    Features:
    - Environment-aware configuration (local vs production)
    - Direct configuration values - no resource resolution needed
    - Clear database and storage configurations
    - Parameter management per endpoint
    - Self-documenting JSON structure

    Usage:
        # Load from file (existing apps)
        config = ConfigLoader("endpoint_config.json")

        # Load from dict (blob storage or other sources)
        config_dict = load_config_from_blob(...)
        config = ConfigLoader.from_dict(config_dict)
    """

    def __init__(self, config_file: str):
        """
        Initialize configuration system from JSON file.

        Environment Detection:
            Reads ENVIRONMENT variable from os.environ (should be set by application).
            Defaults to 'production' if not set.

            Applications should call load_dotenv() before importing this module:
                from dotenv import load_dotenv
                load_dotenv()  # Load .env file
                from streamlit_azure_kit.config import ConfigLoader

        Args:
            config_file: Path to JSON config file

        Example:
            >>> from dotenv import load_dotenv
            >>> load_dotenv()
            >>> config = ConfigLoader("config/endpoint_config.json")
            >>> db_config = config.get_database_config("my_app", "primary_db")
        """
        # Load JSON from file
        config_dict = self._load_from_file(config_file)

        # Initialize from dict
        self._initialize(config_dict, config_file=config_file)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]):
        """
        Initialize configuration system from pre-loaded dictionary.

        Use this when config is loaded from blob storage or other source.
        Bypasses file I/O entirely - just processes the config dict.

        Environment Detection:
            Reads ENVIRONMENT variable from os.environ (should be set by application).
            Defaults to 'production' if not set.

            Applications should call load_dotenv() before importing this module:
                from dotenv import load_dotenv
                load_dotenv()  # Load .env file
                from streamlit_azure_kit.config import ConfigLoader

        Args:
            config_dict: Pre-loaded configuration dictionary

        Returns:
            ConfigLoader instance initialized from dict

        Example:
            >>> from dotenv import load_dotenv
            >>> load_dotenv()
            >>> config_dict = load_config_from_blob(
            ...     account_url="https://myaccount.blob.core.windows.net",
            ...     container="configs",
            ...     blob_name="endpoint_config.json"
            ... )
            >>> config = ConfigLoader.from_dict(config_dict)
            >>> db_config = config.get_database_config("my_app", "primary_db")
        """
        instance = cls.__new__(cls)  # Create instance without calling __init__
        instance._initialize(config_dict, config_file=None)
        return instance

    def _load_from_file(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.

        This is Part A: File I/O layer, separated from config processing.

        Args:
            config_file: Path to JSON config file

        Returns:
            Parsed JSON as dictionary

        Raises:
            ValueError: If file not found or invalid JSON
        """
        try:
            with open(config_file, 'r') as f:
                config_dict = json.load(f)
            logger.info(f"✅ Configuration loaded from {config_file}")
            return config_dict
        except FileNotFoundError:
            raise ValueError(f"Configuration file not found: {config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")

    def _initialize(self, config_dict: Dict[str, Any], config_file: str = None):
        """
        Initialize from configuration dictionary.

        This is Part B: Config processing, independent of source.
        Works the same whether config came from file, blob, or anywhere else.

        Environment Detection:
            Reads ENVIRONMENT variable from os.environ (should be set by application).
            Defaults to 'production' if not set.

            Applications should call load_dotenv() before importing this module:
                from dotenv import load_dotenv
                load_dotenv()  # Load .env file
                from streamlit_azure_kit.config import ConfigLoader

        Args:
            config_dict: Configuration dictionary
            config_file: Optional file path (for logging only)
        """
        # Store config
        self.config = config_dict
        self.config_file = config_file  # May be None for blob-loaded configs

        # Read environment - application is responsible for loading .env
        # See: https://12factor.net/config
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.is_local = self.environment == 'local'

        # Log initialization
        source = f"file {config_file}" if config_file else "dictionary"
        env_status = 'set' if os.getenv('ENVIRONMENT') else 'not set, defaulting to production'
        logger.info(
            f"ConfigLoader initialized from {source} "
            f"for {self.environment} environment "
            f"(ENVIRONMENT={env_status})"
        )

    def get_database_config(self, endpoint_name: str, db_key: str) -> Dict[str, Any]:
        """
        Get database configuration for an endpoint.
        Supports both direct objects and references to _database_definitions.

        Args:
            endpoint_name: Name of the endpoint (e.g., 'streamlit_dashboard', 'completed_orders')
            db_key: Database key from JSON (e.g., 'primary_db', 'secondary_db')

        Returns:
            Dict with database configuration details
        """
        try:
            db_ref = self.config[endpoint_name][self.environment][db_key]
        except KeyError:
            raise ValueError(
                f"Database config not found: {endpoint_name}.{self.environment}.{db_key}. "
                f"Check that '{endpoint_name}' exists in endpoint_config.json "
                f"and has a '{self.environment}' section with '{db_key}' defined."
            )

        # If it's a string reference, validate it exists and resolve it
        if isinstance(db_ref, str):
            if db_ref not in self.config.get("_database_definitions", {}):
                available_refs = list(self.config.get("_database_definitions", {}).keys())
                raise ValueError(
                    f"Database reference '{db_ref}' not found in _database_definitions. "
                    f"Referenced by: {endpoint_name}.{self.environment}.{db_key}\n"
                    f"Available references: {available_refs}"
                )
            return self.config["_database_definitions"][db_ref]

        # Otherwise return as-is (direct object)
        return db_ref

    def get_storage_config(self, endpoint_name: str, storage_key: str) -> Dict[str, Any]:
        """
        Get storage configuration for an endpoint.
        Supports both direct objects and references to _storage_definitions.

        Args:
            endpoint_name: Name of the endpoint (e.g., 'streamlit_dashboard', 'completed_orders')
            storage_key: Storage key from JSON (e.g., 'model_storage', 'data_storage')

        Returns:
            Dict with storage configuration details
        """
        try:
            storage_ref = self.config[endpoint_name][self.environment][storage_key]
        except KeyError:
            raise ValueError(
                f"Storage config not found: {endpoint_name}.{self.environment}.{storage_key}. "
                f"Check that '{endpoint_name}' exists in endpoint_config.json "
                f"and has a '{self.environment}' section with '{storage_key}' defined."
            )

        # If it's a string reference, validate it exists and resolve it
        if isinstance(storage_ref, str):
            if storage_ref not in self.config.get("_storage_definitions", {}):
                available_refs = list(self.config.get("_storage_definitions", {}).keys())
                raise ValueError(
                    f"Storage reference '{storage_ref}' not found in _storage_definitions. "
                    f"Referenced by: {endpoint_name}.{self.environment}.{storage_key}\n"
                    f"Available references: {available_refs}"
                )
            return self.config["_storage_definitions"][storage_ref]

        # Otherwise return as-is (direct object)
        return storage_ref

    def get_parameters(self, endpoint_name: str) -> Dict[str, Any]:
        """
        Get endpoint-specific parameters.

        Args:
            endpoint_name: Name of the endpoint (e.g., 'streamlit_dashboard', 'completed_orders')

        Returns:
            Dict with endpoint parameters
        """
        try:
            return self.config[endpoint_name][self.environment].get('parameters', {})
        except KeyError:
            logger.warning(f"Parameters not found for {endpoint_name}.{self.environment}")
            return {}

    def get_endpoint_names(self) -> list:
        """Get list of configured endpoint names (excludes documentation entries)."""
        return [name for name in self.config.keys() if not name.startswith('_')]

    def get_environments(self, endpoint_name: str) -> list:
        """Get list of configured environments for an endpoint."""
        if endpoint_name not in self.config:
            return []
        return list(self.config[endpoint_name].keys())




# Convenience function for backward compatibility
def load_config(config_file: str) -> ConfigLoader:
    """Load configuration from JSON file."""
    return ConfigLoader(config_file)
