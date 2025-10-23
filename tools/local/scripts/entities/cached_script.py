from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.local.memory.cache import CacheClient
from innovation.FeedbackerAi.tools.local.scripts.entities.script import Script
import re
import ast
import json
from typing import Optional, Dict, Any

class CachedScript(Script):
    
    def __init__(self, parent_folder, name, topic, memento_enabled = False, force_update = False):
        super().__init__(parent_folder, name)
        self.topic = topic
        self.memento_enabled = memento_enabled
        self.force_update = force_update
        
    def execute(self, command="", inputs=..., args=...):
        method_args = (command, inputs, args)        
        
        if not self.force_update:
            cached_data = CacheClient.get_cached_data(self.topic)
            if not cached_data:
                cached_data = CacheClient.caching(self.topic, super().execute, method_args)
        else:
           cached_data = CacheClient.caching(self.topic, super().execute, method_args) 
        
        output_lines = []
        if self.memento_enabled:
            for output_line in cached_data: 
                output_lines.append(json.loads(output_line))
        elif cached_data:
            output_lines = [json.loads(cached_data)]
            
        self.output = output_lines
        return self.output