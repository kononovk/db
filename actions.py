from re import findall
from db_types import Privilege, User


class Actions:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self.user = User.default_user

    # Users
    def create_user(self, login: str, password: str, privilege: Privilege) -> None:
        self.cursor.execute("""INSERT INTO Users (login,password,privilege) 
                        VALUES (%(login)s, crypt(%(password)s, gen_salt('md5')), %(privilege)s);""",
                            {'login': login, 'password': password, 'privilege': str(privilege)})

    def delete_account(self, login: str) -> None:
        self.cursor.execute(
            """
            DELETE FROM Users WHERE login=%(login)s;
            """, {'login': login})

    def login(self, username: str, password: str) -> User:
        query = """SELECT id, privilege
                    FROM users
                    WHERE login = %(login)s
                    AND password = public.crypt(%(password)s, password);"""

        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        self.cursor.execute(query, {'login': username, 'password': password})
        data = self.cursor.fetchone()
        if data:
            uid, privilege = data
            self.user = User(uid, username, Privilege(int(privilege)))
        return self.user

    def logout(self) -> None:
        self.user.login = 'default'
        self.user.privilege = Privilege.guest
        self.user.uid = -1

    # Posts and moderation

    def create_post(self, uid: int, post: str) -> None:
        query = """INSERT INTO posts (user_id, post)
                    VALUES (%(user_id)s, %(post)s);"""
        self.cursor.execute(query, {'user_id': uid, 'post': post})

        self.cursor.execute(
            """
            select post_id from posts where user_id=%(user_id)s
            """, {'user_id': uid})

        post_id, _ = self.cursor.fetchone()
        for ht in findall(r'(#+[a-zA-Z0-9(_)]+)', post):
            self.cursor.execute("""INSERT INTO hashtags (post_id, hashtag) 
                    VALUES (%(post_id)s, %(hashtag)s);""", {'post_id': post_id, 'hashtag': ht})

    def delete_post(self, post_id: int) -> None:
        self.cursor.execute(
            """
            DELETE FROM posts WHERE post_id=%(post_id)s;
            """, {'post_id': post_id})

    def get_user_id_by_post_id(self, post_id: int):
        self.cursor.execute("""
        SELECT user_id FROM posts WHERE post_id=%(post_id)s;
        """, {'post_id': post_id})
        user_id, = self.cursor.fetchone()
        return user_id

    def change_post(self, post_id: int, new_post: str) -> None:
        self.cursor.execute(
            """
            UPDATE posts set post = %(new_post)s WHERE post_id=%(post_id)s;
            """, {'post_id': post_id, 'new_post': new_post})

    def posts_by_login(self, login: str, order_by: int) -> list:
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': login})

        user_id, = self.cursor.fetchone()
        self.cursor.execute(
            f"""
            SELECT time, post FROM Posts WHERE user_id=%(user_id)s ORDER BY time {"DESC" if order_by else "ASC"};""",
            {'user_id': user_id})

        return list(self.cursor.fetchall())

    def all_subs_posts(self, login: str, order_by: int) -> list:
        self.cursor.execute(
            """
            SELECT id FROM Users WHERE login=%(login)s;
            """, {'login': login})

        user_id, _ = self.cursor.fetchone()

        self.cursor.execute(
            f"""
            SELECT time, post 
            FROM Posts 
            WHERE 
                user_id IN (
                    SELECT id_to FROM Subscriptions WHERE id_from=%(user_id)s
                )
            ORDER BY time 
            {"DESC" if order_by else "ASC"};""",
            {'user_id': user_id})

        return list(self.cursor.fetchall())

    def subscribe_user(self, subscriber: str, subscription: str) -> None:
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': subscription})
        subscription_id, _ = self.cursor.fetchone()

        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': subscriber})
        subscriber_id, _ = self.cursor.fetchone()

        self.cursor.execute(
            """
            INSERT INTO subscriptions (id_from, id_to) VALUES(%(id_from)s, %(id_to)s);
            """, {'id_from': subscriber_id, 'id_to': subscription_id})

    def get_subscribers(self, login: str) -> list:
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': login})
        user_id, = self.cursor.fetchone()

        self.cursor.execute(
            """
            SELECT id_from FROM Subscriptions WHERE id_to=%(user_id)s;
            """, {'user_id': user_id})
        subscribers_id = [name for name in self.cursor.fetchall()]

        subscribers = []
        for sub_id in subscribers_id:
            self.cursor.execute("""
                                SELECT login FROM Users WHERE id=%(id)s 
                                """, {'id': sub_id})

            subscribers.append(self.cursor.fetchone()[0])
        return subscribers

    def get_subscriptions(self, login: str) -> list:
        self.cursor.execute(
            """
            SELECT id FROM Users WHERE login=%(login)s;
            """, {'login': login})
        user_id, = self.cursor.fetchone()

        self.cursor.execute(
            """
            SELECT id_to FROM Subscriptions WHERE id_from=%(user_id)s;
            """, {'user_id': user_id})

        subscriptions_id = [name for name, in self.cursor.fetchall()]

        subscriptions = []
        for sub_id in subscriptions_id:
            self.cursor.execute("""
                                SELECT login FROM Users WHERE id=%(id)s 
                                """, {'id': sub_id})

            subscriptions.append(self.cursor.fetchone()[0])
        return subscriptions

    def mutual_sub(self, login: str) -> list:
        self.cursor.execute(
            """
            SELECT id FROM Users WHERE login=%(login)s;
            """, {'login': login})

        user_id, = self.cursor.fetchone()
        self.cursor.execute(
            """
            SELECT id_from
            FROM Subscriptions
            WHERE
                id_to=%(user_id)s AND
                
                id_from IN (
                    SELECT id_to 
                    FROM Subscriptions 
                    WHERE 
                        id_from=%(user_id)s
                );
            """, {'user_id': user_id})

        subs = self.cursor.fetchall()
        mut_subs = []
        for sub_id, _ in subs:
            self.cursor.execute(
                """
                SELECT login 
                FROM Users
                WHERE id=%(user_id)s;
                """, {'user_id': sub_id})
            value, = self.cursor.fetchone()
            mut_subs.append(value)

        return mut_subs

    def change_roll(self, login: str, privilege: Privilege) -> None:
        self.cursor.execute(
            """
            SELECT id FROM Users WHERE login=%(login)s;
            """, {'login': login})

        user_id, _ = self.cursor.fetchone()

        self.cursor.execute(
            """
            UPDATE Users set privilege=%(new_privilege)s WHERE id=%(user_id)s;
            """, {'user_id': user_id, 'new_privilege': privilege})
