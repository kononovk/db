import psycopg2


class Database:
    def __init__(self, db_name) -> None:
        self.name = db_name
        self.cursor = None
        self.conn = self.__try_connect(db_name, autocommit=True)
        self.cursor = self.conn.cursor()

    @staticmethod
    def __try_connect(db_name, *, autocommit):
        try:
            conn = psycopg2.connect(dbname=db_name, host="localhost", port=5432)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Database connection failed: {error}")
            raise error
        conn.autocommit = autocommit
        return conn
