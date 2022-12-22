class UnknownUserException(Exception):
    pass


class MyException(Exception):
    pass


class Role:
    guest = -1
    user = 0
    moder = 1
    admin = 2

    def __init__(self, value):
        if value not in {Role.guest, Role.user, Role.moder, Role.admin}:
            raise "Incorrect enum value"
        self.value = value

    def __str__(self):
        return str(self.value)


class User:
    def __init__(self, uid, login, role) -> None:
        self.login = login
        self.uid = uid
        self.role = role
