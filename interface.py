from actions import Actions
from auth import Auth
from db_types import Privilege, UnknownUserException, User


class Interface:
    def __init__(self, conn) -> None:
        self.actions = Actions(conn)
        self.auth = Auth()
        self.current_user = User(None, None, Privilege.guest)
        self.run_action = True

    def registration(self):
        while True:
            command = input("1 - sign up\n2 - log in\n3 - exit\n")

            match command:
                case "1":
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    privilege = Privilege.user
                    self.actions.create_user(username, password, privilege)
                    print("Registration successful")
                    break
                case "2":
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    self.current_user = self.actions.login(username, password)
                    if self.current_user.privilege == Privilege.guest:
                        raise UnknownUserException("Unknown user")
                    else:
                        print("Login successful")
                        self.auth.login(self.current_user)
                    break
                case "3":
                    exit(0)
                case wrong_command:
                    print(f"Unknown command: {wrong_command}")
        self.run_action = True

    def logout(self):
        self.auth.logout()
        self.actions.logout()
        self.current_user = User.default_user

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
        16. change privilege by login"""

        print(user_actions)
        if self.current_user.privilege in {Privilege.moder, Privilege.admin}:
            print(moderator_actions)
        if self.current_user.privilege == Privilege.admin:
            print(admin_actions)

    def step(self):
        self.print_actions()
        action = input("Choose action: ")

        if self.auth.registered():
            self.try_to_do_action(action)
        else:
            print("Permission denied")

    @staticmethod
    def confirm_action(what_confirm) -> bool:
        while True:
            key = input(f"Are you sure you want to {what_confirm} [Y/N]: ")
            if key == "Y":
                return True
            elif key == "N":
                return False
            else:
                print("Invalid symbol. Please confirm your action\n")

    @staticmethod
    def get_order():
        while True:
            key = input()
            if key == "0" or key == "1":
                return int(key)
            print("Invalid symbol. Please choose order\n")

    def try_to_do_action(self, action):
        match action:
            case "1":
                if self.confirm_action('delete your account'):
                    self.actions.delete_account(self.current_user.login)
                    self.logout()
                    self.run_action = False
            case "2":
                post = input('Enter post:\n')
                self.actions.create_post(self.current_user.uid, post)
            case "3":
                print("Choose the order\n1 - from new to old\n2 - from old to new\n")
                print("Your posts: \n")
                for post in self.actions.posts_by_login(self.current_user.login, self.get_order()):
                    print(post)
            case "4":
                if self.confirm_action('delete your post'):
                    post_id = int(input('Enter post id: '))
                    self.actions.delete_post(post_id)
            case "5":
                post_id = int(input('Enter post id: '))
                new_post = input('Enter new post: \n')
                if self.current_user.uid == post_id:
                    self.actions.change_post(post_id, new_post)
                else:
                    print("Permission deny")
            case "6":
                user_login = input('Enter user login: ')
                print("Choose the order\n1 - from new to old\n2 - from old to new\n")
                for post in self.actions.posts_by_login(user_login, self.get_order()):
                    print(post)
            case "7":
                sub_login = input('Enter user\'s login you want to subscribe to: ')
                self.actions.subscribe_user(self.current_user.login, sub_login)
            case "8":
                for sub in self.actions.get_subscriptions(self.current_user.login):
                    print(sub)
            case "9":
                for sub in self.actions.get_subscribers(self.current_user.login):
                    print(sub)
            case "10":
                for sub in self.actions.mutual_sub(self.current_user.login):
                    print(sub)
            case "11":
                print("Choose the order\n1 - from new to old\n2 - from old to new\n")
                for post in self.actions.all_subs_posts(self.current_user.login, self.get_order()):
                    print(post)
            case "12":
                self.logout()
                self.run_action = False
            case "13":
                post_id = int(input('Enter post id you want to change: '))
                new_post = input('Enter new post: ')

                if self.auth.has_moder_permissions():
                    self.actions.change_post(post_id, new_post)
                else:
                    print("Permission denied")
            case "14":
                login = input('Enter the login of the account you want to delete: ')
                if self.auth.has_moder_permissions():
                    self.actions.delete_account(login)
                else:
                    print("Permission denied")
            case "15":
                post_id = int(input("Enter the id of the post you want to delete: "))
                if self.auth.has_moder_permissions():
                    self.actions.delete_post(post_id)
                else:
                    print("Permission denied")
            case "16":
                login = input("Enter the login of the user you want to change privilege: ")
                privilege = Privilege(int(input('Enter new privilege (user, moderator, admin) [0,1,2]: ')))
                if self.auth.has_admin_permissions():
                    self.actions.change_roll(login, privilege)
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
                    raise e
