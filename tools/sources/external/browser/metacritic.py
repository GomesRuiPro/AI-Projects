import os
from innovation.FeedbackerAi.tools.sources.source import Webpage
from innovation.FeedbackerAi.tools.sources.external.browser.browser_client import BrowserClient
from innovation.FeedbackerAi.tools.sources.entities.browser import BrowserAnswer, BrowserQuestion
from innovation.FeedbackerAi.tools.local.entities.platform import PLATFORM
from innovation.FeedbackerAi.tools.local.dtos.source_type import SOURCE_TYPE
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE, GENRE_TYPE
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.local.scripts.script_manager import ScriptManager
from typing import Optional, Dict, Any, Set, List
import math
from abc import ABC
import datetime
from typing import List

# Load configuration
# config = Utility.load_yaml()["local"]["cache"]

class MetacriticClient(BrowserClient):
      
    available_source_types = [SOURCE_TYPE.CRITIC, SOURCE_TYPE.USER]
    available_platforms = [PLATFORM.PC, PLATFORM.PS5, PLATFORM.XBOX_X]

    def __init__(self, config, to_debug):
        super().__init__("metacritic.com", MetacriticClient.available_source_types, MetacriticClient.available_platforms)
        self.config = config
        self.to_debug = to_debug
        
    def extract_genres(self):
        pass
        
    def get_games(self, browserQuestion: BrowserQuestion, max_results, number_of_attempts: int = 3) -> List[BrowserAnswer]:
        
        genre = browserQuestion.text
        year_min = browserQuestion.metadata["year_min"]
        year_max = browserQuestion.metadata.get("year_max", year_min)
        sort_by = browserQuestion.metadata.get("sort_by", "userscore")
        
        # Setting url
        release_year = ["current-year",""] if year_min == year_max else ["all_time",f"releaseYearMin={year_min}&releaseYearMax={year_max}&"]
        self.webpage.resource = f"browse/game/all/{genre}/{release_year[0]}/{sort_by}"
        self.webpage.filter = f"?{release_year[1]}genre={genre}&page=1"
        
        # Setting ui component tree structure
        parent_ui_component = Webpage.Branch(_class="c-productListings")
        parent_ui_component.tags["custom_1"] = "section=detailed|1"
        parent_ui_component.add(Webpage.Leaf(attr_to_fetch="href", _class="c-finderProductCard_container g-color-gray80 u-grid"))
        self.webpage.ui_component = parent_ui_component
        
        games_hrefs = ScriptManager.scrappe_url(self.webpage, max_results) # Gives a list of a dict with the key href. since memento is off, we will only get one row
        
        if number_of_attempts == 0:
            raise Exception("No games were found in Metacritic")
        if not games_hrefs:
            number_of_attempts = number_of_attempts-1
            browserQuestion.metadata["year_min"] = year_min-1
            return self.get_games(browserQuestion, max_results, number_of_attempts)
        
        games_hrefs_list = games_hrefs[0][0]['href']
        
        games: Set[str] = set()
        for game_href in games_hrefs_list:
            games.add(game_href.split("/")[2])
            
            if len(games) == max_results:
                break
            
        return [BrowserAnswer(game) for game in games]
    
    # We need to perform a for-loop because the url is different between different platforms and source types
    def get_reviews(self, browserQuestion: BrowserQuestion, max_results) -> List[BrowserAnswer]:
        
        app_globals = Utility.get_globals()
        
        game = browserQuestion.text
        source_types = browserQuestion.metadata.get("source_types", [SOURCE_TYPE.USER])
        platforms = browserQuestion.metadata.get("platforms", [PLATFORM.PS5])
        sort_by = browserQuestion.metadata.get("sort_by", "Metascore")
        genre = app_globals.genre
        focus = app_globals.focus
        
        source_types = list(set(self.available_source_types) & set(source_types))
        platforms = list(set(self.available_platforms) & set(platforms))
        
        # max_results_per_call = math.ceil(max_results/(len(source_types*len(platforms))))
        for platform in platforms:
            for source_type in source_types:
                # Setting url
                source_type_str = source_type.name.lower()
                platform_str = platform.value
                self.webpage.resource = f"game/{game}/{source_type_str}-reviews"
                self.webpage.filter = f"?platform={platform_str}&sort-by={sort_by}"
                
                # Setting ui component tree structure
                parent_ui_component = Webpage.Branch()
                parent_ui_component.tags["custom_1"] = "data-testid=product-reviews"
                parent_ui_component.add(Webpage.Leaf(type_to_fetch="span", _class="c-siteReview_quote g-outer-spacing-bottom-small"))
                self.webpage.ui_component = parent_ui_component
            
                # reviews[platform.name] = {
                #     source_type.name: []
                # }
                
                reviews_spans = ScriptManager.scrappe_url(self.webpage, max_results)
                
                reviews_spans_list = reviews_spans[0][0]['span']
                            
                # if len(reviews_spans_list) > max_results_per_call:
                #     reviews_spans_list = reviews_spans_list[-max_results_per_call:]
                
                # for review_span in reviews_spans_list:
                #     reviews.add(Review(genre=genre, focus=focus, text=review_span, source_type=source_type, platform=platform))
                    
                #     if len(reviews) == max_results:
                #         break
            
        # [review.print() for review in reviews]
        return [BrowserAnswer(review_span, metadata = {
                        "platform": platform,
                        "source_type": source_type
                    }) for review_span in reviews_spans_list[:max_results]]
                
                
    