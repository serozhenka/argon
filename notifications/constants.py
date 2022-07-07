from enum import Enum

NOTIFICATIONS_PAGE_SIZE = 10


class NotificationType(str, Enum):
    NEW_NOTIFICATION = "new_notification"
    DELETE_NOTIFICATION = "delete_notification"
    LOAD_NOTIFICATIONS = "load_notifications"
    NOTIFICATIONS_COUNT = "notifications_count"

    NEW_CHAT_MESSAGE_NOTIFICATION = "new_chat_message_notification"
    EDIT_CHAT_MESSAGE_NOTIFICATION = "edit_chat_message_notification"
    MESSAGES_NOTIFICATIONS_COUNT = "messages_notifications_count"

    ROOM_EMPTY = "room_empty"

    READ_NOTIFICATION = "read_notification"
    PAGINATION_EXHAUSTED = "pagination_exhausted"
    ERROR = "error"