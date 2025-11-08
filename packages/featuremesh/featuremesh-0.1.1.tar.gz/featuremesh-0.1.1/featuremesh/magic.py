"""
IPython/Jupyter magic commands for FeatureMesh.

This module provides the %%featureql cell magic for executing FeatureQL queries
directly in Jupyter notebooks with various display and debugging options.

Usage in Jupyter:
    %load_ext featuremesh
    
    %%featureql --show-sql
    SELECT * FROM my_table

Available options:
    --client CLIENT      Use CLIENT from shell namespace
    --debug             Enable debug mode
    --show-sql          Print the translated SQL query
    --hide-dataframe    Hide dataframe output display
    --show-slt          Print the SLT output
    --hook VARIABLE     Store complete results dict in VARIABLE
"""

import shlex
import argparse
import traceback
import json
from dataclasses import asdict
from IPython import get_ipython
from .client import BaseClient
from .config import get_default

__all__ = ["load_ipython_extension", "featureql"]


def parse_parameters(line: str) -> dict:
    """
    Parse parameters from the magic command line using argparse.

    Args:
        line: The line containing magic command parameters

    Returns:
        Dictionary of parsed parameters

    Examples:
        %%featureql --show-sql --debug --hook results --client my_client
        %%featureql --hide-dataframe --show-slt
    """

    # Check for help request first
    if line.strip():
        args = shlex.split(line)
        if "--help" in args or "-h" in args:
            help_text = """
Usage: %%featureql [options]

Options:
--client CLIENT   Use CLIENT from shell namespace
--debug           Enable debug mode
--show-sql        Print the translated SQL query
--hide-dataframe  Hide dataframe output display
--show-slt        Print the SLT output  
--hook VARIABLE   Store complete results dict in VARIABLE

Examples:
%%featureql --client my_client --show-sql
%%featureql --hide-dataframe --show-slt --hook results
            """
            print(help_text)
            return None  # Signal to skip execution

    parser = argparse.ArgumentParser(prog="%%featureql", add_help=False)
    parser.add_argument(
        "--client",
        type=str,
        default=None,
        help="Client variable name from shell namespace",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=get_default("debug_mode"),
        help="Enable debug mode",
    )
    parser.add_argument(
        "--show-sql",
        action="store_true",
        default=get_default("show_sql"),
        help="Print the translated SQL",
    )
    parser.add_argument(
        "--hide-dataframe",
        action="store_true",
        default=False,
        help="Hide dataframe output display",
    )
    parser.add_argument(
        "--show-slt", action="store_true", default=False, help="Print the SLT output"
    )
    parser.add_argument(
        "--hook",
        type=str,
        default=None,
        help="Variable name to store complete results dict",
    )

    if not line.strip():
        # Return defaults when no arguments
        return {
            "show_sql": get_default("show_sql"),
            "show_slt": False,
            "hide_dataframe": False,
            "debug": get_default("debug_mode"),
            "hook": None,
            "client": None,
        }

    try:
        args = parser.parse_args(shlex.split(line))
        return {
            "show_sql": args.show_sql,
            "show_slt": args.show_slt,
            "hide_dataframe": args.hide_dataframe,
            "debug": args.debug,
            "hook": args.hook,
            "client": args.client,
        }
    except SystemExit:
        # argparse calls sys.exit on error, catch it
        raise ValueError("Invalid arguments. Use --help for usage information")


def featureql(line: str, cell: str):
    """
    Execute FeatureQL queries in Jupyter notebook cells.
    
    This is the main function for the %%featureql cell magic command.
    
    Args:
        line: Magic command line containing options
        cell: Cell content containing the FeatureQL query
        
    Returns:
        DataFrame for display, or None if hidden
    """
    params = parse_parameters(line)

    if params is None:  # Help was shown
        return None

    # Get client from parameters or use default
    client_str = params.get("client")
    if client_str:
        shell = get_ipython()
        client = shell.user_ns.get(client_str)
        if not isinstance(client, BaseClient):
            raise ValueError(f"'{client_str}' is not a FeatureQL client")
    else:
        client = get_default("client")
        if client is None:
            raise ValueError(
                "No default client set. Use set_default('client', client) or specify --client parameter"
            )

    results = None

    shell = get_ipython()

    # Get the basic results using the client's query method
    results = client.query(cell, debug_mode=params["debug"])

    # Display errors and warnings using the display utility
    from .display import display_errors, display_warnings

    display_errors(results.errors)
    display_warnings(results.warnings)

    # Handle display logic
    if params["show_sql"] and results.sql:
        print(results.sql)

    if params["show_slt"] and results.slt:
        print(results.slt)

    if params["debug"] and results.debug_logs:
        step_index = results.debug_logs.get("default", {}).get("step_index", {})
        for reference, steps in step_index.items():
            print(f"\nDebugging reference: {reference}")
            for step in steps:
                content = results.debug_logs.get(reference, {}).get(step, "")
                print(f"\n- {step}: {len(json.dumps(content))} characters")
            print("\n")

        if not params["hook"]:
            print(
                f"INFO: Use option --hook to store the debugging information in a variable"
            )

    # Store in shell namespace if hook specified
    if params["hook"]:
        # Convert dataclass to dict using asdict()
        shell.user_ns[params["hook"]] = asdict(results)
        print(
            f"INFO: The output has been stored as a dict in variable '{params['hook']}'"
        )

    # Return dataframe for display unless hidden
    if params["hide_dataframe"]:
        return None
    else:
        return results.dataframe


def load_ipython_extension(ipython) -> None:
    """
    Load the FeatureMesh IPython extension.
    
    Called automatically when %load_ext featuremesh is executed.
    
    Args:
        ipython: IPython InteractiveShell instance
    """
    ipython.register_magic_function(featureql, "cell")
