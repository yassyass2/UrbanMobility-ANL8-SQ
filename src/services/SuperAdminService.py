from models.Session import Session
from services.SystemAdminService import SystemAdminService
import sqlite3
import secrets
import string
from datetime import datetime
from logger import *

import zipfile
import os
import shutil

DB_FILE = "data/urban_mobility.db"
BACKUP_DIR = "system_backups"
TEMP_EXTRACT_PATH = "temp_restore"


class SuperAdminService(SystemAdminService):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def restore_backup_without_code(self, backup_filename: str) -> tuple[bool, str]:
        if not self.session.is_valid() or self.session.role not in ["super_admin"]:
            log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to restore backup", "additional_info": f"{self.session.user} has no super admin session.", "suspicious": 1})
            return "Fail, Session expired" if not self.session.is_valid() else "Must be super admin to perform this action."
         
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        if not os.path.exists(backup_path):
            return False, f"Backup file '{backup_filename}' not found."

        try:
            os.makedirs(TEMP_EXTRACT_PATH, exist_ok=True)

            with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                zip_ref.extractall(TEMP_EXTRACT_PATH)

            db_files = [f for f in os.listdir(TEMP_EXTRACT_PATH) if f.endswith('.db')]
            if not db_files:
                return False, "No database file found in the backup ZIP."

            extracted_db_path = os.path.join(TEMP_EXTRACT_PATH, db_files[0])

            shutil.copy2(extracted_db_path, DB_FILE)

            log_to_db({"username": self.session.user, "activity": "Restored a backup", "additional_info": f"backup '{backup_filename}' restored.", "suspicious": 0})
            return True, "Backup successfully restored."

        except Exception as e:
            return False, f"Error restoring backup: {str(e)}"

        finally:
            # Clean up van tijdelijke folder
            shutil.rmtree(TEMP_EXTRACT_PATH, ignore_errors=True)

    def generate_restore_code(self, backup_file, admin_id):
        if not self.session.is_valid() or self.session.role not in ["super_admin"]:
            log_to_db({"username": self.session.user, "activity": "Unauthorized attempt to generate restore code", "additional_info": f"{self.session.user} has no super admin session.", "suspicious": 1})
            return "Fail, Session expired" if not self.session.is_valid() else "Must be super admin to perform this action."

        cipher = Fernet(os.getenv("FERNET_KEY").encode())
        characters = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(characters) for _ in range(12))

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO restore_codes (
                code,
                backup_filename,
                system_admin_id,
                used,
                created_at
            ) VALUES (?, ?, ?, ?, ?)
            ''', (cipher.encrypt(code.encode()).decode(), cipher.encrypt(backup_file.encode()).decode(), admin_id,
                  0, datetime.now().strftime('%Y-%m-%d')))
            
            conn.commit()
        log_to_db({"username": self.session.user, "activity": "Generated a Restore code", "additional_info": f"backup: '{backup_file}', admin: '{admin_id}'", "suspicious": 0})
        return f"Restore code for System Admin {admin_id} for {backup_file} succesfully created"

    def revoke_restore_code(self, code_to_delete):
        if not self.session.is_valid() or self.session.role not in ["super_admin"]:
            log_to_db({"username": self.session.user, "activity": "tried to revoke restore code", "additional_info": f"{self.session.user} has no super admin session.", "suspicious": 1})
            return "Fail, Session expired" if not self.session.is_valid() else "Must be super admin to perform this action."
        

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT code FROM restore_codes")
            rows = cursor.fetchall()
            cipher = Fernet(os.getenv("FERNET_KEY").encode())

            for row in rows:
                decrypted_code = cipher.decrypt(row[0].encode()).decode()
                if decrypted_code == code_to_delete:
                    cursor.execute("DELETE FROM restore_codes WHERE code = ?", (row[0],))
                    conn.commit()
                    break

            rows_deleted = cursor.rowcount

            if rows_deleted:
                log_to_db({"username": self.session.user, "activity": "Revoked a Restore code", "additional_info": f"Revoked code '{code_to_delete}'", "suspicious": 0})
                return f"Restore code '{code_to_delete}' deleted successfully."
            else:
                log_to_db({"username": self.session.user, "activity": f"Tried to revoke restore code'{code_to_delete}'", "additional_info": "not found", "suspicious": 0})
                return f"No restore code found for '{code_to_delete}'."
            
    def view_all_backups(self):
        if not self.session.is_valid() or self.session.role not in ["super_admin"]:
            log_to_db({"username": self.session.user, "activity": "Tried to view all backups", "additional_info": "Not a super admin", "suspicious": 1})
            return "Fail, Session expired" if not self.session.is_valid() else "Fail, Must be super admin to perform this action."

        if not os.path.exists(BACKUP_DIR):
            return []

        backups = [
            filename for filename in os.listdir(BACKUP_DIR)
            if filename.endswith(".zip") and os.path.isfile(os.path.join(BACKUP_DIR, filename))
        ]

        return sorted(backups)
