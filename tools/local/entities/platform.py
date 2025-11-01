from enum import Enum

class PLATFORM(Enum):
    XBOX_X = "xbox-series-x"
    PC = "pc"
    PS5 = "playstation-5"
    NINTENDO_SW2 = "nintendo-switch-2"
    ALL = "all"
    
    @classmethod
    def __getitem__(cls, item):
        # Override to make lookups case-insensitive
        item = item.upper()
        return super().__getitem__(item)