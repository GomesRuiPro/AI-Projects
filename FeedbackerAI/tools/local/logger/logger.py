import logging
from abc import ABC
    
class LoggerSingleton:
    
    logger: logging.Logger = None
    
    @classmethod
    def create(cls, name='defaultLogger', log_file='', level=logging.INFO):
            
        if cls.logger:
            return cls.logger
        
        cls.logger = logging.getLogger(name)
        cls.logger.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(cls.logger.level)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(cls.logger.level)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            cls.logger.addHandler(file_handler)

        # Add handlers to the logger
        cls.logger.addHandler(console_handler)
        return cls.logger

class LoggerFactory(ABC):
    logger: logging.Logger = LoggerSingleton.create()
        
    @staticmethod
    def is_debug():
        if LoggerFactory.logger.level <= logging.DEBUG:
            return True
        return False
