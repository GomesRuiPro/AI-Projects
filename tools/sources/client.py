from abc import ABC, abstractmethod
from inspect import ismethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.sources.factory import DatabaseFactory, BrowserFactory, APIFactory
from innovation.FeedbackerAi.tools.sources.entities.source import SourceAnswer, SourceQuestion
from innovation.FeedbackerAi.tools.sources.external.browser.browser_client import BrowserClient
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component_type import ComponentType
from typing import Set, List


SOURCES_CONFIG = Utility.load_yaml()["sources"]

class SourceClient(ABC):
    
    component_type = ComponentType.SOURCE

    @abstractmethod
    def create(device_debug=0):
        pass
    
    # To select which method to call after intersect / concatenate ops
    @staticmethod
    def execute(source, question: SourceQuestion, method_fn: ismethod, max_results: int) -> List[Answer]:
        return method_fn(source, question, max_results)
    
    @staticmethod
    def extract_genres(source, sourceQuestion: SourceQuestion, max_results):
        return source.extract_genres(max_results)

    @staticmethod
    def get_games(source, sourceQuestion: SourceQuestion, max_results):
        return source.get_games(sourceQuestion, max_results)

    @staticmethod
    def get_reviews(source, sourceQuestion: SourceQuestion, max_results):
        return source.get_reviews(sourceQuestion, max_results)


# INTERNAL SOURCES #
class Database(SourceClient):

    @staticmethod
    def create(device_debug=0):
        config = SOURCES_CONFIG['internal']['databases']
        databaseFactory = DatabaseFactory(
            config, SOURCES_CONFIG['path'])
        return databaseFactory.create(device_debug)
        
    
# EXTERNAL SOURCES #    
class Api(SourceClient):

    @staticmethod
    def create(device_debug=0):
        config = SOURCES_CONFIG['external']['apis']
        apiFactory = APIFactory(config)
        return apiFactory.create(device_debug)
        

class Browser(SourceClient):

    @staticmethod
    def create(device_debug=0):
        config = SOURCES_CONFIG['external']['websites']
        browserFactory = BrowserFactory(config)
        return browserFactory.create(device_debug)
        
        
    