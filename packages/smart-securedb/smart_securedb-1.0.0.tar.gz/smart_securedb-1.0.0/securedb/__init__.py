"""securedb - small secure DB helper package

Expose SecureDB and connection helpers.
"""

from .core import SmartSecureDB
from .connections import (
    sqlite_engine,
    mysql_engine,
    postgres_engine,
    oracle_engine,
    mssql_engine,
)
from .utils import is_safe_identifier, ALLOWED_TABLES

__all__ = [
    "SmartSecureDB",
    "sqlite_engine",
    "mysql_engine",
    "postgres_engine",
    "oracle_engine",
    "mssql_engine",
    "is_safe_identifier",
    "ALLOWED_TABLES",
]
