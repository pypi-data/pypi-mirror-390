"""Basic tests for SecureDB using in-memory sqlite and smart-encryptor mock."""

import pytest
from sqlalchemy import text
from securedb.connections import sqlite_engine, mysql_engine
from securedb.core import SmartSecureDB
from securedb.utils import ALLOWED_TABLES
from smart_encryptor import encrypt, generate_key

# Update allowed mapping for test tables
ALLOWED_TABLES.update({"test_users": "test_users"})


@pytest.fixture(scope="module")
def db_engine():
    """Creates in-memory sqlite DB for testing."""
    engine = sqlite_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT
            )
        """))
    return engine


def test_insert_and_fetch(db_engine):
    s = SmartSecureDB(db_engine)
    s.insert_named("test_users", {"username": "alice", "email": "alice@example.com"})
    s.insert_named("test_users", {"username": "bob", "email": "bob@example.com"})

    rows = s.run_raw_read_with_table("test_users", limit=10)
    assert len(rows) == 2
    assert rows[0]["username"] == "alice"


def test_fetch_by_id(db_engine):
    s = SmartSecureDB(db_engine)
    rows = s.fetch_by_id("test_users", 1)
    assert len(rows) == 1
    assert rows[0]["id"] == 1


def test_invalid_identifier_rejected(db_engine):
    s = SmartSecureDB(db_engine)
    with pytest.raises(ValueError):
        s.insert_named("test_users", {"username;DROP": "x"})  # invalid column name


def test_encrypted_connection_string_decryption(monkeypatch):
    """
    Tests MySQL engine creation from an encrypted connection string.
    The encryption/decryption process should return a valid DB URI.
    """
    key = generate_key()
    uri = "mysql+mysqlconnector://user:pass@localhost:3306/testdb"
    encrypted_uri = encrypt(uri, key)

    # Patch get_default_key so that our mock key is used
    monkeypatch.setattr("securedb.connections.get_default_key", lambda: key)

    # Decrypt and verify
    engine = mysql_engine(encrypted_uri)
    assert "mysqlconnector" in str(engine.url)
