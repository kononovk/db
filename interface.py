from actions import *
from auth import *
from user import *
from types import Role, UnknownUserException


def yes_no_wait() -> str:
    key = ""
    while True:
        key = str(input())
        if key == "Y" or key == "N":
            break
        else:
            print("Invalid symbol. Please confirm your action\n")

    return key


def order_wait():
    key = ""
    while True:
        key = str(input())
        if key == "0" or key == "1":
            break
        else:
            print("Invalid symbol. Please choose order\n")

    return key


class Interface:
    def __init__(self, conn) -> None:
        self.actions = Actions(conn)
        self.auth = Auth()
        self.current_user = User('default', -1, Role.guest)
        self.run_action = True

    def registration(self):
        while True:
            command = input("1 - sign up\n2 - log in\n3 - exit\n")

            match command:
                case "1":
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    try:
                        role = Role.user
                        self.actions.create_user(username, password, role)
                        print("Registration successful")
                    except UnknownUserException as err:
                        print(err.args[0])
                case "2":
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    try:
                        self.current_user = self.actions.login(username, password)
                        if self.current_user.role == Role.guest:
                            raise UnknownUserException("Unknown user")
                        else:
                            print("Login successful")
                            self.auth.login(self.current_user)
                        break
                    except UnknownUserException as err:
                        print(err.args[0])
                case "3":
                    exit(0)
                case wrong_command:
                    print(f"Unknown command: {wrong_command}")
        self.run_action = True

    def logout(self):
        self.auth.logout()
        self.actions.logout()
        self.current_user = User('default', -1, Role.guest)

    def print_actions(self):
        user_actions = """Choose action:
        1. delete account
        2. create post
        3. view your posts
        4. delete your post
        5. edit your post
        6. check user posts by login
        7. subscribe on user
        8. check subscriptions
        9. check subscribers
        10. check mutual subscriptions 
        11. check all posts from subscriptions
        12. log out"""
        moderator_actions = """Moderation actions:
        13. edit post by id
        14. delete account by login
        15. delete post by id"""
        admin_actions = """Admin actions:
        16. change role by login"""

        print(user_actions)
        if self.current_user.role not in {Role.guest, Role.user}:
            print(moderator_actions)
        if self.current_user.role == Role.admin:
            print(admin_actions)

    def step(self):
        self.print_actions()
        action = input("Choose action: ")

        if self.auth.not_guest():
            try:
                match action:
                    case "1":
                        print("Are you sure you want to delete your account [Y/N]?\n")

                        key = yes_no_wait()

                        if key == "Y":
                            self.actions.delete_account(self.current_user.login)
                            self.logout()
                            self.run_action = False
                    case "2":
                        print("Enter please your post")
                        post = str(input())

                        self.actions.create_post(self.current_user.uid, post)
                    case "3":
                        print("Choose the order new/old, old/new [0/1]: \n")

                        order = order_wait()

                        print("Your posts: \n")
                        posts = self.actions.posts_by_login(self.current_user.login, int(order))

                        for post in posts:
                            print(post)
                            print("\n")

                    case "4":
                        print("Are you sure you want to delete your post [Y/N]?\n")

                        key = yes_no_wait()

                        if key == "Y":
                            print("Enter post id: \n")
                            post_id = int(input())
                            self.actions.delete_post(post_id)

                    case "5":
                        print("Enter post id: \n")
                        post_id = int(input())
                        print("Enter new post: \n")
                        new_post = input()

                        self.actions.change_post(post_id, new_post)
                    case "6":
                        print("Enter user login: \n")
                        user_login = input()

                        print("Choose the order new/old, old/new [0/1]: \n")

                        order = order_wait

                        posts = self.actions.posts_by_login(user_login, int(order))

                        for post in posts:
                            print(post)
                            print("\n")
                    case "7":
                        print("Enter subscription login: \n")
                        sub_login = input()

                        self.actions.subscribe_user(self.current_user.login, sub_login)
                    case "8":
                        subs = self.actions.get_subscriptions(self.current_user.login)

                        for sub in subs:
                            print(sub)
                            print("\n")
                    case "9":
                        subs = self.actions.get_subscribers(self.current_user.login)

                        for sub in subs:
                            print(sub)
                            print("\n")
                    case "10":
                        mut_subs = self.actions.mutual_sub(self.current_user.login)

                        for sub in mut_subs:
                            print(sub)
                            print("\n")
                    case "11":
                        print("Choose the order new/old, old/new [0/1]: \n")
                        order = order_wait()

                        all_posts = self.actions.all_subs_posts(self.current_user.login, int(order))

                        for post in all_posts:
                            print(post)
                            print("\n")
                    case "12":
                        self.logout()
                        self.run_action = False
                    case "13":
                        print("Enter changebel post id: \n")
                        post_id = int(input())
                        print("Enter new post:\n")
                        new_post = input()

                        subject_id = 0

                        if self.auth.moder_request(subject_id):
                            self.actions.change_post(post_id, new_post)
                        else:
                            print("Permission denied")
                    case "14":
                        print("Enter the login of the account you want to delete: \n")
                        login = input()

                        subject_id = 0

                        if self.auth.moder_request(subject_id):
                            self.actions.delete_account(self.current_user.login)
                        else:
                            print("Permission denied")
                    case "15":
                        print("Enter the id of the post you want to delete: \n")
                        post_id = int(input())

                        subject_id = 0

                        if self.auth.moder_request(subject_id):
                            self.actions.delete_post(post_id)
                        else:
                            print("Permission denied")
                    case "16":
                        print("Enter the login of the user you want to change role: \n")
                        login = input()
                        print("Enter new role (user, moderator, admin) [0,1,2]\n")
                        role = input()

                        subject_id = 0

                        if self.auth.admin_request(subject_id):
                            self.actions.change_roll(login, role)
                        else:
                            print("Permission denied")

            except Exception as e:
                print(e.args[0])
        else:
            print("Permission denied")

    def main_loop(self):
        while True:
            self.registration()

            while self.run_action:
                try:
                    self.step()
                except UnknownUserException as e:
                    print(e)
