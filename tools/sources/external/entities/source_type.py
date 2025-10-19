from enum import Enum

# Boolean values represent if these are critic or user feedback
class SOURCE_TYPE(Enum):
    FORUM = False
    SOCIAL_MEDIA = False
    CRITIC = True
    USER = False
    UNKNOWN = False