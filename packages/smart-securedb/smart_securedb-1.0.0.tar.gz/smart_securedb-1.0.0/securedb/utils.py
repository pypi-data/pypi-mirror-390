"""Utility functions for safe identifier validation and small helpers."""

import re
from typing import Dict

# Simple allow-list mapping: public keys -> real table names in DB.
# Populate/extend this mapping in your app to avoid exposing raw table names to users.
ALLOWED_TABLES: Dict[str, str] = {
    "users": "app_users",
    "events": "app_events",
    "items": "app_items",
}

_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_]{1,64}$")

def is_safe_identifier(name: str) -> bool:
    """
    Validate that an identifier (table/column) is safe.
    Accept only letters, digits and underscore, length <= 64.
    """
    if not isinstance(name, str):
        return False
    return bool(_IDENTIFIER_RE.fullmatch(name))

def resolve_table_key(key: str) -> str:
    """
    Resolve a user-supplied key to an allowed table name.
    Raises ValueError if not allowed.
    """
    if key not in ALLOWED_TABLES:
        raise ValueError("disallowed table key")
    return ALLOWED_TABLES[key]
