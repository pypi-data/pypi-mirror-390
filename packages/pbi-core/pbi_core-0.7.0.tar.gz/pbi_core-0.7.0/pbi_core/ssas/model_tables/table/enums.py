from enum import Enum


class DataCategory(Enum):
    """Source: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/6360ac84-0717-4170-bce0-284cbef419ca).

    Note:
        Only used for table, the Column and Measure DataCategories are just strings

    """

    UNKNOWN = 0
    REGULAR = 1
    TIME = 2
    GEOGRAPHY = 3
    ORGANIZATION = 4
    BILL_OF_MATERIALS = 5
    ACCOUNTS = 6
    CUSTOMERS = 7
    PRODUCTS = 8
    SCENARIO = 9
    QUANTITATIVE = 10
    UTILITY = 11
    CURRENCY = 12
    RATES = 13
    CHANNEL = 14
    PROMOTION = 15
