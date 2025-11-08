"""
Client utility functions for FeatureMesh.

This module provides helper functions for pretty-printing and formatting
various data structures used in the FeatureMesh client.
"""

from typing import Any
import json
import textwrap


def pprint(stuff: Any, as_string: bool = False) -> str | None:
    """
    Pretty-print data structures or strings.
    
    Args:
        stuff: Data to print (string or JSON-serializable object)
        as_string: If True, return the formatted string instead of printing
    
    Returns:
        The formatted string if as_string=True, None otherwise
    """
    string = (
        stuff if isinstance(stuff, str) else json.dumps(stuff, sort_keys=True, indent=4)
    )
    if as_string:
        return string
    else:
        print(string)
    return None


def nprint(stuff: Any, num_lines: bool = True, as_string: bool = False) -> None | str:
    """
    Print text with optional line numbers.
    
    Args:
        stuff: Text content to print
        num_lines: If True, prepend line numbers to each line
        as_string: If True, return the formatted string instead of printing
    
    Returns:
        The formatted string if as_string=True, None otherwise
    """
    try:
        formatted_stuff = "\n".join(
            [
                ":  ".join([f"{nline+1:_>6}", line]) if num_lines else line
                for nline, line in enumerate(textwrap.dedent(stuff).strip().split("\n"))
            ]
        )
    except Exception:
        formatted_stuff = f"(NON-FORMATED)\n\n{stuff}"

    if as_string:
        return formatted_stuff

    print(f"\n{formatted_stuff}\n")
    return None
