

from abc import ABC, abstractmethod
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.tools.sources.entities.browser import BrowserAnswer, BrowserQuestion
from innovation.FeedbackerAi.tools.sources.entities.source import SourceAnswer, SourceQuestion
from innovation.FeedbackerAi.tools.sources.source import Webpage
from typing import Set, List

class BrowserClient(ABC):
    
    def __init__(self, domain, available_source_types, available_platforms):
        self.domain = domain
        self.available_source_types = available_source_types
        self.available_platforms = available_platforms
        self.webpage = Webpage(self.domain)
        self.component_type = self.webpage.component_type

    
    @abstractmethod
    def extract_genres(self, max_results):
        pass
        
    @abstractmethod 
    def get_games(self, sourceQuestion: SourceQuestion, max_results, number_of_attempts: int = 3):
        pass

    @abstractmethod 
    def get_reviews(self, sourceQuestion: SourceQuestion, max_results):
        pass