import re
import datetime
import sqlite3
import hashlib
from ui.menu_utils import *
from cryptography.fernet import Fernet

USERNAME_REGEX = re.compile(r"^[a-z_][a-z0-9_'.]{7,9}$", re.IGNORECASE)


def is_valid_username(username):
    return bool(USERNAME_REGEX.fullmatch(username))


def is_valid_name(name):
    return (
        1 <= len(name) <= 30 and
        re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'.\- ]+", name)
    )


def is_valid_password(password):
    return (
    12 <= len(password) <= 30 and
    re.search(r"[a-z]", password) and
    re.search(r"[A-Z]", password) and
    re.search(r"\d", password) and
    re.search(r"[~!@#$%&_\-\+=`|\\(){}\[\]:;'<>,.?/]", password)
)

def is_valid_zip(zip_code):
    return bool(re.fullmatch(r"\d{4}[A-Z]{2}", zip_code.strip().upper()))


def is_valid_mobile(mobile):
    return bool(re.fullmatch(r"\d{8}", mobile.strip()))

def is_valid_license(license_number):
    return bool(re.fullmatch(r"[A-Za-z]{1,2}\d{7,8}", license_number.strip())) and len(license_number.strip()) == 9

def is_valid_gender(value: str) -> bool:
    return value.strip().lower() in ["male", "female"]

def is_valid_street(street: str) -> bool:
    return bool(street) and all(c.isalpha() or c.isspace() for c in street)

def is_valid_house_number(value: str) -> bool:
    return value.isdigit() and 0 < int(value) < 5663 # Highest house number in NL is 5663

def is_valid_city(city: str, cities: list) -> bool:
    return city in cities

def is_valid_date(value: str) -> bool:
    try:
        datetime.datetime.strptime(value, "%d-%m-%Y")
        return True
    except ValueError:
        return False
    
def is_valid_birthday(value: str) -> bool:
    try:
        birth_date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        today = datetime.date.today()
        age = (today - birth_date).days / 365.25
        return 16 < age <= 99
    except ValueError:
        return False


def is_valid_email_and_domain(email: str) -> bool:
    # Basic email validation
    email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    if not email_regex.match(email):
        return False
    
    # Domain validation
    domain = email.split('@')[1]
    valid_domains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]
    
    return domain in valid_domains

def is_valid_serial_number(serial_number):
    return serial_number.isalnum() and 10 <= len(serial_number) <= 17


def is_valid_number(number):
    try:
        num = float(number)
        return num == num and num != float("inf") and num != float("-inf")
    except (ValueError, TypeError):
        return False

def is_valid_model(model):
    try:
        model = model.strip()
        if not model:
            return False
        if len(model) < 2 or len(model) > 30:
            return False
        if not re.match(r"^[A-Za-z0-9\s\-]+$", model):
            return False
        return True
    except (ValueError, TypeError):
        return False

def is_valid_mileage(mileage):
    try:
        miles = float(mileage)
        if miles < 0 or miles > 99999:
            return False
        return True
    except (ValueError, TypeError):
        return False
    
def is_valid_speed(speed):
    try:
        speed_value = float(speed)
        if speed_value < 1 or speed_value > 100:
            return False
        return True
    except (ValueError, TypeError):
        return False

def is_valid_capacity(capacity):
    try:
        capacity_value = float(capacity)
        if capacity_value < 1 or capacity_value > 5000:
            return False
        return True
    except (ValueError, TypeError):
        return False
    
def is_valid_soc(soc):
    try:
        soc_value = float(soc)
        if soc_value < 0 or soc_value > 100:
            return False
        return True
    except (ValueError, TypeError):
        return False
    
def is_valid_range_soc(range_soc):
    try:
        if '-' not in range_soc:
            return False
        min_soc, max_soc = map(float, range_soc.split('-'))
        if min_soc < 0 or max_soc > 100 or min_soc >= max_soc:
            return False
        return True
    except (ValueError, TypeError):
        return False
    
def is_valid_date_iso_8601(date: str) -> bool:
    try:
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.date.today()
        valid_date = (today - date).days / 365.25
        return 0 < valid_date <= 99
    except ValueError:
        return False

def validate_restore_code(code_username):
    db_path="data/urban_mobility.db"
    flush_input()
    code = input("Enter the 12-character restore code: ").strip()

    if not re.fullmatch(r'[A-Z0-9]{12}', code):
        print("Invalid format. Code must be 12 characters, using only uppercase letters and numbers.")
        return None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username_hash = ?", (hashlib.sha256(code_username.encode()).hexdigest(),))
    belong_id = cursor.fetchone()[0]

    cipher = Fernet(os.getenv("FERNET_KEY").encode())
    cursor.execute("SELECT code FROM restore_codes")
    rows = cursor.fetchall()

    for row in rows:
        decrypted_code = cipher.decrypt(row[0].encode()).decode()
        if decrypted_code == code:
            cursor.execute("SELECT * FROM restore_codes WHERE code = ? AND system_admin_id = ?", (row[0], belong_id))
            result = cursor.fetchone()
            break
    conn.close()

    if result:
        print("Restore code is valid and exists. restoring backup...")
        return result
    else:
        print("Restore code not found.")
        flush_input()
        click_to_return()
        return None


def validate_code():
    db_path="data/urban_mobility.db"
    flush_input()
    code = input("Enter the 12-character restore code: ").strip()

    if not re.fullmatch(r'[A-Z0-9]{12}', code):
        print("Invalid format. Code must be 12 characters, using only uppercase letters and numbers.")
        return None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cipher = Fernet(os.getenv("FERNET_KEY").encode())
    cursor.execute("SELECT code FROM restore_codes")
    rows = cursor.fetchall()

    for row in rows:
        decrypted_code = cipher.decrypt(row[0].encode()).decode()
        if decrypted_code == code:
            cursor.execute("SELECT * FROM restore_codes WHERE code = ?", (row[0],))
            result = cursor.fetchone()
            break
    conn.close()

    if result:
        print("Restore code is valid and exists. restoring backup...")
        return result
    else:
        print("Restore code not found.")
        flush_input()
        click_to_return()
        return None