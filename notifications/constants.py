from enum import Enum

NOTIFICATIONS_PAGE_SIZE = 10


class NotificationType(str, Enum):
    LOAD_NOTIFICATIONS = "load_notifications"

    PAGINATION_EXHAUSTED = "pagination_exhausted"
    ERROR = "error"