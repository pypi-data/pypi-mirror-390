"""
Azure Blob Storage connection utilities.
Works with any Azure Storage account via configuration.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def create_blob_client_from_config(storage_config: Dict[str, Any]) -> object:
    """
    Create Azure Blob Storage client from configuration dictionary.

    Args:
        storage_config: Storage configuration containing:
            - account_name: Storage account name (required)
            - container_name: Default container (optional)
            - connection_timeout: HTTP timeout in seconds (optional, default: 20)
            - max_single_put_size: Max single upload size in bytes (optional)
            - max_block_size: Block blob size in bytes (optional)

    Returns:
        BlobServiceClient configured for the specified storage account

    Example:
        >>> storage_config = config.get_storage_config("my_app", "blob_storage")
        >>> blob_client = create_blob_client_from_config(storage_config)
        >>> container = blob_client.get_container_client("mycontainer")
    """
    account_name = storage_config['account_name']
    account_url = f"https://{account_name}.blob.core.windows.net"

    # Detect environment
    environment = os.getenv('ENVIRONMENT', 'production')
    is_local = environment == 'local'

    if is_local:
        # Local development: Use Azure CLI authentication
        logger.info(f"🏠 Creating local blob client for {account_name} using Azure CLI authentication")

        try:
            from azure.identity import AzureCliCredential
            from azure.storage.blob import BlobServiceClient

            credential = AzureCliCredential()

            # Build client with optional configuration
            client_kwargs = {}
            if 'connection_timeout' in storage_config:
                client_kwargs['connection_timeout'] = storage_config['connection_timeout']
            if 'max_single_put_size' in storage_config:
                client_kwargs['max_single_put_size'] = storage_config['max_single_put_size']
            if 'max_block_size' in storage_config:
                client_kwargs['max_block_size'] = storage_config['max_block_size']

            blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=credential,
                **client_kwargs
            )

        except Exception as e:
            # Sanitize error message to prevent potential credential leaks
            error_msg = str(e)
            if any(word in error_msg.lower() for word in ['token', 'password', 'secret', 'key=', 'credential']):
                error_msg = "Authentication error (details redacted for security)"
            raise Exception(f"Failed to create local blob client for {account_name}: {error_msg}. Run 'az login' first.")

    else:
        # Production: Use Azure Managed Identity
        logger.info(f"☁️ Creating production blob client for {account_name} using Managed Identity")

        try:
            from azure.identity import DefaultAzureCredential
            from azure.storage.blob import BlobServiceClient

            credential = DefaultAzureCredential()

            # Build client with optional configuration
            client_kwargs = {}
            if 'connection_timeout' in storage_config:
                client_kwargs['connection_timeout'] = storage_config['connection_timeout']
            if 'max_single_put_size' in storage_config:
                client_kwargs['max_single_put_size'] = storage_config['max_single_put_size']
            if 'max_block_size' in storage_config:
                client_kwargs['max_block_size'] = storage_config['max_block_size']

            blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=credential,
                **client_kwargs
            )

        except Exception as e:
            # Sanitize error message to prevent potential credential leaks
            error_msg = str(e)
            if any(word in error_msg.lower() for word in ['token', 'password', 'secret', 'key=', 'credential']):
                error_msg = "Authentication error (details redacted for security)"
            raise Exception(f"Failed to create production blob client for {account_name}: {error_msg}")

    # Test the connection
    try:
        # Simple health check - list containers (lightweight operation)
        _ = list(blob_service_client.list_containers(max_results=1))
        logger.info(f"✅ Blob storage client ready: {account_name}")
    except Exception as e:
        # Sanitize error message
        error_msg = str(e)
        if any(word in error_msg.lower() for word in ['token', 'password', 'secret', 'key=', 'credential']):
            error_msg = "Connection error (details redacted for security)"
        raise Exception(f"Failed to connect to blob storage {account_name}: {error_msg}")

    return blob_service_client