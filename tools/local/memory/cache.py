import os
from innovation.FeedbackerAi.tools.local.utilities import Utility
from abc import ABC
import datetime
from typing import Optional, Dict, Any

# Load configuration
config = Utility.load_yaml()["local"]["cache"]

class CacheClient(ABC):
    PATH = config["path"]
    MEMORY = {}

    @staticmethod
    def init_cache():
        if CacheClient.MEMORY:
            raise Exception("Compiler error: The cache memory is already initialized with value. You will need to reload if you wish to reset the data in runtime!")
        CacheClient.MEMORY = Utility.files_to_dict(CacheClient.PATH)
        for topic in CacheClient.MEMORY.keys():
            cache = CacheClient.__Cache(topic)
            CacheClient.MEMORY[topic] = cache
        
    # WARNING: this method will reset available data! 
    @staticmethod
    def reload_cache():
        if not config['ignore_warning']:
            print("WARNING: You are about to reset data that is live and saved in a cache memory!")
            answer = input("Do you wish to continue? [y/n]").strip()
            if answer != 'y':
                return
        for topic in CacheClient.MEMORY.keys():
            cache = CacheClient.__Cache(topic)
            cache.create_content(topic)
            CacheClient.MEMORY[topic] = cache
            
    @staticmethod
    def get_cached_data(topic):
        return CacheClient.__get_data(topic)
    
    @staticmethod
    def caching(topic, method_to_call=None, method_args=None, memento_enabled=False):
        
        cached_data = None
        try:
            if not CacheClient.MEMORY:
                CacheClient.init_cache()
                
            cached_data = CacheClient.__get_data(topic)
            content = None
            if cached_data:
                # If we want historical data and the method is specified - add it everytime this is called (ASYNC)
                if memento_enabled and method_to_call:
                    content = Utility.call_lambda(method_to_call, method_args)
                    if content:
                        return CacheClient.__add_data(topic, content)
                # If we want to reset the data and the method is specified - reset it everytime this is called (ASYNC)
                if method_to_call:
                    content = Utility.call_lambda(method_to_call, method_args)
                    if content:
                        return CacheClient.__set_data(topic, content)
                # If no method is specified - return cached data
                return cached_data
            else:
                # If the method is specified - return new data and write into cache (ASYNC)
                if method_to_call:
                    content = Utility.call_lambda(method_to_call, method_args)
                    if content:
                        return CacheClient.__set_data(topic, content)
                # If no method is specified - return empty
                return None

        except Exception as ex:
            print(f"Caching was not possible: {ex} Skipping...")
            
        return cached_data
    
    @staticmethod
    def __get_history(topic):
        if topic in CacheClient.MEMORY:
            if CacheClient.MEMORY[topic]:
                return CacheClient.MEMORY[topic].load_content()
            return None
        return None
    
    @staticmethod    
    def __get_data(topic):
        if topic in CacheClient.MEMORY:
            if CacheClient.MEMORY[topic]:
                return CacheClient.MEMORY[topic].load_content()[0]
            return None
        return None
            
    @staticmethod
    def __add_data(topic, data):
        temp_cache = CacheClient.MEMORY[topic]
        temp_cache.update_content(data)
        # if topic in CacheClient.MEMORY:
        #     temp_cache = CacheClient.MEMORY[topic]
        #     if temp_cache:
        #         temp_cache.update_content(data)
        # else:
        #     cache = CacheClient.__Cache(topic)
        #     cache.create_content(data)
        #     CacheClient.MEMORY[topic] = cache
        return CacheClient.__get_history(topic)

    @staticmethod
    def __set_data(topic, data):
        if topic in CacheClient.MEMORY:
            temp_cache = CacheClient.MEMORY[topic]
            if temp_cache:
                temp_cache.create_content(data) 
            else:
                cache = CacheClient.__Cache(topic)
                cache.create_content(data)
                CacheClient.MEMORY[topic] = cache
        else:
            cache = CacheClient.__Cache(topic)
            cache.create_content(data)
            CacheClient.MEMORY[topic] = cache
        return CacheClient.__get_data(topic)
    
    class __Cache:
        
        topic = None
        file_path = None
        
        def __init__(self, topic):
            self.topic = topic
            self.file_path = f"{CacheClient.PATH}{topic}.txt"
            # for volatile_topic in config["list_volatile_topics"].split(','):
            #     if self.topic == volatile_topic:
            #         self.is_volatile = True              
            
        def load_content(self):
            if Utility.does_file_exist(self.file_path):
                return Utility.read_data_from_file(self.file_path)
            return None

        def create_content(self, content):
            if Utility.does_file_exist(self.file_path):
                Utility.remove_file(self.file_path)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content = f"--- {current_time} ---\n{content}"
            Utility.create_file_from_path(self.file_path, content)
        
        def update_content(self, content):
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content = f"--- {current_time} ---\n{content}"
            Utility.append_to_file(self.file_path, content)
            
        def remove_content(self):
            Utility.remove_file(self.file_path)
            