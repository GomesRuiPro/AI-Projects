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

class SOURCE_TYPE(Enum):
    def __init__(self, description, subsources: Enum = None):
        super().__init__()
        self.description = description
        self.subsources = subsources
    
    @classmethod
    def __getitem__(cls, item):
        # Override to make lookups case-insensitive
        item = item.upper()
        return super().__getitem__(item)
    
class SOURCE_INTERNAL_DATABASE(SOURCE_TYPE):
    SQLITE = "sqlite3"
    UNKNOWN = "unknown"
    
    def parent(self) -> SOURCE_TYPE:
        return SOURCE_INTERNAL, SOURCE_INTERNAL.DATABASE
    
    def get_client(self):
        from innovation.FeedbackerAi.tools.sources.client import Database
        return Database
    
class SOURCE_INTERNAL(SOURCE_TYPE):
    DATABASE = "database", SOURCE_INTERNAL_DATABASE
    UNKNOWN = "unknown"
    
    def parent(self) -> SOURCE_TYPE:
        return SOURCE, SOURCE.INTERNAL
    
class SOURCE_EXTERNAL_BROWSER(SOURCE_TYPE):
    METACRITIC = "metacritic"
    STEAMCHARTS = "steamcharts"
    STEAMDB = "steamdb"
    UNKNOWN = "unknown"

    def parent(self) -> SOURCE_TYPE:
        return SOURCE_EXTERNAL, SOURCE_EXTERNAL.BROWSER
    
    def get_client(self):
        from innovation.FeedbackerAi.tools.sources.client import Browser
        return Browser
    
class SOURCE_EXTERNAL_API(SOURCE_TYPE):
    YOUTUBE = "youtube"
    STEAM = "steam"
    UNKNOWN = "unknown"
        
    def parent(self) -> SOURCE_TYPE:
        return SOURCE_EXTERNAL, SOURCE_EXTERNAL.API
    
    def get_client(self):
        from innovation.FeedbackerAi.tools.sources.client import Api
        return Api
    
class SOURCE_EXTERNAL(SOURCE_TYPE):
    BROWSER = "website", SOURCE_EXTERNAL_BROWSER
    API = "api", SOURCE_EXTERNAL_API
    UNKNOWN = "unknown"
    
    def parent(self) -> SOURCE_TYPE:
        return SOURCE, SOURCE.EXTERNAL
    
class SOURCE(Enum):
    INTERNAL = "internal", SOURCE_INTERNAL
    EXTERNAL = "external", SOURCE_EXTERNAL
    UNKNOWN = "unknown"
    
    def parent(self):
        return None, SOURCE

# Update this method if you add more enums
# available_children = all the bottom/leaf children 
# number_of_levels = levels you want to recurse (by default - goes until the highest parent/branch)
def recurse_bottom_to_top(bottom_name: str, 
                          available_children: List[SOURCE_TYPE] = [SOURCE_INTERNAL_DATABASE, SOURCE_EXTERNAL_BROWSER, SOURCE_EXTERNAL_API],
                          number_of_levels: int = 3) -> Enum:
    
    found_source_type: SOURCE_TYPE = None
    
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

