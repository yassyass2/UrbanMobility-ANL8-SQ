import sqlite3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from visual.text_colors import TextColors

t = TextColors

DB_FILE = "urban_mobility.db"


def initialize_database():
    """Initializes the database and creates necessary tables."""
    if not os.path.exists(DB_FILE):
        print(f"{t.blue}[INFO] Creating database...{t.end}")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            create_users_table(cursor)
            create_travellers_table(cursor)
            create_scooters_table(cursor)
            conn.commit()
            print(f"{t.green}[INFO] Database initialized.{t.end}")
    else:
        print(f"{t.red}[INFO] Database already exists.{t.end}")


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
            last_maintenance DATE
        );
    """)

