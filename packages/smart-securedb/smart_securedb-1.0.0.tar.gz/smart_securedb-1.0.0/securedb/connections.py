"""
Connection factories for common DBs using SQLAlchemy.
Integrates with smart-encryptor for secure connection string decryption.
"""

import base64
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from typing import Optional
from smart_encryptor import decrypt, get_default_key


def _decrypt_value(encrypted_value: str, key_b64: str = None) -> str:
    """
    Decrypts an encrypted string using AES-256-GCM via smart-encryptor.
    """
    key = base64.urlsafe_b64decode(key_b64) if key_b64 else get_default_key()
    return decrypt(encrypted_value, key)


def sqlite_engine(sqlite_url: str = "sqlite:///:memory:") -> Engine:
    """Simple SQLite engine for tests or local use."""
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})


def mysql_engine(encrypted_conn_str: str, key_b64: Optional[str] = None) -> Engine:
    """
    Create MySQL engine from an AES-encrypted connection string.
    Example decrypted format: mysql+mysqlconnector://user:pass@localhost:3306/dbname
    """
    decrypted_uri = _decrypt_value(encrypted_conn_str, key_b64)
    return create_engine(decrypted_uri, pool_size=10, max_overflow=20, pool_pre_ping=True)


def postgres_engine(encrypted_conn_str: str, key_b64: Optional[str] = None) -> Engine:
    """
    PostgreSQL engine factory (psycopg).
    Example decrypted format: postgresql+psycopg://user:pass@host:5432/db
    """
    decrypted_uri = _decrypt_value(encrypted_conn_str, key_b64)
    return create_engine(decrypted_uri, pool_size=10, max_overflow=20, pool_pre_ping=True)


def oracle_engine(encrypted_conn_str: str, key_b64: Optional[str] = None) -> Engine:
    """
    Oracle engine factory (oracledb).
    Example decrypted format: oracle+oracledb://user:pass@host:1521/?service_name=XE
    """
    decrypted_uri = _decrypt_value(encrypted_conn_str, key_b64)
    return create_engine(decrypted_uri, pool_size=5, max_overflow=5, pool_pre_ping=True)


def mssql_engine(encrypted_conn_str: str, key_b64: Optional[str] = None) -> Engine:
    """
    MSSQL engine factory (pyodbc).
    Example decrypted format: mssql+pyodbc://user:pass@host:1433/db?driver=ODBC+Driver+17+for+SQL+Server
    """
    decrypted_uri = _decrypt_value(encrypted_conn_str, key_b64)
    return create_engine(decrypted_uri, pool_size=5, max_overflow=10, pool_pre_ping=True)
