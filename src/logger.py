import sqlite3
from cryptography.fernet import Fernet
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

cipher = Fernet(os.environ["FERNET_KEY"].encode())



def log_to_db(log_dict: dict, db_path: str = "src/data/urban_mobility.db"):
    # log dict bevat username, activity, additional_info en suspicious
    now = datetime.now()
    log_dict["date"] = now.strftime("%Y-%m-%d")
    log_dict["time"] = now.strftime("%H:%M:%S")

    encrypted_logs = {k: cipher.encrypt(str(v).encode()).decode() for k, v in log_dict.items()}

    columns = ', '.join(encrypted_logs.keys())
    placeholders = ', '.join('?' for _ in encrypted_logs)
    values = list(encrypted_logs.values())

    query = f"INSERT INTO activity_logs ({columns}) VALUES ({placeholders})"

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
