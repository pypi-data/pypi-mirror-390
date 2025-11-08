"""
FeatureMesh Client implementations.

This module provides client classes for interacting with the FeatureMesh API:
- BaseClient: Abstract base class for all clients
- OfflineClient: Translates FeatureQL to SQL and executes via local SQL backends
- OnlineClient: Executes FeatureQL queries via the FeatureMesh serving API

The clients handle all API communication, error handling, and result formatting.
"""

import requests
import pandas as pd
from typing import Callable, Dict, Any
import traceback

from .utils.utils_slt import return_slt
from .results import Error, Warning, TranslateResult, QueryResult

from .config import (
    OFFLINE_BACKENDS,
    get_auth_header,
    get_default,
    Backend,
    get_user_agent,
    __version__,
)

__all__ = ["BaseClient", "OfflineClient", "OnlineClient"]


def parse_warnings_and_errors(
    response: Dict[str, Any],
) -> tuple[list[Warning], list[Error]]:
    """
    Parse warnings and errors from API response into dataclass objects.

    Args:
        response: The API response dictionary

    Returns:
        Tuple of (warnings, errors) as dataclass objects
    """
    if response is None or not isinstance(response, dict):
        raise ValueError(f"Response is None or not a dictionary: {response=}")

    # Parse errors (handle None case)
    error_dicts = response.get("errors") or []
    errors = [Error.from_dict(error) for error in error_dicts] if error_dicts else []

    if errors:
        return [], errors

    # Parse warnings
    response_data = response.get("data")
    if response_data is None or not isinstance(response_data, dict):
        return [], []

    warning_dicts = response_data.get("warnings") or []
    warnings = (
        [Warning.from_dict(warning) for warning in warning_dicts]
        if warning_dicts
        else []
    )

    return warnings, []


class BaseClient:
    """
    Base class for FeatureMesh clients.
    
    Attributes:
        access_token: User project token for API authentication
    """

    def __init__(self, access_token: str | None) -> None:
        """
        Initialize the base client.
        
        Args:
            access_token: Optional user project token. If None, uses default from config.
        """
        self.access_token = (
            access_token if access_token is not None else get_default("access_token")
        )


class OfflineClient(BaseClient):
    """
    Client for offline FeatureMesh queries using various database backends.
    
    Translates FeatureQL queries to SQL via the FeatureMesh API and executes
    them using a provided SQL executor function.
    
    Attributes:
        access_token: User project token for API authentication
        backend: Database backend (DuckDB, Trino, BigQuery, DataFusion)
        sql_executor: Function that executes SQL and returns a DataFrame
        host: API host URL
        path: API endpoint path
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
    """

    def __init__(
        self,
        access_token: str,
        backend: Backend,
        sql_executor: Callable[[str], pd.DataFrame],
    ) -> None:
        """
        Initialize the offline client.
        
        Args:
            access_token: User project token for API authentication
            backend: Database backend to use
            sql_executor: Function that executes SQL and returns a DataFrame
            
        Raises:
            ValueError: If backend is not supported for offline use
        """
        super().__init__(access_token)
        self.backend = backend
        self.sql_executor = sql_executor
        self.host = get_default("registry.host")
        self.path = get_default("registry.path")
        self.timeout = get_default("registry.timeout")
        self.verify_ssl = get_default("registry.verify_ssl")

        if self.backend.name not in [backend.name for backend in OFFLINE_BACKENDS]:
            raise ValueError(
                f"Unsupported backend: {self.backend}. Must be one of: {OFFLINE_BACKENDS}"
            )

    def translate(self, featureql: str, debug_mode: bool = None) -> TranslateResult:
        """
        Translate a FeatureQL query to SQL using the FeatureMesh API.

        Args:
            featureql: FeatureQL query string
            debug_mode: Whether to enable debug mode

        Returns:
            TranslateResult object containing the translation results.
            Errors are captured in the result.errors attribute instead of raising exceptions.
        """

        if debug_mode is None:
            debug_mode = get_default("debug_mode")

        result = TranslateResult(
            featureql=featureql,
            backend=self.backend.name,
            debug_mode=debug_mode,
            client_type="OfflineClient",
        )

        params_post = {
            "query": featureql,
            "language": self.backend.name,
            "debug_mode": debug_mode,
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": get_user_agent(),
        } | get_auth_header(self.access_token)

        # Detect misconfigurations and network errors
        try:
            response = requests.post(
                f"{self.host}{self.path}",
                json=params_post,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        except Exception as e:
            error = Error(
                code="NETWORK_ERROR",
                message=f"Contacting FeatureMesh API endpoint {self.host}{self.path} failed with error: {e}",
                stack_trace=traceback.format_exc().split("\n"),
            )
            result.errors.append(error)
            return result

        # Detect JSON parsing errors
        response_json = None
        try:
            response_json = response.json()
        except Exception as e:
            error = Error(
                code="JSON_PARSE_ERROR",
                message=f"Failed to parse JSON response. Status code: {response.status_code}. Error: {e}",
                context=f"featureql={featureql.strip()}, backend={self.backend.name}, debug_mode={debug_mode}",
            )
            result.errors.append(error)
            return result

        result.full_response = response_json

        # Parse warnings and errors from API response
        warnings, errors = parse_warnings_and_errors(response_json)
        result.warnings = warnings
        result.errors = errors

        # Extract SQL and debug logs only if no errors
        if not result.errors and response_json.get("data"):
            result.sql = response_json.get("data", {}).get("query_sql")
            if debug_mode:
                result.debug_logs = response_json.get("data", {}).get("debug_logs", {})

        return result

    def query(
        self,
        featureql: str,
        debug_mode: bool | None = None,
    ) -> QueryResult:
        """
        Run a FeatureQL query and return complete results.

        Args:
            featureql: FeatureQL query string
            debug_mode: If True, enable debug mode for detailed query information

        Returns:
            QueryResult object containing sql, dataframe, slt, and metadata.
            Errors are captured in the result.errors attribute instead of raising exceptions.
        """
        if debug_mode is None:
            debug_mode = get_default("debug_mode")

        # Translate to SQL
        translate_result = self.translate(featureql, debug_mode=debug_mode)

        # Initialize query result from translate result
        result = QueryResult(
            featureql=featureql,
            sql=translate_result.sql,
            warnings=translate_result.warnings,
            errors=translate_result.errors,
            backend=self.backend.name,
            debug_mode=debug_mode,
            debug_logs=translate_result.debug_logs,
            client_type="OfflineClient",
        )

        # If translation failed, return early without executing SQL
        if not translate_result.success:
            return result

        # Execute SQL only if translation succeeded
        if result.sql is not None:
            try:
                result.dataframe = self.sql_executor(result.sql)
            except Exception as e:
                error = Error(
                    code="SQL_EXECUTION_ERROR",
                    message=f"Error in sql_executor: {e}",
                    context=f"SQL query: {result.sql}",
                    stack_trace=traceback.format_exc().split("\n"),
                )
                result.errors.append(error)
                # Return early, don't try to generate SLT
                return result

        # Generate SLT format only if we have a dataframe
        if result.dataframe is not None:
            try:
                error_messages = (
                    [e.message for e in result.errors] if result.errors else None
                )
                result.slt = return_slt(
                    featureql,
                    translate_result.full_response,
                    backend=self.backend,
                    dataframe=result.dataframe,
                    errors=error_messages,
                )
            except Exception as e:
                # SLT generation is non-blocking, just skip it
                pass

        return result


class OnlineClient(BaseClient):
    """
    Client for online FeatureQL queries via the FeatureMesh serving API.
    
    Executes FeatureQL queries directly against the FeatureMesh online service,
    which handles both translation and execution.
    
    Attributes:
        access_token: User project token for API authentication
        host: Serving API host URL
        path: Serving API endpoint path
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
    """

    def __init__(
        self,
        access_token: str,
    ) -> None:
        """
        Initialize the online client.
        
        Args:
            access_token: User project token for API authentication
        """
        super().__init__(access_token)
        self.host = get_default("serving.host")
        self.path = get_default("serving.path")
        self.timeout = get_default("serving.timeout")
        self.verify_ssl = get_default("serving.verify_ssl")

    def query(
        self,
        featureql: str,
        debug_mode: bool | None = None,
    ) -> QueryResult:
        """
        Run a FeatureQL query and return complete results.

        Args:
            featureql: FeatureQL query string
            debug_mode: If True, enable debug mode for detailed query information

        Returns:
            QueryResult object containing sql, dataframe, slt, and metadata.
            Errors are captured in the result.errors attribute instead of raising exceptions.
        """
        if debug_mode is None:
            debug_mode = get_default("debug_mode")

        result = QueryResult(
            featureql=featureql,
            debug_mode=debug_mode,
            client_type="OnlineClient",
        )

        # Handle online query
        params_post = {
            "query": featureql,
            "debug_mode": debug_mode,
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": get_user_agent(),
        } | get_auth_header(self.access_token)

        try:
            response_post = requests.post(
                f"{self.host}{self.path}",
                json=params_post,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        except Exception as e:
            error = Error(
                code="NETWORK_ERROR",
                message=f"Contacting FeatureMesh Serving endpoint {self.host}{self.path} failed with error: {e}",
                stack_trace=traceback.format_exc().split("\n"),
            )
            result.errors.append(error)
            return result

        if response_post.status_code != 200:
            error = Error(
                code="HTTP_ERROR",
                message=f"Non-200 HTTP response: {response_post.status_code}",
                context=response_post.text,
            )
            result.errors.append(error)
            return result

        try:
            response = response_post.json()
        except Exception as e:
            error = Error(
                code="JSON_PARSE_ERROR",
                message=f"Failed to parse JSON response: {e}",
            )
            result.errors.append(error)
            return result

        if response is None or response.get("data") is None:
            error = Error(
                code="INVALID_RESPONSE",
                message="Translation failed: no data in response",
                context=response,
            )
            result.errors.append(error)
            return result

        # Parse warnings and errors from API response
        warnings, errors = parse_warnings_and_errors(response)
        result.warnings = warnings
        result.errors = errors

        # If there are errors, return early
        if result.errors:
            return result

        # Extract results
        result.sql = response.get("data", {}).get("query_sql")
        rows = response.get("data", {}).get("rows", [])
        result.dataframe = pd.DataFrame(rows)
        if not result.dataframe.empty:
            result.dataframe.columns = [
                str(col).upper() for col in result.dataframe.columns
            ]

        # OnlineClient doesn't support SLT format
        result.slt = None

        return result
