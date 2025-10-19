from abc import ABC, abstractmethod

class Database(ABC):
    
    def __init__(self, config):
        self.config = config
        
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