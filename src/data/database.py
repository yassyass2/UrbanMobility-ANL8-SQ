import sqlite3
import os
import bcrypt
from cryptography.fernet import Fernet
import hashlib
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


DB_FILE = "data/urban_mobility.db"


def initialize_database():
    """Initializes the database and creates necessary tables."""
    if not os.path.exists(DB_FILE):
        print(f"[INFO] Creating database...")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            create_users_table(cursor)
            create_travellers_table(cursor)
            create_scooters_table(cursor)
            create_logs_and_backup_codes(cursor)
            insert_super_admin_user(cursor)
            conn.commit()
            print(f"[INFO] Database initialized.")


def create_users_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            registration_date TEXT,
            username_hash TEXT UNIQUE,
            must_change_password INTEGER DEFAULT 0
        );
    """)


def create_travellers_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS travellers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(30),
            last_name VARCHAR(30),
            birthday DATE,
            gender CHAR,
            street VARCHAR(30),
            house_number INT,
            zip_code VARCHAR(6),
            city VARCHAR(30),
            email VARCHAR(50),
            mobile CHAR(14),
            license_number CHAR(9),
            registration_date DATE
        );
    """)


def create_scooters_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scooters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand VARCHAR(30),
            model VARCHAR(30),
            serial_number VARCHAR(30) UNIQUE,
            top_speed INT,
            battery_capacity INT,
            soc DECIMAL(5,2),
            target_range_soc VARCHAR(20),
            location VARCHAR(50),
            out_of_service INT,
            mileage DECIMAL(7,1),
            last_maintenance DATE,
            in_service DATE
        );
    """)


def create_logs_and_backup_codes(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restore_codes (
    code TEXT PRIMARY KEY,
    backup_filename TEXT NOT NULL,
    system_admin_id INTEGER NOT NULL,
    used INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
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
""")

def insert_super_admin_user(cursor):
    cipher = Fernet(os.getenv("FERNET_KEY").encode())

    username = os.getenv("HARDCODED_SUPADMIN_USERNAME")
    password = os.getenv("HARDCODED_SUPADMIN_PASS")
    first_name = "yass"
    last_name = "yass"
    role = "super_admin"
    registration_date = datetime.now().strftime("%Y-%m-%d")
    must_change_password = 0

    encrypted_username = cipher.encrypt(username.encode()).decode()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    username_hash = hashlib.sha256(username.encode()).hexdigest()

    cursor.execute("""
        INSERT INTO users (
            username,
            password_hash,
            role,
            first_name,
            last_name,
            registration_date,
            username_hash,
            must_change_password
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        encrypted_username,
        password_hash,
        role,
        first_name,
        last_name,
        registration_date,
        username_hash,
        must_change_password
    ))

initialize_database()