"""
Blob Storage Configuration Loader

Simple function to load JSON configuration files from Azure Blob Storage.
Completely resource-agnostic - all Azure coordinates provided by caller.

Design Principle: "Dumb pipe" - loads JSON from blob, returns dict. Period.
- No caching (that's the dashboard's concern)
- No hardcoded resources (that's the dashboard's concern)
- No Streamlit dependency (that's the dashboard's concern)

The consumer app handles caching, resource coordinates, and UI integration.
"""

import json
import logging
from typing import Dict, Any

try:
    from azure.storage.blob import BlobServiceClient
    from azure.identity import DefaultAzureCredential, AzureCliCredential, ChainedTokenCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

logger = logging.getLogger(__name__)


def load_config_from_blob(
    account_url: str,
    container: str,
    blob_name: str
) -> Dict[str, Any]:
    """
    Load JSON configuration from Azure Blob Storage.

    Simple, explicit function - caller provides all Azure coordinates.
    No caching, no hardcoded resources, no UI concerns.

    Args:
        account_url: Azure Storage account URL (e.g., "https://myaccount.blob.core.windows.net")
        container: Blob container name
        blob_name: Blob file name (must include .json extension)

    Returns:
        Parsed JSON configuration as dictionary

    Raises:
        Exception: If blob fetch or JSON parse fails

    Example:
        >>> # In dashboard code
        >>> import streamlit as st
        >>> from streamlit_azure_kit.config import ConfigLoader, load_config_from_blob
        >>>
        >>> # Dashboard handles caching
        >>> @st.cache_data(ttl=300)
        >>> def get_config():
        ...     return load_config_from_blob(
        ...         account_url="https://okcdashboards.blob.core.windows.net",
        ...         container="configs",
        ...         blob_name="endpoint_config.json"
        ...     )
        >>>
        >>> # Dashboard uses the config
        >>> config_dict = get_config()
        >>> config = ConfigLoader(config_dict=config_dict)

    Authentication:
        Uses ChainedTokenCredential:
        - Local dev: Azure CLI credential (az login)
        - Production: Managed Identity (DefaultAzureCredential)
    """
    if not AZURE_AVAILABLE:
        raise ImportError(
            "Azure storage dependencies not available. "
            "Install with: pip install azure-storage-blob azure-identity"
        )

    try:
        # Get authenticated client
        credential = ChainedTokenCredential(
            AzureCliCredential(),
            DefaultAzureCredential()
        )
        blob_service = BlobServiceClient(account_url, credential=credential)
        blob_client = blob_service.get_blob_client(container, blob_name)

        # Download and parse
        blob_data = blob_client.download_blob().readall()
        config = json.loads(blob_data)

        logger.info(f"✅ Config loaded from blob: {container}/{blob_name}")
        return config

    except Exception as e:
        logger.error(f"Failed to load config from blob: {str(e)}")
        raise
