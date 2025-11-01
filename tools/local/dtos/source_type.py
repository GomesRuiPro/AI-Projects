from enum import Enum

# Boolean values represent if these are official/recognized entity (false) or player feedback (true)
class SOURCE_TYPE(Enum):
    FORUM = "forum", True
    SOCIAL_MEDIA = "social-media", True
    CRITIC = "critic", False
    USER = "user", True
    ALL = "all", True
    
    @classmethod
    def __getitem__(cls, item):
        # Override to make lookups case-insensitive
        item = item.upper()
        return super().__getitem__(item)