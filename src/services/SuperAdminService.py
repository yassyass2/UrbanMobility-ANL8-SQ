import bcrypt
import sqlite3
from models.Session import Session
from services.SystemAdminService import SystemAdminService

DB_FILE = "src/data/urban_mobility.db"


class SuperAdminService(SystemAdminService):
    def __init__(self, session: Session):
        super().__init__(session)
