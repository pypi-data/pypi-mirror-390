from enum import Enum


class ModelPermission(Enum):
    NONE = 1
    READ = 2
    READ_REFRESH = 3
    REFRESH = 4
    ADMINISTRATOR = 5
