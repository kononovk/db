from user import User
import re
from types import Role, MyException


class Actions:
    def __init__(self, conn) -> None:
        self.conn = conn
        self.cursor = conn.cursor()
        self.user = User('default', -1, Role.guest)

    # Users
    def create_user(self, login: str, password: str, role: Role) -> None:
        try:
            self.cursor.execute("""INSERT INTO Users (login,password,role) 
                        VALUES (%(login)s, crypt(%(password)s, gen_salt('md5')), %(role)s);""",
                                {'login': login, 'password': password, 'role': str(role)})
        except Exception:
            raise MyException("internal create_user DB error")

    def delete_account(self, uid: int) -> None:
        try:
            self.cursor.execute(
                """
                DELETE FROM user WHERE user_id=%(user_id)s;
                """, {'user_id': uid})
        except Exception:
            raise MyException("internal delete_account DB error")

    def login(self, username: str, password: str) -> User:
        query = """SELECT id, role
                    FROM users
                    WHERE login = %(login)s
                    AND password = public.crypt(%(password)s, password);"""

        try:
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
            self.cursor.execute(query, {'login': username, 'password': password})
        except Exception:
            raise MyException("internal login DB error")

        data = self.cursor.fetchone()

        if data:
            uid, role = data

            self.user = User(uid, username, Role(int(role)))

        return self.user

    def logout(self) -> None:
        self.user.login = 'default'
        self.user.role = Role.guest
        self.user.uid = -1

    # Posts and moderation

    def create_post(self, uid: int, post: str) -> None:
        query = """INSERT INTO posts (user_id, post)
                    VALUES (%(user_id)s, %(post)s);"""

        try:
            self.cursor.execute(query, {'user_id': uid, 'post': post})
        except Exception:
            raise MyException("internal create_post DB error")

        ht_query = """INSERT INTO hashtags (post_id, hashtag) 
                    VALUES (%(post_id)s, %(hashtag)s);"""

        try:
            self.cursor.execute(
                """
                select post_id from posts where user_id=%(user_id)s
                """, {'user_id': uid})
        except Exception:
            raise MyException("internal create_post post selection DB error")

        post_id, = self.cursor.fetchone()

        hashtags = re.findall(r'(#+[a-zA-Z0-9(_)]+)', post)

        try:
            for ht in hashtags:
                self.cursor.execute(ht_query, {'post_id': post_id, 'hashtag': ht})
        except Exception:
            raise MyException("internal create_post hashtags DB error")

    def delete_post(self, post_id: int) -> None:
        try:
            self.cursor.execute(
                """
                DELETE FROM posts WHERE post_id=%(post_id)s;
                """, {'post_id': post_id})
        except Exception:
            raise MyException("internal delete_post DB error")

    def change_post(self, post_id: int, new_post: str) -> None:
        try:
            self.cursor.execute(
                """
                UPDATE posts set post = %(new_post)s WHERE post_id=%(post_id)s;
                """, {'post_id': post_id, 'new_post': new_post})
        except Exception:
            raise MyException("internal change_post DB error")

    def posts_by_login(self, login: str, order_by: int) -> list:
        try:
            self.cursor.execute(
                """
                SELECT id FROM users WHERE login=%(login)s;
                """, {'login': login})
        except Exception:
            raise MyException("internal posts_by_login id selection DB error")

        user_id, = self.cursor.fetchone()

        order = "DESC" if order_by else "ASC"

        try:
            self.cursor.execute(
                """
                SELECT time, post FROM posts WHERE user_id=%(user_id)s ORDER BY time """ + order,
                {'user_id': user_id})
        except Exception:
            raise MyException("internal posts_by_login DB error")

        date_posts = list(self.cursor.fetchall())

        return date_posts

    def all_subs_posts(self, login: str, order_by: int) -> list:
        date_posts = []

        order = "DESC;" if order_by else "ASC;"

        try:
            self.cursor.execute(
                """
                SELECT id FROM users WHERE login=%(login)s;
                """, {'login': login})
        except Exception:
            raise MyException("internal all_subs_posts id selection DB error")

        user_id, = self.cursor.fetchone()

        try:
            self.cursor.execute(
                """
                SELECT time, post 
                FROM posts 
                WHERE 
                    user_id IN (
                        SELECT id_to FROM Subscriptions WHERE id_from=%(user_id)s
                    )
                ORDER BY time 
                """ + order,
                {'user_id': user_id})
        except Exception:
            raise MyException("internal all_subs_posts DB error")

        date_posts.append(self.cursor.fetchall())

        return date_posts

    # Subscriptions

    def subscribe_user(self, subscriber: str, subscription: str) -> None:
        try:
            self.cursor.execute(
                """
                SELECT id FROM users WHERE login=%(login)s;
                """, {'login': subscription})

        except Exception:
            raise MyException("internal subscribe_user id selection DB error")

        subscription_id, = self.cursor.fetchone()

        try:
            self.cursor.execute(
                """
                SELECT id FROM users WHERE login=%(login)s;
                """, {'login': subscriber})

        except Exception:
            raise MyException("internal subscribe_user subscriber id selection DB error")

        subscriber_id, = self.cursor.fetchone()

        self.cursor.execute(
            """
            INSERT INTO subscriptions (id_from, id_to) VALUES(%(id_from)s, %(id_to)s);
            """, {'id_from': subscriber_id, 'id_to': subscription_id})

        try:
            self.cursor.execute(
                """
                INSERT INTO subscriptions (id_from, id_to) VALUES(%(id_from)s, %(id_to)s);
                """, {'id_from': subscriber_id, 'id_to': subscription_id})
        except Exception:
            raise MyException("internal subscribe_user DB error")

    def get_subscribers(self, login: str) -> list:
        try:
            self.cursor.execute(
                """
                SELECT id FROM users WHERE login=%(login)s;
                """, {'login': login})
        except Exception:
            raise MyException("internal get_subscribers id selection DB error")

        user_id, = self.cursor.fetchone()

        try:
            self.cursor.execute(
                """
                SELECT id_from FROM Subscriptions WHERE id_to=%(user_id)s;
                """, {'user_id': user_id})

        except Exception:
            raise MyException("internal get_subscribers subs id selection DB error")

        subscribers_id = [name for name, in self.cursor.fetchall()]

        subscribers = []

        try:
            for sub_id in subscribers_id:
                self.cursor.execute("""
                                    SELECT login FROM Users WHERE id=%(id)s 
                                    """, {'id': sub_id})

                subscribers.append(self.cursor.fetchone()[0])

        except Exception:
            raise MyException("internal get_subscribers DB error")

        return subscribers

    def get_Subscriptions(self, login: str) -> list:
        try:
            self.cursor.execute(
                """
                SELECT id FROM Users WHERE login=%(login)s;
                """, {'login': login})
        except Exception:
            raise MyException("internal get_subscriptions id selection DB error")

        user_id, = self.cursor.fetchone()

        try:
            self.cursor.execute(
                """
                SELECT id_to FROM Subscriptions WHERE id_from=%(user_id)s;
                """, {'user_id': user_id})

        except Exception:
            raise MyException("internal get_subscriptions subscriptions id selection DB error")

        subscriptions_id = [name for name, in self.cursor.fetchall()]

        subscriptions = []

        try:
            for sub_id in subscriptions_id:
                self.cursor.execute("""
                                    SELECT login FROM Users WHERE id=%(id)s 
                                    """, {'id': sub_id})

                subscriptions.append(self.cursor.fetchone()[0])

        except Exception:
            raise MyException("internal get_subscriptions DB error")

        return subscriptions

    def mutual_sub(self, login: str) -> list:
        try:
            self.cursor.execute(
                """
                SELECT id FROM Users WHERE login=%(login)s;
                """, {'login': login})

        except Exception:
            raise MyException("internal mutual_sub id selection DB error")

        user_id, = self.cursor.fetchone()

        try:
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
        except Exception:
            raise MyException("internal mutual_sub DB error")

        subs = self.cursor.fetchall()

        mut_subs = []

        for id, in subs:
            self.cursor.execute(
                """
                SELECT login 
                FROM Users
                WHERE id=%(user_id)s;
                """, {'user_id': id})

            value, = self.cursor.fetchone()
            mut_subs.append(value)

        return mut_subs

    # Administration

    def change_roll(self, login: str, role: Role) -> None:
        try:
            self.cursor.execute(
                """
                SELECT id FROM Users WHERE login=%(login)s;
                """, {'login': login})

        except Exception as e:
            raise MyException("internal change_roll id selection DB error")

        user_id, = self.cursor.fetchone()

        try:
            self.cursor.execute(
                """
                UPDATE Users set role=%(new_role)s WHERE id=%(user_id)s;
                """, {'user_id': user_id, 'new_role': role})
        except Exception:
            raise MyException("internal change_roll DB error")
