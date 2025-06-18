import sqlite3
from cryptography.fernet import Fernet
from datetime import datetime
import os
from tabulate import tabulate
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


def view_logs(session, db_path: str = "app.db"):
    if (not session.is_valid() or session.role not in ["super_admin", "system_admin"]):
        log_to_db({"username": session.user, "activity": "Unauthorized attempt to view system logs", "additional_info": f"{session.user} is not an admin.", "suspicious": 1})
        return

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs")
        rows = cursor.fetchall()

        # Column namen
        column_names = [description[0] for description in cursor.description]

        decrypted_logs = []
        for row in rows:
            decrypted_row = []
            for value in row:
                try:
                    decrypted_value = cipher.decrypt(value.encode()).decode()
                except Exception:
                    decrypted_value = value
                decrypted_row.append(decrypted_value)
            decrypted_logs.append(decrypted_row)

        if decrypted_logs:
            print(tabulate(decrypted_logs, headers=column_names, tablefmt="fancy_grid"))
        else:
            print("No logs to display.")
    
    log_to_db({"username": session.user, "activity": "Viewed activity logs", "additional_info": f"{session.user} an admin.", "suspicious": 0})