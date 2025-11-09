"""
Generic Azure SQL Database connection utilities.
Works with any Azure SQL setup via configuration.
"""

import os
import time
import logging
import urllib.parse
from functools import wraps
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def retry_on_connection_error(max_retries, delay):
    """Decorator to retry database operations on connection errors (for serverless wake-up)."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    # Check if it's a paused database error
                    error_msg = str(e).lower()
                    if any(keyword in error_msg for keyword in [
                        '40613', 'database unavailable'
                    ]):
                        if attempt < max_retries:
                            sleep_time = delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(f"Database connection error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                            logger.info(f"Retrying in {sleep_time:.1f} seconds...")
                            time.sleep(sleep_time)
                            continue
                    # If not a paused database error or max retries reached, re-raise
                    raise
            raise last_exception

        return wrapper

    return decorator


def create_engine_from_config(db_config: Dict[str, Any]) -> object:
    """
    Create database engine from direct configuration dictionary.

    Args:
        db_config: Database configuration containing:
            - server: Database server hostname
            - database: Database name
            - db_engine_type: 'serverless' or 'always_on'

    Returns:
        SQLAlchemy engine configured for the specified database
    """
    server = db_config['server']
    database = db_config['database']
    engine_type = db_config['db_engine_type']  # 'serverless' or 'always_on'

    # Read operational parameters from config
    # All parameters read from JSON with sensible defaults as fallback
    # For serverless databases: use pool_size=0, max_overflow=0 in JSON
    # For always-on databases: use pool_size=10+, max_overflow=20+ in JSON
    retry_config = db_config.get('retry_config', {'max_retries': 6, 'delay': 2.0})
    connection_timeout = db_config.get('connection_timeout', 30)

    # Detect environment
    environment = os.getenv('ENVIRONMENT', 'production')
    is_local = environment == 'local'

    if is_local:
        # Local development: Use Azure CLI authentication
        logger.info(f"🏠 Creating local engine for {database} using Azure CLI authentication")

        try:
            from azure.identity import AzureCliCredential
            import struct

            # Get access token using Azure CLI credentials
            credential = AzureCliCredential()
            database_token = credential.get_token('https://database.windows.net/.default')

            # Convert token to required format for pyodbc
            token_bytes = database_token.token.encode("UTF-16-LE")
            token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

            # Connection string WITHOUT authentication parameter
            connection_string = (
                f"Driver={{ODBC Driver 18 for SQL Server}};"
                f"Server={server};"
                f"Database={database};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout={connection_timeout};"
            )

            # Engine configuration - all values from JSON with defaults
            engine_config = {
                "pool_pre_ping": db_config.get('pool_pre_ping', True),
                "pool_size": db_config.get('pool_size', 10),
                "max_overflow": db_config.get('max_overflow', 20),
                "pool_timeout": db_config.get('pool_timeout', 30),
                "pool_recycle": db_config.get('pool_recycle', 3600)
            }

            # Create connection with access token
            SQL_COPT_SS_ACCESS_TOKEN = 1256
            engine = create_engine(
                f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}",
                fast_executemany=True,
                connect_args={"attrs_before": {SQL_COPT_SS_ACCESS_TOKEN: token_struct}},
                **engine_config
            )

        except Exception as e:
            # Sanitize error message to prevent potential token/credential leaks from third-party libraries
            error_msg = str(e)
            if any(word in error_msg.lower() for word in ['token', 'password', 'secret', 'key=', 'credential']):
                error_msg = "Authentication error (details redacted for security)"
            raise Exception(f"Failed to create local database engine for {database}: {error_msg}. Run 'az login' first.")

    else:
        # Production: Use Azure Managed Identity
        logger.info(f"☁️ Creating production engine for {database} using Managed Identity")

        try:
            connection_string = (
                f"mssql+pyodbc://{server}/{database}?"
                f"driver=ODBC+Driver+18+for+SQL+Server&"
                f"authentication=ActiveDirectoryMsi"
            )

            # Engine configuration - all values from JSON with defaults
            engine_config = {
                "pool_pre_ping": db_config.get('pool_pre_ping', True),
                "pool_size": db_config.get('pool_size', 10),
                "max_overflow": db_config.get('max_overflow', 20),
                "pool_timeout": db_config.get('pool_timeout', 30),
                "pool_recycle": db_config.get('pool_recycle', 3600)
            }

            engine = create_engine(
                connection_string,
                fast_executemany=True,
                connect_args={"timeout": connection_timeout},
                **engine_config
            )

        except Exception as e:
            # Sanitize error message to prevent potential token/credential leaks from third-party libraries
            error_msg = str(e)
            if any(word in error_msg.lower() for word in ['token', 'password', 'secret', 'key=', 'credential']):
                error_msg = "Authentication error (details redacted for security)"
            raise Exception(f"Failed to create production database engine for {database}: {error_msg}")

    # Test the connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            test_result = result.fetchone()
            if not (test_result and test_result[0] == 1):
                raise Exception(f"Database connection test failed for {database}")
    except Exception as e:
        # Sanitize error message to prevent potential token/credential leaks
        error_msg = str(e)
        if any(word in error_msg.lower() for word in ['token', 'password', 'secret', 'key=', 'credential']):
            error_msg = "Connection error (details redacted for security)"
        raise Exception(f"Failed to connect to {database}: {error_msg}")

    logger.info(f"✅ Database engine ready: {database} ({engine_type})")
    return engine


def test_database_health(engine, db_name: str) -> bool:
    """Test database connectivity with an existing engine."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            test_result = result.fetchone()

            if test_result and test_result[0] == 1:
                logger.info(f"✅ {db_name} database health check successful")
                return True
            else:
                logger.error(f"❌ {db_name} database health check failed - unexpected result")
                return False

    except Exception as e:
        logger.error(f"❌ {db_name} database health check failed: {e}")
        return False


def validate_database_connection(engine, db_name: str, table_name: str) -> Dict[str, Any]:
    """
    Validate database connection with basic diagnostics.

    Args:
        engine: SQLAlchemy engine
        db_name: Database name for logging
        table_name: Optional table to check (e.g., 'sync_metadata')

    Returns:
        Dict with validation results
    """
    validation = {
        "connection_healthy": False,
        "table_exists": False,
        "database_server": "unknown",
        "database_name": "unknown",
        "database_type": db_name,
    }

    try:
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1"))
            if result.fetchone()[0] == 1:
                validation["connection_healthy"] = True

            # Check if specific table exists
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                validation["table_exists"] = True
                validation["row_count"] = result.fetchone()[0]
            except Exception:
                validation["table_exists"] = False

            # Get database info
            try:
                result = conn.execute(text("SELECT @@SERVERNAME, DB_NAME()"))
                server_info = result.fetchone()
                if server_info:
                    validation["database_server"] = server_info[0]
                    validation["database_name"] = server_info[1]
            except Exception:
                pass

    except Exception as e:
        validation["connection_error"] = str(e)
        logger.error(f"Connection validation failed for {db_name}: {e}")

    return validation