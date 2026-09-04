from abc import ABC, abstractmethod
from enum import Enum
from innovation.FeedbackerAi.tools.players.player import Player
from innovation.FeedbackerAi.tools.local.entities.player_type import PLAYER_TYPE
from typing import Optional, Dict, Any

class Factory(ABC):
    config = None
    player_to_run = None

    def __init__(self, config):
        self.config = config
        for player_to_run in self.config:
            if player_to_run['is_enabled']:
                self.player_to_run = player_to_run

# PLAYER PERSONA #

class PlayerFactory(Factory):

    def __init__(self, config):
        super().__init__(config)

    def create(self, to_debug=0):
        if not self.player_to_run:
            return None

        # do reflection here
        player_name = self.player_to_run['name']
        if PLAYER_TYPE.GENERIC.value in player_name.lower():
            return None