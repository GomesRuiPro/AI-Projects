from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.sources.factory import DatabaseFactory, BrowserFactory, APIFactory
from innovation.FeedbackerAi.tools.sources.entities.source import SourceAnswer, SourceQuestion
from innovation.FeedbackerAi.tools.sources.external.browser.browser_client import BrowserClient
from innovation.FeedbackerAi.agents.entities.answer import Answer
from innovation.FeedbackerAi.agents.entities.question import Question
from typing import Set


SOURCES_CONFIG = Utility.load_yaml()["sources"]

class SourceClient(ABC):
    
    source = None

    @abstractmethod
    def create(device_debug=0):
        pass
    
    # To select which method to call after intersect / concatenate ops
    @staticmethod
    def execute(question: SourceQuestion) -> Set[Answer]:
        return question.method_fn(question)
    
    @staticmethod
    def extract_genres(sourceQuestion: SourceQuestion):
        SourceClient.source.extract_genres()

    @staticmethod
    def get_games(sourceQuestion: SourceQuestion):
        SourceClient.source.get_games(sourceQuestion)

    @staticmethod
    def get_reviews(sourceQuestion: SourceQuestion):
        SourceClient.source.get_reviews(sourceQuestion)


# INTERNAL SOURCES #
class Database(SourceClient):

    @staticmethod
    def create(device_debug=0):
        config = SOURCES_CONFIG['internal']['databases']
        databaseFactory = DatabaseFactory(
            config, SOURCES_CONFIG['path'])
        SourceClient.source = databaseFactory.create(device_debug)
        return SourceClient.source
    
# EXTERNAL SOURCES #    
class Api(SourceClient):

    @staticmethod
    def create(device_debug=0):
        config = SOURCES_CONFIG['external']['apis']
        apiFactory = APIFactory(config)
        SourceClient.source = apiFactory.create(device_debug)
        return SourceClient.source

class Browser(SourceClient):

    @staticmethod
    def create(device_debug=0):
        config = SOURCES_CONFIG['external']['websites']
        browserFactory = BrowserFactory(config)
        SourceClient.source = browserFactory.create(device_debug)
        return SourceClient.source
        
    