import time


class Session:
    def __init__(self, user, role):
        self.user = user
        self.role = role
        self.created_at = time.time()
        self.expires_in = 900

    def is_valid(self):
        return (time.time() - self.created_at) < self.expires_in
