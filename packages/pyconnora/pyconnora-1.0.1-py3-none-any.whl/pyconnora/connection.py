
"""
Connect to Oracle databases
"""

import os
import platform
import cx_Oracle
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class Connect:
    host: str = None
    user: str = None
    password: str = None
    db: str = None                 
    port: str = None
    schema: str = "dashboard"
    table: str = "employee_dtl"

        
    def __post_init__(self) -> None:
        if platform.system() == 'Windows':
            home_dir = 'HOMEPATH'
        elif platform.system() == 'Linux':
            home_dir = 'HOME'
        else:
            raise FileNotFoundError('Home directory not found.')
            
        load_dotenv(os.path.join(os.getenv(home_dir), '.env'))
        
        # Env fallbacks
        self.host = self.host or os.getenv("ORA_HOST")
        self.user = self.user or os.getenv("ORA_USER")
        self.password = self.password or os.getenv("ORA_PASSWORD")
        self.db = self.db or os.getenv("ORA_DB")
        self.port = self.port or os.getenv("ORA_PORT")
        
        self.connection = cx_Oracle.connect(f'{self.user}@{self.host}:{self.port}/{self.db}')
        self.cur = self.connection.cursor()
      
    def get_all_rows(self, column_name):
        self.cur.execute(f"SELECT {column_name} from {self.schema}.{self.table}")
        rows = self.cur.fetchall()
        return rows   
    
    
    def get_user_info(self, user_name, column_name):
        sql = f"SELECT {column_name} FROM {self.schema}.{self.table} WHERE username = :username"
        self.cur.execute(sql, {"username":user_name})
        rows = self.cur.fetchall()
        return rows
 
    
    def close(self):
        self.connection.close()