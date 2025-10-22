from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.sources.factory import DatabaseFactory, BrowserFactory, APIFactory

SOURCES_CONFIG = Utility.load_yaml()["sources"]

class SourceClient(ABC):
    
    source = None

    @abstractmethod
    def create(device_debug=0):
        pass

# INTERNAL SOURCES #
class Database(SourceClient):

    @staticmethod
    def create(device_debug=0):
        config = SOURCES_CONFIG['internal']['databases']
        databaseFactory = DatabaseFactory(
            config, SOURCES_CONFIG['path'])
        SourceClient.model = databaseFactory.create(device_debug)
        return SourceClient.model
    
# EXTERNAL SOURCES #    
class Api(SourceClient):

    @staticmethod
    def create(device_debug=0):
        config = SOURCES_CONFIG['external']['apis']
        apiFactory = APIFactory(config)
        SourceClient.model = apiFactory.create(device_debug)
        return SourceClient.model

class Webpage(SourceClient):

    @staticmethod
    def create(device_debug=0):
        config = SOURCES_CONFIG['external']['websites']
        browserFactory = BrowserFactory(config)
        SourceClient.model = browserFactory.create(device_debug)
        return SourceClient.model
