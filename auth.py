import sqlite3
import hashlib

# ユーザー専用のDBファイル
AUTH_DB_FILE = "user.db"

# ユーザーDB側の初期化
def init_auth_db():
    with sqlite3.connect(AUTH_DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_user(username, password):
    try:
        with sqlite3.connect(AUTH_DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, make_hash(password)))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    with sqlite3.connect(AUTH_DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, make_hash(password)))
        user = cursor.fetchone()
        return user[0] if user else None