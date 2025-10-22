from innovation.FeedbackerAi.tools.models.model import Model
from typing import Optional, Dict, Any


class DoNothing(Model):
    def __init__(self):
        super().__init__(None, None)

    def execute(self):
        return None
