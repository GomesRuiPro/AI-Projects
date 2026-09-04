from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from innovation.FeedbackerAi.agents.entities.component_type import ComponentType

# Based on personalities
class Player(ABC):
    component_type = ComponentType.PLAYER

class Generic(Player, ABC):
    pass

class Gaming(Player, ABC):
    pass