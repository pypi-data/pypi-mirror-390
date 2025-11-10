from enum import Enum


class ExecuteSourceQueryColumns(Enum):
    EVENT_CLASS = 0
    CURRENT_TIME = 2
    START_TIME = 3
    END_TIME = 4
    DURATION = 5
    CPU_TIME = 6
    JOB_ID = 7
    SESSION_TYPE = 8
    INTEGER_DATA = 10
    OBJECT_ID = 11
    OBJECT_TYPE = 12
    OBJECT_NAME = 13
    OBJECT_PATH = 14
    SEVERITY = 22
    SUCCESS = 23
    ERROR = 24
    CONNECTION_ID = 25
    DATABASE_NAME = 28
    CLIENT_PROCESS_ID = 36
    SESSION_ID = 39
    SP_ID = 41
    TEXT_DATA = 42
    SERVER_DATA = 43
    ACTIVITY_ID = 46
    REQUEST_ID = 47
    ERROR_TYPE = 49
    APPLICATION_CONTEXT = 52
