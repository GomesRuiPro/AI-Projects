from innovation.FeedbackerAi.tools.players.player import Player
from typing import Optional, Dict, Any


class DoNothing(Player):
    def __init__(self):
        super().__init__()

    def execute(self):
        return None
