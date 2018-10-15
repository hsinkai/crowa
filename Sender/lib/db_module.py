import sys
import os
import time
import MySQLdb

class db_module() :
    
    def __init__(self, host, database, login_id, password) :
        
        self.host = host
        self.database = database
        self.login_id = login_id
        self.password = password
        
    def connect(self) : 
        
        self.db = MySQLdb.connect(self.host, self.login_id, self.password, self.database )
        self.cursor = self.db.cursor()
    
    def get_all_content(self, table) :
        
        self.connect()
        sql = 'SELECT * FROM %s' % table
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        self.db.close()
        return results

    def get_raw_number(self, table) :
        
        self.connect()
        sql = 'SELECT COUNT(*) FROM %s' % table
        self.cursor.execute(sql)
        results = self.cursor.fetchone()
        self.db.close()
        return  results[0]
          
    def db_read(self, cmd) :
        
        self.connect()
        self.cursor.execute(cmd)
        results = self.cursor.fetchall()
        self.db.close()
        return results
    
    def db_write(self, cmd) :
        
        self.connect()
        self.cursor.execute(cmd)
        self.db.commit()
        results = self.cursor.lastrowid
        self.db.close()
        self.cursor.close()
        return results