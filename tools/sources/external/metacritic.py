import os
from innovation.FeedbackerAi.tools.sources.source import Webpage
from innovation.FeedbackerAi.tools.utilities import Utility
from abc import ABC
import datetime

# Load configuration
# config = Utility.load_yaml()["local"]["cache"]

class MetacriticClient():
      
    DOMAIN = "metacritic.com"

    _instance = None

    def __new__(cls, config):
        if cls._instance is None:
            cls._instance = super(MetacriticClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        self.config = config
        self.webpage = Webpage(MetacriticClient.DOMAIN)
        
    def get_games(self, genre, year_min, year_max, max_results, sort_by="userscore"):
        
        # Setting url
        release_year = ["current-year",""] if year_min == year_max else ["all_time",f"releaseYearMin={year_min}&releaseYearMax={year_max}&"]
        self.webpage.resource = f"browse/game/all/{genre}/{release_year[0]}/{sort_by}"
        self.webpage.filter = f"?{release_year[1]}genre={genre}&page=1"
        
        # Setting ui component tree structure
        parent_ui_component = Webpage.Branch(_class="c-productListings")
        parent_ui_component.tags["custom_1"] = "section=detailed|1"
        parent_ui_component.add(Webpage.Leaf("data-title", _class="c-finderProductCard_title"))
        self.webpage.ui_component = parent_ui_component
        # self.webpage.ui_component = Webpage.Leaf("data-title", _class="c-finderProductCard_title")
        
        results = Utility.scrappe_url(self.webpage, max_results)
        return results