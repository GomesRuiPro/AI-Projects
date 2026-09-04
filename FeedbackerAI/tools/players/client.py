from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.agents.entities.component_type import ComponentType

PLAYER_CONFIG = Utility.load_yaml()["player"]

# TBD = work in progress
class PlayerClient(ABC):
    
    component_type = ComponentType.PLAYER

    @abstractmethod
    def create():
        pass
    
class GamingPlayer(PlayerClient):

    @staticmethod
    def create():
        config = PLAYER_CONFIG['games'] 
    
class GenericPlayer(PlayerClient):
    @staticmethod
    def create():
        config = PLAYER_CONFIG['generic']