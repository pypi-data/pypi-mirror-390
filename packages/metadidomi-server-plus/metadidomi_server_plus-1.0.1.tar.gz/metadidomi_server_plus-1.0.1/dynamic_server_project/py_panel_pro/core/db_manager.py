import mysql.connector
from mysql.connector import errorcode

class MySQLManager:
    def __init__(self, host='127.0.0.1', port=3306, user='root', password=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.password)
            return True, ''
        except mysql.connector.Error as err:
            return False, str(err)

    def list_databases(self):
        cur = self.conn.cursor()
        cur.execute('SHOW DATABASES')
        return [row[0] for row in cur.fetchall()]

    def list_tables(self, db):
        cur = self.conn.cursor()
        cur.execute(f"USE `{db}`")
        cur.execute('SHOW TABLES')
        return [row[0] for row in cur.fetchall()]

    def fetch_rows(self, db, table, limit=100):
        cur = self.conn.cursor(dictionary=True)
        cur.execute(f"USE `{db}`")
        cur.execute(f"SELECT * FROM `{table}` LIMIT {limit}")
        return cur.fetchall()
