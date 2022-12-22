from db_types import Privilege, User


class Auth:
    def __init__(self):
        self.user = User.default_user

    def uid(self) -> int:
        return self.user.uid

    def login(self, user: User):
        self.user = user

    def logout(self):
        self.user = User.default_user

    def registered(self) -> bool:
        return self.user.privilege != Privilege.guest

    def has_moder_permissions(self):
        return self.user.privilege == Privilege.moder and self.user.privilege == Privilege.admin

    def has_admin_permissions(self) -> bool:
        return self.user.privilege == Privilege.admin
