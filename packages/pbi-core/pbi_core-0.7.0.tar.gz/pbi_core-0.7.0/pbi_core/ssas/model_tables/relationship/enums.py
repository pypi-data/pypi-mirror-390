from enum import Enum


class RelationshipType(Enum):
    SINGLE_COLUMN = 1


class CrossFilteringBehavior(Enum):
    ONE_DIRECTION = 1
    BOTH_DIRECTION = 2
    AUTOMATIC = 3


class JoinOnDateBehavior(Enum):
    DATE_AND_TIME = 1
    DATE_PART_ONLY = 2


class SecurityFilteringBehavior(Enum):
    ONE_DIRECTION = 1
    BOTH_DIRECTIONS = 2
    NONE = 3


class FromCardinality(Enum):
    ONE = 1
    MANY = 2


class ToCardinality(Enum):
    ONE = 1
    MANY = 2
