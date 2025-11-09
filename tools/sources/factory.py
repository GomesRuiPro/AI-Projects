from abc import ABC, abstractmethod
from enum import Enum
from innovation.FeedbackerAi.tools.sources.internal.database_sql.sql_lite import SQLite
from innovation.FeedbackerAi.tools.sources.external.browser.metacritic import MetacriticClient
from innovation.FeedbackerAi.tools.sources.external.browser.steamdb import SteamDbClient
from innovation.FeedbackerAi.tools.sources.source import Source
from innovation.FeedbackerAi.tools.local.entities.source_type import SOURCE_EXTERNAL_API, SOURCE_EXTERNAL_WEBSITE, SOURCE_INTERNAL_DATABASE
from typing import Optional, Dict, Any

class Factory(ABC):
    config = None
    source_to_run = None

    def __init__(self, config):
        self.config = config
        for source_to_run in self.config:
            if source_to_run['is_enabled']:
                self.source_to_run = source_to_run

# INTERNAL SOURCES #

class InternalSourceFactory(Factory, ABC):
    @abstractmethod
    def create(self, to_debug=0):
        pass

class DatabaseFactory(InternalSourceFactory):

    SOURCE_TYPE = SOURCE_INTERNAL_DATABASE
    
    def __init__(self, config):
        super().__init__(config)

    def create(self, database_path, to_debug=0):
        if not self.source_to_run:
            return None

        # do reflection here
        source_name = self.source_to_run['name']
        database_file_path = database_path + "/" + self.source_to_run['storage']
        if DatabaseFactory.SOURCE_TYPE.SQLITE.value in source_name.lower():
            return SQLite(self.source_to_run, database_file_path, to_debug)

# EXTERNAL SOURCES #

class ExternalSourceFactory(Factory, ABC):
    @abstractmethod
    def create(self, to_debug=0):
        pass
        
class BrowserFactory(ExternalSourceFactory):

    SOURCE_TYPE = SOURCE_EXTERNAL_WEBSITE
    
    def __init__(self, config):
        super().__init__(config)

    def create(self, to_debug=0):
        if not self.source_to_run:
            return None
        
        # do reflection here
        source_name = self.source_to_run['name']
        if BrowserFactory.SOURCE_TYPE.METACRITIC.value in source_name.lower():
            return MetacriticClient(self.source_to_run, to_debug)
        if BrowserFactory.SOURCE_TYPE.STEAMDB.value in source_name.lower():
            return SteamDbClient(self.source_to_run, to_debug)
        
class APIFactory(ExternalSourceFactory):

    SOURCE_TYPE = SOURCE_EXTERNAL_API
    
    def __init__(self, config):
        super().__init__(config)

    def create(self, to_debug=0):
        if not self.source_to_run:
            return None

        # do reflection here
        source_name = self.source_to_run['name']
        if APIFactory.SOURCE_TYPE.YOUTUBE.value in source_name.lower():
            return None
        if APIFactory.SOURCE_TYPE.STEAM.value in source_name.lower():
            return None