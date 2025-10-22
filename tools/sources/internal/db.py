from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class Database(ABC):
    
    def __init__(self, config, to_debug):
        self.config = config
        self.to_debug = to_debug
        
    @abstractmethod
    def create(self, table_name, columns):
        pass
    
    @abstractmethod
    def update(self, table_name, column, value, condition):
        pass
    
    @abstractmethod
    def delete(self, table_name, condition):
        pass
    
    @abstractmethod
    def read(self, table_name, column=None, condition=None):
        pass
        
    def close(self):
        """
        Close the connection to the database.
        """
        self.conn.close()