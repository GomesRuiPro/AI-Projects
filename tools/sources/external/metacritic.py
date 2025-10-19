import os
from innovation.FeedbackerAi.tools.sources.source import Webpage
from innovation.FeedbackerAi.tools.sources.external.entities.platform import PLATFORM
from innovation.FeedbackerAi.tools.sources.external.dtos.source import SOURCE_TYPE
from innovation.FeedbackerAi.tools.sources.external.dtos.game_genre import GENRE, SUBGENRE
from innovation.FeedbackerAi.tools.utilities import Utility
from innovation.FeedbackerAi.tools.local.scripts.script_manager import ScriptManager
import math
from abc import ABC
import datetime
from typing import List

# Load configuration
# config = Utility.load_yaml()["local"]["cache"]

class MetacriticClient():
      
    DOMAIN = "metacritic.com"
    _instance = None
    
    available_source_types = [SOURCE_TYPE.CRITIC, SOURCE_TYPE.USER]
    available_platforms = [PLATFORM.PC, PLATFORM.PS5, PLATFORM.XBOX_X]
    

    def __new__(cls, config):
        if cls._instance is None:
            cls._instance = super(MetacriticClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        self.config = config
        self.webpage = Webpage(MetacriticClient.DOMAIN)
        
    def get_genres(self):
        pass
        
    def get_games(self, genre, year_min, year_max, max_results, sort_by="userscore"):
        
        # Setting url
        release_year = ["current-year",""] if year_min == year_max else ["all_time",f"releaseYearMin={year_min}&releaseYearMax={year_max}&"]
        self.webpage.resource = f"browse/game/all/{genre}/{release_year[0]}/{sort_by}"
        self.webpage.filter = f"?{release_year[1]}genre={genre}&page=1"
        
        # Setting ui component tree structure
        parent_ui_component = Webpage.Branch(_class="c-productListings")
        parent_ui_component.tags["custom_1"] = "section=detailed|1"
        parent_ui_component.add(Webpage.Leaf(attr_to_fetch="href", _class="c-finderProductCard_container g-color-gray80 u-grid"))
        self.webpage.ui_component = parent_ui_component
        
        games_hrefs = ScriptManager.scrappe_url(self.webpage, max_results)[0][0] # Gives a list of a dict with the key href. since memento is off, we will only get one row
        
        games_hrefs_list = games_hrefs['href']
        games = []
        for game_href in games_hrefs_list:
            games.append(game_href.split("/")[2])
        return games
    
    # We need to perform a for-loop because the url is different between different platforms and source types
    def get_reviews(self, game, max_results,
                    source_types: List[SOURCE_TYPE]=[SOURCE_TYPE.USER], 
                    platforms: List[PLATFORM]=[PLATFORM.PS5],
                    sort_by="Metascore"):
        
        reviews = {}
        source_types = list(set(MetacriticClient.available_source_types) & set(source_types))
        platforms = list(set(MetacriticClient.available_platforms) & set(platforms))
        
        max_results_per_call = math.ceil(max_results/(len(source_types*len(platforms))))
        for platform in platforms:
            for source_type in source_types:
                # Setting url
                source_type_str = source_type.name.lower()
                platform_str = platform.value
                self.webpage.resource = f"/{game}/{source_type_str}-reviews/"
                self.webpage.filter = f"?platform={platform_str}&sort-by={sort_by}"
                
                # Setting ui component tree structure
                parent_ui_component = Webpage.Branch()
                parent_ui_component.tags["custom_1"] = "data-testid=product-reviews"
                parent_ui_component.add(Webpage.Leaf(type_to_fetch="span", _class="c-siteReview_quote g-outer-spacing-bottom-small"))
                self.webpage.ui_component = parent_ui_component
            
                reviews[platform][source_type] = ScriptManager.scrappe_url(self.webpage, max_results_per_call)
                
        return reviews
                
                
    