from abc import ABC
from dataclasses import dataclass

@dataclass
class Component(ABC):
    
    def __init__(self, name, config):
        self.name = name
        self.config = config
    
    