from enum import Enum

class ActivityType(str, Enum):
    CALL = "call"
    MEETING = "meeting"
    TASK = "task"