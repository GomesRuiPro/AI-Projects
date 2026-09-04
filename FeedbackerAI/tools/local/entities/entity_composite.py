from abc import ABC
from enum import Enum

class EntityComposite(ABC):
    
    def iterate(enum_obj: Enum, entity: str, linked_entity: object = None):
        for member in enum_obj:
            if member.value == entity:
                if linked_entity:
                    return linked_entity
                return True
        if linked_entity:
            return None
        return False