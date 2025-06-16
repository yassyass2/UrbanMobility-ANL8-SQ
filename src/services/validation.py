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

def is_valid_zip(zip_code):
    return bool(re.fullmatch(r"\d{4}[A-Z]{2}", zip_code.strip().upper()))


def is_valid_mobile(mobile):
    return bool(re.fullmatch(r"\d{8}", mobile.strip()))

def is_valid_license(license_number):
    return bool(re.fullmatch(r"\d{10}", license_number.strip()))

def is_valid_gender(value: str) -> bool:
    return value.strip().lower() in ["male", "female"]

def is_valid_street(street: str) -> bool:
    return bool(street) and all(c.isalpha() or c.isspace() for c in street)

def is_valid_house_number(value: str) -> bool:
    return value.isdigit() and 0 < int(value) < 5663 # Highest house number in NL is 5663

def is_valid_city(city: str, cities: list) -> bool:
    return city in cities

def is_valid_date(value: str) -> bool:
    import datetime
    try:
        datetime.datetime.strptime(value, "%d-%m-%Y")
        return True
    except ValueError:
        return False
    
def is_valid_birthday(value: str) -> bool:
    import datetime
    try:
        birth_date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        today = datetime.date.today()
        age = (today - birth_date).days / 365.25
        return 0 < age <= 99
    except ValueError:
        return False


def is_valid_email_and_domain(email: str) -> bool:
    import re
    # Basic email validation
    email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    if not email_regex.match(email):
        return False
    
    # Domain validation
    domain = email.split('@')[1]
    valid_domains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]
    
    return domain in valid_domains