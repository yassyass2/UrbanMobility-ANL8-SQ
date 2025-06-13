from models.Session import Session
from models.User import User
from services.SystemAdminService import SystemAdminService
import zipfile
import os
from datetime import datetime

DB_FILE = "src/data/urban_mobility.db"
BACKUP_DIR = "system_backups"


class SuperAdminService(SystemAdminService):
    def __init__(self, session: Session):
        super().__init__(session)

    def create_backup(self):
        if not self.session.is_valid() or self.session.role not in ["super_admin"]:
            return "Fail, Session expired" if not self.session.is_valid() else "Must be super admin to perform this action."
        
        if not os.path.exists(DB_FILE):
            return (False, f"Database file '{DB_FILE}' does not exist.")

        os.makedirs(BACKUP_DIR, exist_ok=True)

        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{backup_timestamp}.zip"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(DB_FILE, arcname=os.path.basename(DB_FILE))
            return (True, f"Backup created at: {backup_path}")
        except Exception as e:
            return (False, f"Backup failed: {e}")
        
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
    
    def restore_backup(self):
        print("doe ik morgen")
