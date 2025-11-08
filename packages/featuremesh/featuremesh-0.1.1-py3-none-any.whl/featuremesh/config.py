"""
Configuration management for FeatureMesh client.

This module provides configuration settings, defaults, and utility functions for:
- API endpoints and connection settings
- Backend configuration (DuckDB, Trino, BigQuery, DataFusion, Online)
- Access token and authentication management
- Debug and display preferences

Configuration can be customized using set_default() and get_default() functions.
"""

import sys
import platform
import hashlib

from enum import Enum
import importlib.metadata

try:
    __version__ = importlib.metadata.version("featuremesh")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "set_default",
    "get_default",
    "get_all_defaults",
    "get_user_agent",
    "get_kernel_id",
    "get_auth_header",
    "Backend",
    "OFFLINE_BACKENDS",
    "__version__",
]

# THESE PARAMETERS CAN BE OVERWRITTEN BY THE USER USING set_default(param_name, param_value)
_DEFAULTS = {
    # Parameters for the environment
    "registry.host": "https://api.featuremesh.com",
    "registry.path": "/v1/featureql",
    "registry.timeout": 30,
    "registry.verify_ssl": True,
    # Parameters for the serving API
    "serving.host": "http://host.docker.internal:10090",
    "serving.path": "/v1/featureql",
    "serving.timeout": 30,
    "serving.verify_ssl": True,
    # For access management
    "access.host": "https://api.featuremesh.com",
    "access.path": "/v1/access",
    "access.timeout": 30,
    "access.verify_ssl": True,
    # Parameters for the client
    "identity_token": None,
    "access_token": None,
    "service_account_token": None,
    "debug_mode": False,
    # Parameters for the magic commands
    "client": None,
    "show_sql": False,
    "hide_dataframe": False,
    "show_slt": False,
    "hook": None,
}


def set_default(param_name: str, param_value) -> None:
    """
    Set a default parameter value that will be used by FeatureMesh clients and magic commands.

    Args:
        param_name: Name of the parameter to set
        param_value: Value to set for the parameter

    Raises:
        ValueError: If the parameter name is not recognized
    """
    if param_name not in _DEFAULTS:
        valid_params = ", ".join(_DEFAULTS.keys())
        raise ValueError(
            f"Unknown parameter '{param_name}'. Valid parameters: {valid_params}."
        )

    _DEFAULTS[param_name] = param_value


def get_default(param_name: str):
    """
    Get a default parameter value.

    Args:
        param_name: Name of the parameter to get

    Returns:
        The current default value for the parameter

    Raises:
        ValueError: If the parameter name is not recognized
    """
    if param_name not in _DEFAULTS:
        valid_params = ", ".join(_DEFAULTS.keys())
        raise ValueError(
            f"Unknown parameter '{param_name}'. Valid parameters: {valid_params}."
        )

    return _DEFAULTS[param_name]


def get_all_defaults() -> dict:
    """
    Get all current default parameter values.

    Returns:
        Dictionary of all default parameter values
    """
    return _DEFAULTS.copy()


def get_user_agent() -> str:
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    # Get OS name
    system = platform.system()
    if system == "Darwin":
        system = "macOS"

    # Check if running in Jupyter and get JupyterLab version
    jupyter_info = ""
    try:
        from IPython import get_ipython

        ipython = get_ipython()
        if ipython is not None and "IPKernelApp" in ipython.config:
            # Try to get JupyterLab version
            try:
                import jupyterlab  # type: ignore

                jupyter_info = f" JupyterLab/{jupyterlab.__version__}"
            except ImportError:
                # Fall back to jupyter_core or just mark as Jupyter
                try:
                    import jupyter_core  # type: ignore

                    jupyter_info = f" Jupyter/{jupyter_core.__version__}"
                except ImportError:
                    jupyter_info = " Jupyter"
    except (ImportError, AttributeError):
        pass

    return f"featuremesh-pip/{__version__} Python/{python_version} ({system}){jupyter_info}"


def get_kernel_id() -> str:
    """
    Get a hashed Jupyter kernel ID for temporary access tokens.
    
    Returns:
        Hashed kernel ID (12 characters)
        
    Raises:
        ValueError: If kernel ID cannot be determined
    """
    # Try to get Jupyter kernel ID
    try:
        import ipykernel  # type: ignore

        kernel_id = ipykernel.get_connection_file().split("-", 1)[1].split(".")[0]
        return hashlib.sha256(kernel_id.encode()).hexdigest()[:12]
    except Exception as e:
        raise ValueError(
            f"The access token cannot be created because a temporary jupyter kernel ID cannot be determined. Please set the access token. Error: {e}"
        )


def get_auth_header(token: str | None = None) -> str:
    """
    Generate Authorization Bearer header value.
    
    If no access token is provided, creates a temporary guest token using the kernel ID.
    
    Args:
        access_token: Optional user project token. If None, uses default or creates guest token.
        
    Returns:
        Authorization Bearer string (e.g., "Bearer token_value")
    """
    if token is not None:
        return {"Authorization": f"Bearer {token}"}
    if get_default("access_token") is not None:
        return {"Authorization": f"Bearer {get_default("access_token")}"}
    return {"X-Auth-Token": f"PIPGUEST_TOKEN_{get_kernel_id()}"}


# THESE PARAMETERS CANNOT BE CHANGED BY THE USER


class Backend(Enum):
    DUCKDB = "DUCKDB"
    TRINO = "TRINO"
    BIGQUERY = "BIGQUERY"
    DATAFUSION = "DATAFUSION"
    ONLINE = "ONLINE"


# Supported backends for offline client
OFFLINE_BACKENDS = [Backend.DUCKDB, Backend.TRINO, Backend.BIGQUERY, Backend.DATAFUSION]
