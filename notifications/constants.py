from enum import Enum

NOTIFICATIONS_PAGE_SIZE = 10


class NotificationType(str, Enum):
    NEW_NOTIFICATION = "new_notification"
    DELETE_NOTIFICATION = "delete_notification"
    LOAD_NOTIFICATIONS = "load_notifications"
    NOTIFICATIONS_COUNT = "notifications_count"

    READ_NOTIFICATION = "read_notification"
    PAGINATION_EXHAUSTED = "pagination_exhausted"
    ERROR = "error"