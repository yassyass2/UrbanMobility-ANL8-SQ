from models.Session import Session
from models.User import User
from services.SystemAdminService import SystemAdminService

import zipfile
import os
import shutil

DB_FILE = "src/data/urban_mobility.db"
BACKUP_DIR = "system_backups"
TEMP_EXTRACT_PATH = "temp_restore" 


class SuperAdminService(SystemAdminService):
    def __init__(self, session: Session):
        super().__init__(session)

    def view_all_backups(self):
        if not self.session.is_valid() or self.session.role not in ["super_admin"]:
            return "Fail, Session expired" if not self.session.is_valid() else "Must be super admin to perform this action."

        if not os.path.exists(BACKUP_DIR):
            return []

        backups = [
            filename for filename in os.listdir(BACKUP_DIR)
            if filename.endswith(".zip") and os.path.isfile(os.path.join(BACKUP_DIR, filename))
        ]

        return sorted(backups)
    
    def restore_backup_without_code(self, backup_filename: str) -> tuple[bool, str]:
        if not self.session.is_valid() or self.session.role not in ["super_admin"]:
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

            return True, "Backup successfully restored."

        except Exception as e:
            return False, f"Error restoring backup: {str(e)}"

        finally:
            # Clean up van tijdelijke folder
            shutil.rmtree(TEMP_EXTRACT_PATH, ignore_errors=True)

    def generate_restore_code()
