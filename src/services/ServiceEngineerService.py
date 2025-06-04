import bcrypt
import os
import sqlite3
import sys
from src.models import Session


class ServiceEngineerService():
    def __init__(self, session: Session):
        self.session: Session = session

    def update_scooter(self, scooter_id):
        if (not self.session.is_valid()):
            print("session expired")
            return
        print(f"Updated scooter {scooter_id}.")

    def check_scooter_status(self, scooter_id):
        if (not self.session.is_valid()):
            print("session expired")
            return
        print(f"Scooter {scooter_id} status: OK.")
