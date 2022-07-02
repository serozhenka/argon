from enum import Enum

CHAT_ROOM_MESSAGE_PAGE_SIZE = 50


class MsgType(str, Enum):
    STANDARD_MESSAGE = "standard_message"
    LOAD_MESSAGES = "load_messages"
    DELETE_MESSAGE = "delete_message"
    JOIN = "join"
    ERROR = "error"

    PAGINATION_EXHAUSTED = "pagination_exhausted"

