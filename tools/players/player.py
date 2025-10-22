from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

# Based on personalities
class Player(ABC):
    pass

class Generic(Player, ABC):
    pass

class Gaming(Player, ABC):
    pass