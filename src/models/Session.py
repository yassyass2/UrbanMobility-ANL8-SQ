import time
from ui.menu_utils import *
from logger import *


class Session:
    def __init__(self, user, role):
        self.user = user
        self.role = role
        self.created_at = time.time()
        self.expires_in = 900

    def is_valid(self):
        if not (time.time() - self.created_at) < self.expires_in:
            flush_input()
            print("Your Session has expired, you were logged in over 15 minutes.")
            log_to_db({"username": self.user, "activity": "Users session expired", "additional_info": "", "suspicious": 0})
            click_to_renew_session()
            raise SessionExpired("User token expired at 12:04")
            
        else:
            return True

class SessionExpired(Exception):
    pass