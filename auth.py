from user import *
from types import Role, UnknownUserException


class Auth:
    def __init__(self):
        self.user = User('default', -1, Role.guest)

    def uid(self) -> int:
        return self.user.uid

    def login(self, u: User):
        self.user = u

    def logout(self):
        self.user.login = 'default'
        self.user.uid = -1
        self.user.role = str(Role.guest)

    def not_guest(self) -> bool:
        return self.user.role != Role.guest

    def moder_request(self, subject_id: int) -> bool:
        return (self.user.role == Role.moder and self.user.role == Role.admin) or self.user.uid == subject_id

    def admin_request(self, subject_id: int) -> bool:
        return self.user.role == Role.admin and self.user.uid != subject_id
