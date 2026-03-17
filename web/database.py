import sqlite3
import os
import psycopg2
from urllib.parse import urlparse


class SQLiteCursorAdapter:
    """Adapts SQLite cursor to accept PostgreSQL-style %s placeholders."""

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        normalized_query = query.replace("%s", "?")
        if params is None:
            return self._cursor.execute(normalized_query)
        return self._cursor.execute(normalized_query, params)

    def executemany(self, query, params_seq):
        normalized_query = query.replace("%s", "?")
        return self._cursor.executemany(normalized_query, params_seq)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class SQLiteConnectionAdapter:
    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return SQLiteCursorAdapter(self._connection.cursor())

    def commit(self):
        return self._connection.commit()

    def rollback(self):
        return self._connection.rollback()

    def close(self):
        return self._connection.close()

    def __getattr__(self, name):
        return getattr(self._connection, name)


def _is_sqlite_connection(conn):
    return isinstance(conn, SQLiteConnectionAdapter) or isinstance(conn, sqlite3.Connection)

def get_connection():
    db_url = os.environ.get("DATABASE_URL")

    if db_url:
        return psycopg2.connect(db_url, sslmode="require")
        
    else:
        # fallback for local development
        conn = sqlite3.connect("database.db")
        conn.execute("PRAGMA foreign_keys = ON")
        return SQLiteConnectionAdapter(conn)
#DB_PATH = os.path.join(os.getcwd(), "database.db")

def safe_print(message):
    """Print function that handles Unicode characters safely on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Replace problematic Unicode characters with ASCII alternatives
        safe_message = message.encode('ascii', 'replace').decode('ascii')
        print(safe_message)
    except Exception as e:
        print(f"Print error: {str(e)}")

def init_db():
    #conn = sqlite3.connect(DB_PATH)
    conn = get_connection()
    c = conn.cursor()
    using_sqlite = _is_sqlite_connection(conn)

    id_col = "INTEGER PRIMARY KEY AUTOINCREMENT" if using_sqlite else "SERIAL PRIMARY KEY"
    image_col = "BLOB" if using_sqlite else "BYTEA"

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id ''' + id_col + ''',
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        phone VARCHAR(15),
        city VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS maps (
        id ''' + id_col + ''',
        user_id INTEGER NOT NULL,
        image ''' + image_col + ''' NULL,
        filename VARCHAR(255),
        file_type VARCHAR(10),
        report TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        payment_status VARCHAR(20) DEFAULT 'pending',
        analysis_status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id ''' + id_col + ''',
        user_id INTEGER NOT NULL,
        map_id INTEGER NOT NULL,
        amount DECIMAL(10,2) DEFAULT 50.00,
        status VARCHAR(20) DEFAULT 'pending',
        transaction_id VARCHAR(100),
        payment_method VARCHAR(50) DEFAULT 'qr_code',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (map_id) REFERENCES maps (id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id ''' + id_col + ''',
            user_id INTEGER NOT NULL,
            map_id INTEGER NOT NULL,
            rule_name TEXT NOT NULL,
            was_correct BOOLEAN NOT NULL,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (map_id) REFERENCES maps(id)
        )''')
    conn.commit()
    conn.close()

def create_user(username, email, password_hash, full_name, phone, city):
    #conn = sqlite3.connect(DB_PATH)
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO users (username, email, password_hash, full_name, phone, city)
                     VALUES (%s, %s, %s, %s, %s, %s)
                     RETURNING id''',
                  (username, email, password_hash, full_name, phone, city))
        user_id = c.fetchone()[0]
        conn.commit()
        return user_id
    except Exception as e:
        # Handle duplicate username/email cleanly for both SQLite and PostgreSQL.
        if isinstance(e, sqlite3.IntegrityError) or isinstance(e, psycopg2.IntegrityError):
            conn.rollback()
            return None
        raise
    finally:
        conn.close()

from werkzeug.security import check_password_hash

def verify_user(username_or_email, password):
    # conn = sqlite3.connect(DB_PATH)
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, password_hash, full_name, city FROM users WHERE username = %s OR email = %s',
              (username_or_email, username_or_email))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        return {'id': user[0], 'full_name': user[2], 'city': user[3]}
    return None

def insert_map(user_id, image_data, filename, file_type):
    # conn = sqlite3.connect(DB_PATH)
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO maps (user_id, image, filename, file_type, report, status, payment_status, analysis_status)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                 RETURNING id''',
              (user_id, image_data, filename, file_type, 'Analysis pending...', 'pending', 'pending', 'pending'))
    map_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return map_id

def update_map_analysis(map_id, report, status):
    try:
        # conn = sqlite3.connect(DB_PATH)
        conn = get_connection()
        c = conn.cursor()
        c.execute('''UPDATE maps SET report = %s, status = %s, analysis_status = 'completed' WHERE id = %s''',
                  (report, status, map_id))
        conn.commit()
        rows_affected = c.rowcount
        conn.close()
        
        if rows_affected == 0:
            safe_print(f"Warning: No rows updated for map_id: {map_id}")
        else:
            safe_print(f"Successfully updated map_id: {map_id} with status: {status}")
            
    except Exception as e:
        safe_print(f"Database update error for map_id {map_id}: {str(e)}")
        try:
            conn.close()
        except:
            pass
        raise e

def get_user_maps(user_id):
    # conn = sqlite3.connect(DB_PATH)
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT id, status, payment_status, analysis_status, created_at, report, filename
                 FROM maps WHERE user_id = %s ORDER BY created_at DESC''',
              (user_id,))
    maps = c.fetchall()
    conn.close()
    return maps
