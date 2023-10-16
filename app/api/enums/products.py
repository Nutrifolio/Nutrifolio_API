from enum import Enum, IntEnum


class MaxDistanceOption(IntEnum):
    ONE_KM = 1
    THREE_KM = 3
    FIVE_KM = 5


class SortByOption(str, Enum):
    PRICE = 'price'
    DISTANCE_KM = 'distance_km'
    POPULARITY = 'view_count'


class SortOrderOption(str, Enum):
    ASC = 'ASC'
    DESC = 'DESC'
