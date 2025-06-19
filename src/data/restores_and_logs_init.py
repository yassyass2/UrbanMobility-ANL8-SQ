import sqlite3

DB_FILE = "data/urban_mobility.db"

create_restore_codes_table_sql = """
CREATE TABLE IF NOT EXISTS restore_codes (
    code TEXT PRIMARY KEY,
    backup_filename TEXT NOT NULL,
    system_admin_id INTEGER NOT NULL,
    used INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

create_logs = """
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    username TEXT,
    activity TEXT NOT NULL,
    additional_info TEXT,
    suspicious INTEGER DEFAULT 0,
    viewed INTEGER DEFAULT 0
);
"""

# Connect to the database and execute the SQL
with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(create_logs)
    conn.commit()