"""High-level secure DB API built on SQLAlchemy Core (text + bind params)."""

from typing import Any, Dict, Iterable, List, Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine, Result
from .utils import is_safe_identifier, resolve_table_key

class SmartSecureDB:
    """
    A small wrapper providing safe common operations.
    Always uses parameterized queries for values. Identifier usage must be via allow-list.
    """

    def __init__(self, engine: Engine):
        self.engine = engine

    def fetch_all(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a read-only query with named parameters and return a list of mapping dicts.
        Example: fetch_all("SELECT * FROM users WHERE id = :id", {"id": 1})
        """
        params = params or {}
        stmt = text(sql)
        with self.engine.connect() as conn:
            result: Result = conn.execute(stmt, params)
            return result.mappings().all()

    def execute_write(self, sql: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Execute a write operation inside a transaction.
        """
        params = params or {}
        stmt = text(sql)
        with self.engine.begin() as conn:
            conn.execute(stmt, params)

    def fetch_by_id(self, table_key: str, id_value: Any, id_column: str = "id") -> List[Dict[str, Any]]:
        """
        Safe fetch by id using allow-listed table keys. This prevents arbitrary table insertion.
        table_key is resolved by ALLOWED_TABLES in utils.
        """
        table = resolve_table_key(table_key)
        if not is_safe_identifier(id_column):
            raise ValueError("invalid id column name")
        sql = text(f"SELECT * FROM {table} WHERE {id_column} = :idval")
        with self.engine.connect() as conn:
            result = conn.execute(sql, {"idval": id_value})
            return result.mappings().all()

    def insert_named(self, table_key: str, values: Dict[str, Any]) -> None:
        """
        Insert a row using a mapping of column -> value.
        Column names are validated to be safe identifiers.
        This constructs a parameterized INSERT.
        """
        table = resolve_table_key(table_key)
        if not values:
            raise ValueError("empty values not allowed")

        # validate columns
        columns = []
        for col in values.keys():
            if not is_safe_identifier(col):
                raise ValueError(f"unsafe column name: {col}")
            columns.append(col)

        cols_sql = ", ".join(columns)
        params_sql = ", ".join(f":{c}" for c in columns)
        sql = text(f"INSERT INTO {table} ({cols_sql}) VALUES ({params_sql})")
        with self.engine.begin() as conn:
            conn.execute(sql, values)

    def run_raw_read_with_table(self, table_key: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Example of a safe raw read when only the table name is user-controlled via the allow-list.
        """
        table = resolve_table_key(table_key)
        sql = text(f"SELECT * FROM {table} LIMIT :lim")
        with self.engine.connect() as conn:
            result = conn.execute(sql, {"lim": limit})
            return result.mappings().all()
