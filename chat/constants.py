from enum import Enum

CHAT_ROOM_MESSAGE_PAGE_SIZE = 10


class MsgType(str, Enum):
    STANDARD_MESSAGE = "standard_message"
    LOAD_MESSAGES = "load_messages"
    JOIN = "join"
    ERROR = "error"

    PAGINATION_EXHAUSTED = "pagination_exhausted"

