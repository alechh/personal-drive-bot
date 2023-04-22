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
            raise Exception("Failed to connect to database on {}:{}".format(self.host, self.port))

    def disconnect(self):
        try:
            self.connection.close()
        except Exception:
            print("Failed to disconnect from  database on {}:{}".format(self.host, self.port))

    def execute(self, query, params=None):
        try:
            cur = self.connection.cursor()
            cur.execute(query, params)
            self.connection.commit()
            if 'SELECT' in query:
                return cur.fetchall()
        except Exception as e:
            raise Exception("Failed to execute query: {}: {}".format(query, e))

    def make_backup(self, query, backup_file):
        try:
            cur = self.connection.cursor()
            cur.copy_expert(query, backup_file)
            if 'SELECT' in query:
                return cur.fetchall()
        except:
            raise Exception("Failed to execute query: {}".format(query))

    def restore_backup(self, query, backup_file):
        try:
            cur = self.connection.cursor()
            cur.copy_expert(query, backup_file)
            self.connection.commit()
            if 'SELECT' in query:
                return cur.fetchall()
        except Exception:
            raise Exception("Failed to restore: {}".format(query))

