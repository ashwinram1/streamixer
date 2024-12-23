from enum import Enum, auto


class RequestType(Enum):
    NEXT = auto()
    PREV = auto()
    PAUSE_PLAY = auto()
    SEEK = auto()
