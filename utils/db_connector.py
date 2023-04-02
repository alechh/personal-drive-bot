import psycopg2

class DB_Connector:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = self.connect()
    
    def __del__(self):
        self.disconnect()

    def connect(self):
        try:
            conn = psycopg2.connect(host=self.host, port=self.port, 
                                database=self.database, user=self.user, 
                                password=self.password)
            return conn
        except:
            print("Failed to connect to database on {}:{}".format(self.host, self.port))

    def disconnect(self):
        try:
            self.connection.close()
        except:
            print("Failed to disconnect from  database on {}:{}".format(self.host, self.port))

    def execute(self, query, params=None):
        try:
            cur = self.connection.cursor()
            cur.execute(query, params)
            self.connection.commit()
            return cur.fetchall()
        except:
            print("Failed to execute query")
            return []
