from enum import Enum, unique


@unique
class Context(Enum):
    FEATURE = 0
    DEV = 1
    TEST = 2
    STAGE = 3
    PRODUCTION = 4