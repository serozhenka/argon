from enum import Enum

CHAT_ROOM_MESSAGE_PAGE_SIZE = 50


class MsgType(str, Enum):
    STANDARD_MESSAGE = "standard_message"
    LOAD_MESSAGES = "load_messages"
    DELETE_MESSAGE = "delete_message"
    EDIT_MESSAGE = "edit_message"
    SET_MESSAGE_READ = "set_message_read"

    JOIN = "join"
    ERROR = "error"

    PAGINATION_EXHAUSTED = "pagination_exhausted"
    DISPLAY_LOADING_SPINNER = "display_loading_spinner"

