import re

USERNAME_REGEX = re.compile(r"^[a-z_][a-z0-9_'.]{7,9}$", re.IGNORECASE)


def is_valid_username(username):
    return bool(USERNAME_REGEX.fullmatch(username))


def is_valid_name(name):
    return (
        1 <= len(name) <= 30 and
        re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'.\- ]+", name)
    )


def is_valid_password(password):
    return (
    12 <= len(password) <= 30 and
    re.search(r"[a-z]", password) and
    re.search(r"[A-Z]", password) and
    re.search(r"\d", password) and
    re.search(r"[~!@#$%&_\-\+=`|\\(){}\[\]:;'<>,.?/]", password)
)