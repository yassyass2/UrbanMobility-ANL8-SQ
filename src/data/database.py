import sqlite3
import os

DB_FILE = "urban_mobility.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def initialize_database():
    """Initializes the database and creates necessary tables."""
    if not os.path.exists(DB_FILE):
        print("[INFO] Creating database...")
        with get_connection() as conn:
            cursor = conn.cursor()
            create_users_table(cursor)
            create_travellers_table(cursor)
            create_scooters_table(cursor)
            create_logs_table(cursor)
            conn.commit()
            print("[INFO] Database initialized.")
    else:
        print("[INFO] Database already exists.")

def create_users_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            registration_date TEXT
        );
    """)

def create_travellers_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS travellers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            birthday TEXT,
            gender TEXT,
            street TEXT,
            house_number TEXT,
            zip_code TEXT,
            city TEXT,
            email TEXT,
            mobile TEXT,
            license_number TEXT,
            registration_date TEXT
        );
    """)

def create_scooters_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scooters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT,
            model TEXT,
            serial_number TEXT UNIQUE,
            top_speed REAL,
            battery_capacity REAL,
            soc INTEGER,
            soc_range_min INTEGER,
            soc_range_max INTEGER,
            latitude REAL,
            longitude REAL,
            out_of_service INTEGER,
            mileage REAL,
            last_maintenance TEXT,
            in_service_date TEXT
        );
    """)

def create_logs_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            username TEXT,
            activity TEXT,
            extra_info TEXT,
            suspicious INTEGER
        );
    """)

