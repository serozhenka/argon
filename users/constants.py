from enum import Enum

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

class DashboardPages(str, Enum):
    EDIT_PROFILE = 'edit_profile'
    PASSWORD = 'password_change'
    PRIVACY_AND_SECURITY = 'privacy_and_security'