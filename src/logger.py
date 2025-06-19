import sqlite3
from cryptography.fernet import Fernet
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

cipher = Fernet(os.environ["FERNET_KEY"].encode())



def log_to_db(log_dict: dict, db_path: str = "data/urban_mobility.db"):
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


def view_logs(session, only_unviewed=False, db_path: str = "data/urban_mobility.db"):
    if (not session.is_valid() or session.role not in ["super_admin", "system_admin"]):
        log_to_db({"username": session.user, "activity": "Unauthorized attempt to view system logs", "additional_info": f"{session.user} is not an admin.", "suspicious": 1})
        return

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activity_logs")
        rows = cursor.fetchall()

        # Column namen
        column_names = [description[0] for description in cursor.description]

        logs_to_update = []

        decrypted_logs = []
        for row in rows:
            decrypted_row = []
            if not only_unviewed or row[7] == 0:
                for value in row:
                    try:
                        decrypted_value = cipher.decrypt(value.encode()).decode()
                    except Exception:
                        decrypted_value = value
                    decrypted_row.append(decrypted_value)

                decrypted_logs.append(decrypted_row)
                logs_to_update.append(row[0])

        if decrypted_logs:
            col_widths = [max(len(str(row[i])) for row in [column_names] + decrypted_logs) for i in range(len(column_names))]

            header = " | ".join(str(name).ljust(col_widths[i]) for i, name in enumerate(column_names))
            print(header)
            print("-" * len(header))

            for row in decrypted_logs:
                print(" | ".join(str(item).ljust(col_widths[i]) for i, item in enumerate(row)))
        elif not only_unviewed:
            print("No logs to display.")
        else:
            print("Currently, there are no unviewed logs. ")

        for log_id in logs_to_update:
            cursor.execute("UPDATE activity_logs SET viewed = ? WHERE id = ?", (1, log_id))
        conn.commit()
    
    log_to_db({"username": session.user, "activity": "Viewed activity logs", "additional_info": f"{session.user} is an admin.", "suspicious": 0})


def any_unviewed_suspicious_logs(db_path: str = "data/urban_mobility.db") -> bool:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT suspicious FROM activity_logs WHERE viewed = ?", (0,))
        rows = cursor.fetchall()

        for (encrypted_suspicious,) in rows:
            try:
                decrypted = cipher.decrypt(encrypted_suspicious.encode()).decode()
                if decrypted == "1":
                    return True
            except Exception as e:
                continue
    return False