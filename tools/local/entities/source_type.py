from enum import Enum
from typing import List, Dict
from abc import ABC, abstractmethod
from typing import Protocol

# class PARENT(Enum):
#     def __init__(self, name: str, child: Enum):
#         super().__init__()
#         self.name = name
#         self.child = child
    
#     def get_name(self):
#         return self.name
    
#     def get_child(self):
#         return self.child

class Child:
    pass
    
class SOURCE_INTERNAL_DATABASE(Child, Enum):
    SQLITE = "sqlite3"
    UNKNOWN = "unknown"
    
    def parent(self) -> Child:
        return SOURCE_INTERNAL, SOURCE_INTERNAL.DATABASE
    
    def get_client(self):
        from innovation.FeedbackerAi.tools.sources.client import Database
        return Database
    
class SOURCE_INTERNAL(Child, Enum):
    DATABASE = "database", SOURCE_INTERNAL_DATABASE
    UNKNOWN = "unknown", None
    
    def parent(self) -> Child:
        return SOURCE, SOURCE.INTERNAL
    
class SOURCE_EXTERNAL_WEBSITE(Child, Enum):
    METACRITIC = "metacritic"
    STEAMCHARTS = "steamcharts"
    STEAMDB = "steamdb"
    UNKNOWN = "unknown"

    def parent(self) -> Child:
        return SOURCE_EXTERNAL, SOURCE_EXTERNAL.WEBSITE
    
    def get_client(self):
        from innovation.FeedbackerAi.tools.sources.client import Webpage
        return Webpage
    
class SOURCE_EXTERNAL_API(Child, Enum):
    YOUTUBE = "youtube"
    STEAM = "steam"
    UNKNOWN = "unknown"
        
    def parent(self) -> Child:
        return SOURCE_EXTERNAL, SOURCE_EXTERNAL.API
    
    def get_client(self):
        from innovation.FeedbackerAi.tools.sources.client import Api
        return Api
    
class SOURCE_EXTERNAL(Child, Enum):
    WEBSITE = "website", SOURCE_EXTERNAL_WEBSITE
    API = "api", SOURCE_EXTERNAL_API
    UNKNOWN = "unknown", None
    
    def parent(self) -> Child:
        return SOURCE, SOURCE.EXTERNAL
    
class SOURCE(Enum):
    INTERNAL = "internal", SOURCE_INTERNAL
    EXTERNAL = "external", SOURCE_EXTERNAL
    UNKNOWN = "unknown", None
    
    def parent(self):
        return None, SOURCE

# Update this method if you add more enums
# available_children = all the bottom/leaf children 
# number_of_levels = levels you want to recurse (by default - goes until the highest parent/branch)
def recurse_bottom_to_top(bottom_name: str, 
                          available_children: List[Child] = [SOURCE_INTERNAL_DATABASE, SOURCE_EXTERNAL_WEBSITE, SOURCE_EXTERNAL_API],
                          number_of_levels: int = 3) -> Enum:
    
    found_source_type: Child = None
    
    if not available_children:
        return SOURCE(bottom_name)
    
    for source_type in available_children:
        try:
            for source_type_enum in source_type:
                if bottom_name in str(source_type_enum.value):
                    found_source_type = source_type(source_type_enum.value)
                    break
            if found_source_type:
                break
        except ValueError:
            continue
    
    if not found_source_type:
        raise Exception("Failed to find the source {bottom_name}")
    
    number_of_levels = number_of_levels-1
    if number_of_levels == 0:
        return found_source_type

    parent_of_this_child, parent_name_of_this_child = found_source_type.parent()
    return recurse_bottom_to_top(parent_name_of_this_child.name, [parent_of_this_child], number_of_levels)