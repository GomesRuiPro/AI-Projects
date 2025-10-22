from enum import Enum

class AGE_GROUP(Enum):
    CHILD = range(7, 12)
    TEEN = range(13, 19)
    YOUNG_ADULT = range(20, 35)
    ADULT = range(36, 55)
    MIDDLE_AGED = range(56, 65)
    SENIOR = range(66, 100)