"""
gspread_datarame - Simple data utilities for spreadsheet operations

A lightweight package providing basic utilities for working with spreadsheet data.
"""

__version__ = "0.1.0"
__author__ = "Data Tools Dev"


def get_version():
    """Return the version of this package."""
    return __version__


def to_dataframe(data):
    """
    Convert data to a simple dictionary format.

    Args:
        data: Input data to convert

    Returns:
        dict: Converted data in dictionary format
    """
    if isinstance(data, dict):
        return data
    return {"data": data}


def from_dataframe(df_dict):
    """
    Convert dictionary format back to data.

    Args:
        df_dict: Dictionary data to convert

    Returns:
        Original data
    """
    if isinstance(df_dict, dict) and "data" in df_dict:
        return df_dict["data"]
    return df_dict


def hello():
    """
    A simple test function.
    """
    return f"gspread_datarame v{__version__} - data utilities package"
