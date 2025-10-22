from innovation.FeedbackerAi.tools.sources.source import Source
from typing import Optional, Dict, Any


class DoNothing(Source):
    def __init__(self):
        super().__init__()

    def execute(self):
        return None
