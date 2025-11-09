# smart-securedb 🔐

A secure Python database connector with SQLAlchemy — designed to prevent SQL injection and use **encrypted connection strings** via [`smart-encryptor`](https://bitbucket.org/yourusername/smart-encryptor).

---

## 🚀 Installation

```bash
pip install smart-securedb smart-encryptor
```

---

## 🔧 Usage

### 1. Encrypt your connection string first
```python
from smart_encryptor import SmartEncryptor, generate_key

# Generate custom key (recommended)
key = generate_key("dbkey.txt")

encryptor = SmartEncryptor(key)
encrypted_conn = encryptor.encrypt("mysql+pymysql://root:MyPass@localhost/mydb")
print("Encrypted:", encrypted_conn)
```

---

### 2. Use encrypted connection in SecureDB

```python
from securedb import SecureDB

# Load your key from file or environment variable
with open("dbkey.txt") as f:
    key = f.read().strip()

db = SecureDB(encrypted_conn_str="<your-encrypted-string>", encryption_key=key)
result = db.execute_query("SELECT * FROM users WHERE id=:id", {"id": 1})

print(result)
db.close()
```

---

### ✅ Features
- Secure encryption for credentials.
- Full protection from SQL Injection (parameterized queries).
- Works with MySQL, PostgreSQL, Oracle, and MSSQL.
- Integrates seamlessly with **smart-encryptor**.

---

### ⚙️ Supported drivers
- `mysql+pymysql`
- `postgresql+psycopg2`
- `oracle+cx_oracle`
- `mssql+pyodbc`
