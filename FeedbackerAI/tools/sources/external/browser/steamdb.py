import os
from typing import Optional, Dict, Any
from abc import ABC
import datetime
from innovation.FeedbackerAi.tools.sources.source import Webpage
from innovation.FeedbackerAi.tools.sources.external.browser.browser_client import BrowserClient
from innovation.FeedbackerAi.tools.local.entities.platform import PLATFORM
from innovation.FeedbackerAi.tools.local.dtos.source_type import SOURCE_TYPE
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE, GENRE_TYPE

# Load configuration
# config = Utility.load_yaml()["local"]["cache"]

class SteamDbClient(BrowserClient):
       
    available_source_types = [SOURCE_TYPE.CRITIC, SOURCE_TYPE.USER]
    available_platforms = [PLATFORM.PC, PLATFORM.PS5, PLATFORM.XBOX_X]
    
    def __init__(self, config, to_debug):
        super().__init__("steamdb.com", SteamDbClient.available_source_types, SteamDbClient.available_platforms)
        self.config = config
        self.to_debug = to_debug
   