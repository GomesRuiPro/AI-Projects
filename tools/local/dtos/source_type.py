from enum import Enum

# Boolean values represent if these are official/recognized entity (false) or player feedback (true)
class SOURCE_TYPE(Enum):
    FORUM = "forum", True
    SOCIAL_MEDIA = "social-media", True
    CRITIC = "critic", False
    USER = "user", True
    UNKNOWN = "unknown", True