from . import constants

def username_validator(username: str) -> tuple[bool, str]:
    if username != username.lower():
        return False, 'Username can not contain uppercase letters'

    if username.isdecimal():
        return False, "Username can not be numeric"

    if not all([x.isnumeric() or x == '_' or x in constants.ALPHABET for x in username]):
        return False, "Username can only numbers and underscores"

    return True, ''