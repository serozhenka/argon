from enum import Enum


class MsgType(str, Enum):
    STANDARD_MESSAGE = "standard_message"
    JOIN = "join"
    ERROR = "error"