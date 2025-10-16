import os
from innovation.FeedbackerAi.tools.sources.source import Webpage
from abc import ABC
import datetime

# Load configuration
# config = Utility.load_yaml()["local"]["cache"]

class SteamDbClient(ABC):
      
    @staticmethod
    def init():
        pass
    
    @staticmethod
    def get_subgenres():
        pass
   