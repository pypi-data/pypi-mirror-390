"""
FeatureMesh Python Client Library.

This package provides a Python client for interacting with the FeatureMesh API,
supporting both offline (via SQL executors) and online query execution.

Main Components:
    - OfflineClient: Execute FeatureQL queries via local SQL backends (DuckDB, Trino, BigQuery, DataFusion)
    - OnlineClient: Execute FeatureQL queries via the FeatureMesh serving API
    - QueryResult: Data class representing query execution results
    - TranslateResult: Data class representing FeatureQL-to-SQL translation results
    - Backend: Enum for supported database backends
    - Configuration functions: set_default, get_default, get_all_defaults

Example:
    >>> from featuremesh import OfflineClient, Backend
    >>> import duckdb
    >>> 
    >>> # Create an offline client with DuckDB
    >>> client = OfflineClient(
    ...     access_token="your_access_token",
    ...     backend=Backend.DUCKDB,
    ...     sql_executor=duckdb.execute
    ... )
    >>> 
    >>> # Execute a query
    >>> result = client.query("SELECT * FROM my_table")
    >>> print(result.dataframe)

For Jupyter notebooks, load the magic extension:
    >>> %load_ext featuremesh
    >>> %%featureql --show-sql
    ... SELECT * FROM my_table
"""

from .client import OfflineClient, OnlineClient
from .access import AccessClient, create_access_client, decode_token, generate_access_token
from .magic import load_ipython_extension
from .config import (
    set_default,
    get_default,
    get_all_defaults,
    Backend,
    __version__,
    get_user_agent,
    get_auth_header,
    get_kernel_id,
)
from .results import QueryResult, TranslateResult, Error, Warning
from .display import (
    display_query_result,
    display_translate_result,
    display_errors,
    display_warnings,
)

__all__ = [
    "OfflineClient",
    "OnlineClient",
    "AccessClient",
    "create_access_client",
    "decode_token",
    "generate_access_token",
    "set_default",
    "get_default",
    "get_all_defaults",
    "get_user_agent",
    "get_auth_header",
    "get_kernel_id",
    "load_ipython_extension",
    "Backend",
    "__version__",
    "QueryResult",
    "TranslateResult",
    "Error",
    "Warning",
    "display_query_result",
    "display_translate_result",
    "display_errors",
    "display_warnings",
]
