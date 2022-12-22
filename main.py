from interface import Interface
from database import Database


if __name__ == '__main__':
    db = Database("test_db")
    interface = Interface(db.conn)
    interface.main_loop()
