from db import Database

class SQL_DB(Database):
    
    def __init__(self, config, db_name):
        super().__init__(config)
        self.db_name = db_name