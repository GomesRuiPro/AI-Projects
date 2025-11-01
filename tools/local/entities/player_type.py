from enum import Enum

class PLAYER_TYPE(Enum):
    GENERIC = "generic"
    GAMING = "gaming"
    UNKNOWN = "unknown"
    
    @classmethod
    def __getitem__(cls, item):
        # Override to make lookups case-insensitive
        item = item.upper()
        return super().__getitem__(item)