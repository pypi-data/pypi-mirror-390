"""
nitro-pandas: A high-performance pandas-like DataFrame library powered by Polars.

This package provides a pandas-compatible API while using Polars as the backend
for optimized data operations. It combines the familiar pandas syntax with
Polars' performance benefits.

Key features:
- Pandas-like API for familiar usage
- Polars backend for high-performance operations
- Support for lazy evaluation with LazyFrame
- Automatic fallback to pandas for unimplemented methods
- Comprehensive I/O support (CSV, Parquet, JSON, Excel)

Main classes:
- DataFrame: Pandas-like DataFrame wrapper around Polars
- LazyFrame: Pandas-like LazyFrame wrapper for lazy evaluation

Example:
    >>> import nitro_pandas as npd
    >>> df = npd.read_csv("data.csv")
    >>> result = df.loc[df['id'] > 2]
    >>> df.groupby('category')['value'].mean()
"""

from .io import *
from .dataframe import DataFrame
from .lazyframe import LazyFrame

# Export useful Polars expressions for user convenience
from polars import (
    col, lit, when, all, any, count, min, max, mean, sum, std, var,
    first, last, concat_str
)

__all__ = [
    'DataFrame',
    'LazyFrame',
    'read_csv',
    'read_csv_lazy',
    'read_parquet',
    'read_parquet_lazy',
    'read_excel',
    'read_excel_lazy',
    'read_json',
    'read_json_lazy',
    # Polars expressions
    'col', 'lit', 'when', 'all', 'any', 'count', 'min', 'max', 'mean',
    'sum', 'std', 'var', 'first', 'last', 'concat_str',
]
