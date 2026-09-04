from innovation.FeedbackerAi.tools.sources.internal.db import Database
from typing import Optional, Dict, Any

class SQLDb(Database):
    
    def __init__(self, config, db_name, to_debug):
        super().__init__(config, to_debug)
        self.db_name = db_name