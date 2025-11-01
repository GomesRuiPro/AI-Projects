import os
from typing import Optional, Dict, Any
from abc import ABC
import datetime
from innovation.FeedbackerAi.tools.sources.source import Webpage
from innovation.FeedbackerAi.tools.local.entities.platform import PLATFORM
from innovation.FeedbackerAi.tools.local.dtos.source_type import SOURCE_TYPE
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE, GENRE_TYPE

# Load configuration
# config = Utility.load_yaml()["local"]["cache"]

class SteamDbClient():
      
    DOMAIN = "steamdb.com"
    _instance = None
    
    available_source_types = [SOURCE_TYPE.CRITIC, SOURCE_TYPE.USER]
    available_platforms = [PLATFORM.PC, PLATFORM.PS5, PLATFORM.XBOX_X]
    

    def __new__(cls, config, to_debug):
        if cls._instance is None:
            cls._instance = super(SteamDbClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, config, to_debug):
        self.config = config
        self.to_debug = to_debug
        self.webpage = Webpage(SteamDbClient.DOMAIN)
   