from abc import ABC, abstractmethod
from enum import Enum
from innovation.FeedbackerAi.tools.players.fallback.donothing.do_nothing import DoNothing
from innovation.FeedbackerAi.tools.players.fallback.userinput.user_input import UserInput
from innovation.FeedbackerAi.tools.players.player import Player
from innovation.FeedbackerAi.tools.local.entities.player_type import PLAYER_TYPE
from typing import Optional, Dict, Any

class Factory(ABC):
    config = None

    def __init__(self, config):
        self.config = config

    def to_fallback(self, player_to_replace, topic=""):
        if not self.config:
            return DoNothing()
        for player_to_run in self.config:
            if player_to_run['is_enabled']:
                return player_to_run
        return UserInput(player_to_replace, topic)

# PLAYER PERSONA #

class PlayerFactory(Factory):

    def __init__(self, config):
        super().__init__(config)

    def create(self, to_debug=0):
        player_to_run = super().to_fallback("Player")
        if isinstance(player_to_run, Player):
            return player_to_run

        # do reflection here
        player_name = player_to_run['name']
        if PLAYER_TYPE.GENERIC.value in player_name.lower():
            return None