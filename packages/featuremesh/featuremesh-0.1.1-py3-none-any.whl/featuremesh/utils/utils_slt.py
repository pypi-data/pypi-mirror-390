"""
SLT (SQL Logic Test) format utilities for FeatureMesh.

This module provides functions to generate SLT test output from FeatureQL queries,
supporting multiple database backends (DuckDB, Trino, BigQuery, DataFusion).

SLT format is used for testing SQL query correctness by comparing expected vs actual results.
"""

from typing import Any, Optional, List
import textwrap
import json
from datetime import datetime, date
import pandas as pd
import numpy as np
import re

from ..config import Backend


def interpret_response(response: Any) -> Any:
    """
    Interpret the response from a FeatureQL query.

    Args:
        response: The response from the FeatureQL query

    Returns:
        A string indicating the response status: "SUCCESS", "ERROR-USER", or "ERROR-500"
    """
    if response is None or not isinstance(response, dict):
        raise ValueError(f"Response is None or not a dictionary: {response=}")
    
    errors = response.get("errors", [])
    if errors is not None and len(errors) > 0:
        if errors[0].get("code") == "ERROR-500":
            return "ERROR-500"
        return "ERROR-USER"
    return "SUCCESS"


def align_left(text: str) -> str:
    """
    Remove common leading whitespace from all lines in text.
    
    Args:
        text: Multi-line string to align
        
    Returns:
        Text with common leading whitespace removed
    """
    lines = [line for line in text.split("\n") if line.strip()]
    if not lines:
        return text

    # Count leading spaces in non-empty lines
    space_counts = [len(line) - len(line.lstrip()) for line in lines if line.strip()]

    # Remove minimum spaces from each line
    min_spaces = min(space_counts) if space_counts else 0
    return "\n".join(line[min_spaces:] if line.strip() else line for line in lines)


def convert_dates_to_iso(obj: Any) -> Any:
    """
    Recursively convert date/datetime objects to ISO 8601 format strings.
    
    Handles dictionaries, lists, numpy arrays, pandas Timestamps, and datetime objects.
    
    Args:
        obj: Object to convert (can be nested structures)
        
    Returns:
        Object with all date/datetime values converted to ISO format strings
    """
    if isinstance(obj, dict):
        return {key: convert_dates_to_iso(value) for key, value in obj.items()}
    elif isinstance(obj, (list, np.ndarray)):
        return [convert_dates_to_iso(item) for item in obj]
    elif isinstance(obj, (pd.Timestamp, datetime, date)):
        if isinstance(obj, date) and not isinstance(obj, datetime):
            obj = datetime.combine(obj, datetime.min.time())
        return obj.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    # Handle numpy datetime64 types
    elif isinstance(obj, np.datetime64):
        return pd.Timestamp(obj).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return obj


class MyJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for handling pandas and numpy types.
    
    Converts non-standard types (pandas objects, numpy arrays, sets, etc.)
    to JSON-serializable formats.
    """
    
    def default(self, o: Any) -> Any:
        """
        Encode objects to JSON-serializable format.
        
        Args:
            o: Object to encode
            
        Returns:
            JSON-serializable representation of the object
        """
        try:
            if isinstance(o, set):
                return list(o)
            if hasattr(o, "to_dict"):
                return o.to_dict()
            if isinstance(o, (pd.Timestamp, datetime, date)):
                return o.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            if isinstance(o, np.ndarray):
                return o.tolist()
            if isinstance(o, np.integer):
                return int(o)
            return super().default(o)
        except TypeError:
            return str(type(o).__name__)


def sort_str_columns(
    dataframe: pd.DataFrame,
    columns: Optional[List[str]] = None,
    ascending: bool = True,
    reset_index: bool = True,
) -> pd.DataFrame:
    """
    Sort DataFrame columns lexicographically (as strings) while preserving original types.

    Args:
        dataframe: Input DataFrame
        columns: List of column names to sort by. If None, uses all columns
        ascending: Sort order for all columns. True for ascending, False for descending
        reset_index: Whether to reset the index after sorting. If True, creates a new sequential index

    Returns:
        Sorted DataFrame with original column types preserved
    """
    dataframe_sorted = dataframe.copy()

    if columns is None:
        columns = dataframe.columns.tolist()

    original_types = {col: dataframe[col].dtype for col in columns}

    dataframe_sorted[columns] = dataframe_sorted[columns].astype(str)
    dataframe_sorted = dataframe_sorted.sort_values(by=columns, ascending=ascending)

    for col, dtype in original_types.items():
        dataframe_sorted[col] = dataframe_sorted[col].astype(dtype)

    if reset_index:
        dataframe_sorted = dataframe_sorted.reset_index(drop=True)

    return dataframe_sorted


def normalize_sql(sql: str, keep_comments: bool = False) -> str:
    """
    Normalize SQL by removing comments and extra whitespace.
    
    Args:
        sql: SQL query string to normalize
        keep_comments: If False, remove all SQL comments
        
    Returns:
        Normalized SQL string with consistent whitespace
    """
    if not keep_comments:
        # Remove single-line comments
        sql = re.sub(r"--.*?(\r\n|\r|\n|$)", " ", sql)
        # Remove multi-line comments
        sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    # Replace multiple whitespace characters with a single space
    sql = re.sub(r"\s+", " ", sql)
    # Remove leading and trailing whitespace
    sql = sql.strip()
    return sql


def deal_with_quotes(value: str) -> str:
    """
    Clean and normalize string values for SLT output format.
    
    Handles quote escaping, boolean conversion, and whitespace normalization.
    
    Args:
        value: String value to clean
        
    Returns:
        Cleaned and normalized string
    """
    value = (
        value.replace('\\"', "##ESCAPED_DOUBLE_QUOTE##")
        .replace('"', "")
        .replace("##ESCAPED_DOUBLE_QUOTE##", '\\"')
        .replace("'", "")
        .replace(".000Z", "")
        .replace("null", "NULL")
        .replace("True", "true")
        .replace("False", "false")
        .replace("\n", " ")
    )
    return normalize_sql(value, keep_comments=True)


def dict_to_tsv_trino(
    data_dict: dict[str, list[Any]], columns_with_types: list[str]
) -> str:
    """
    Convert dictionary data to TSV format for Trino/BigQuery/DataFusion backends.
    
    Args:
        data_dict: Dictionary mapping column names to value lists
        columns_with_types: List of (column_name, column_type) tuples
        
    Returns:
        Tab-separated values string representation of the data
    """
    result: list[str] = []

    def is_sequence_of_dicts(value: Any) -> bool:
        if isinstance(value, list):
            return value and all(isinstance(x, dict) for x in value)
        elif isinstance(value, np.ndarray):
            if value.size == 0:
                return False
            return all(isinstance(x, dict) for x in value.flatten())
        return False

    # Create case-insensitive column mapping
    column_map = {col.lower(): col for col in data_dict.keys()}

    num_rows = len(next(iter(data_dict.values())))

    for i in range(num_rows):
        row: list[str] = []
        for column_name, column_type in columns_with_types:
            # Try to find the column case-insensitively
            actual_column = column_map.get(column_name.lower())
            if actual_column is None:
                raise ValueError(
                    f"Column {column_name} not found in {data_dict.keys()=}"
                )

            value = data_dict[actual_column][i]
            if isinstance(value, bool):
                row.append("true" if value else "false")
            elif isinstance(value, str) and column_type == "JSON":
                row.append(str(value).replace("\n", " "))
            elif value is None:
                row.append("NULL")
            elif isinstance(value, (int, float)) and str(value) == "inf":
                row.append("Infinity")
            elif isinstance(value, (int, float)) and str(value) == "nan":
                row.append("NaN")
            elif isinstance(value, (int, float)):
                row.append(str(value))
            elif isinstance(value, (pd.Timestamp, datetime, date)):
                formatted_date = value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-7]
                row.append(formatted_date)
            elif is_sequence_of_dicts(value) or isinstance(value, (list, np.ndarray)):
                json_value = json.dumps(
                    value.tolist() if isinstance(value, np.ndarray) else value,
                    ensure_ascii=False,
                    cls=MyJSONEncoder,
                )
                non_escaped_value = deal_with_quotes(json_value)
                row.append(non_escaped_value)
            else:
                escaped_value = deal_with_quotes(str(value))
                row.append(escaped_value)

        result.append("\t".join(row))

    return "\n".join(result)


def dict_to_tsv_duckdb(data: pd.DataFrame, columns_with_types: list[str]) -> str:
    """
    Convert DataFrame to TSV format for DuckDB backend.
    
    Args:
        data: Pandas DataFrame containing the query results
        columns_with_types: List of (column_name, column_type) tuples
        
    Returns:
        Tab-separated values string representation of the data
    """
    result: list[str] = []
    num_rows = len(data)
    get_value = lambda col, i: data[col].iloc[i]
    for i in range(num_rows):
        row: list[str] = []
        for column_name, column_type in columns_with_types:
            value = get_value(column_name, i)
            if isinstance(value, bool):
                row.append("true" if value else "false")
            elif isinstance(value, str) and column_type == "JSON":
                row.append(str(value).replace("\n", " "))
            elif value is None:
                row.append("NULL")
            elif isinstance(value, (int, float)) and str(value) == "inf":
                row.append("Infinity")
            elif isinstance(value, (int, float)) and str(value) == "nan":
                row.append("NaN")
            elif isinstance(value, (int, float)):
                row.append(str(value))
            elif isinstance(value, (datetime, date)):
                formatted_date = value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-7]
                row.append(formatted_date)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                structured_data = []
                for item in value:
                    struct_dict = {}
                    for field_name, field_value in item.items():
                        if isinstance(field_value, datetime):
                            struct_dict[field_name] = field_value.strftime(
                                "%Y-%m-%dT%H:%M:%S"
                            )
                        else:
                            struct_dict[field_name] = field_value
                    structured_data.append(struct_dict)
                json_value = json.dumps(structured_data, ensure_ascii=False)
                row.append(deal_with_quotes(json_value))
            else:
                escaped_value = deal_with_quotes(str(value))
                row.append(escaped_value)
        result.append("\t".join(row))
    return "\n".join(result)


dict_to_tsv_bigquery = dict_to_tsv_trino


def return_slt(
    featureql: str,
    response: Any,
    backend: Backend = Backend.TRINO,
    dataframe: pd.DataFrame = None,
    errors: list[str] = None,
) -> str:
    """
    Generate SLT (SQL Test) output from a FeatureQL query response.

    Args:
        featureql: The original FeatureQL query
        response: The response from the FeatureQL query
        backend: The database backend used (Backend.TRINO, Backend.DUCKDB, etc.)
        dataframe: The dataframe that contains the results of the query
        errors: The list of error messages that were returned by the query
    Returns:
        A string containing the SLT test output
    """
    if backend not in [
        Backend.TRINO,
        Backend.DUCKDB,
        Backend.BIGQUERY,
        Backend.DATAFUSION,
    ]:
        raise ValueError(f"Backend {backend} not supported")

    featureql = textwrap.dedent(featureql).strip()

    if interpret_response(response) in ["ERROR-USER"]:
        code = response["errors"][0]["code"]
        message = response["errors"][0]["message"]
        return f"query error\n{featureql}\n----\nERROR {code} {message}"
    if interpret_response(response) in ["ERROR-500"]:
        return f"query error\n{featureql}\n----\nERROR ERROR-500 Uncaught exception"
    if interpret_response(response) != "SUCCESS":
        return f"query error\n{featureql}\n----\nERROR UNKNOWN"

    if errors is not None:
        return f"query error\n{featureql}\n----\nERROR {'\n'.join(errors)}"
    
    if "data" not in response:
        return f"query error\n{featureql}\n----\nERROR The 'data' entry was not found in the response"
    
    if "query_sql" not in response["data"] and "warnings" in response["data"]:
        return f"query error\n{featureql}\n----\nEMPTY-WITH-WARNINGS No query_sql was returned but some warnings: {response['data']['warnings']}"

    if "query_sql" not in response["data"]:
        return f"query error\n{featureql}\n----\nERROR The 'query_sql' entry was not found in the response['data']"

    equivalent_types = {
        "BIGINT": "I",
        "INTEGER": "I",
        "DOUBLE": "D",
        "VARCHAR": "V",
        "BOOLEAN": "B",
        "TIMESTAMP": "T",
        "JSON": "J",
        "ARRAY": "A",
        "ROW": "R",
        "ARRAY_OF_ROWS": "Q",
    }

    def get_equivalent_type_featureql(datatype):
        if datatype.startswith("ARRAY(ROW("):
            return "Q"
        if datatype.startswith("ARRAY("):
            return "A"
        if datatype.startswith("ROW("):
            return "R"
        return equivalent_types.get(datatype, f"?{datatype}")

    # def get_equivalent_type_duckdb(datatype):
    #     datatype = str(datatype).upper()
    #     if datatype.startswith("ROW(") and datatype.endswith("[]"):
    #         return "Q"
    #     if datatype.endswith("[]"):
    #         return "A"
    #     if datatype.startswith("ROW("):
    #         return "R"
    #     if datatype.startswith("DECIMAL"):
    #         return "D"
    #     return equivalent_types.get(datatype, f"?{datatype}")

    results = None
    if dataframe is not None:
        results = dataframe
        if backend in [Backend.TRINO, Backend.BIGQUERY, Backend.DATAFUSION]:
            results = sort_str_columns(results)

    if "query_outputs" in response["data"]:
        columns_with_types = response["data"]["query_outputs"]
        get_equivalent_type = get_equivalent_type_featureql
    else:
        return f"query error\n{featureql}\n----\nERROR The definition of columns in query_outputs was not found"

    columns_with_types_slt = [
        (name, get_equivalent_type(datatype)) for name, datatype in columns_with_types
    ]

    results_tsv = None
    if backend == Backend.DUCKDB:
        results_tsv = dict_to_tsv_duckdb(results, columns_with_types)
    elif backend in [Backend.TRINO, Backend.BIGQUERY, Backend.DATAFUSION]:
        results_tsv = dict_to_tsv_trino(results.to_dict(), columns_with_types)
    else:
        raise ValueError(f"Backend {backend} not supported")

    outputs_str = ",".join(
        [
            f"{output[0] if not output[0].startswith('UNNAMED') else '?'}:{output[1]}"
            for output in columns_with_types_slt
        ]
    )
    output = f"query {outputs_str}\n{align_left(featureql)}\n----\n{results_tsv}"
    return output
