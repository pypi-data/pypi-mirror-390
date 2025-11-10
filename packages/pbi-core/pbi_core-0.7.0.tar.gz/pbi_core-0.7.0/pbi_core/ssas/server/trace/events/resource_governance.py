from enum import Enum


class WlgroupCpuThrottlingColumns(Enum):
    EVENT_CLASS = 0
    CURRENT_TIME = 2
    INTEGER_DATA = 10
    OBJECT_ID = 11
    SERVER_DATA = 43
    ACTIVITY_ID = 46
    REQUEST_ID = 47
    APPLICATION_CONTEXT = 52


class WlgroupExceedsMemoryLimitColumns(Enum):
    EVENT_CLASS = 0
    CURRENT_TIME = 2
    START_TIME = 3
    INTEGER_DATA = 10
    OBJECT_ID = 11
    TEXT_DATA = 42
    SERVER_DATA = 43
    ACTIVITY_ID = 46
    REQUEST_ID = 47
    APPLICATION_CONTEXT = 52


class WlgroupExceedsProcessingLimitColumns(Enum):
    EVENT_CLASS = 0
    CURRENT_TIME = 2
    INTEGER_DATA = 10
    OBJECT_ID = 11
    SERVER_DATA = 43
    ACTIVITY_ID = 46
    REQUEST_ID = 47
    APPLICATION_CONTEXT = 52
