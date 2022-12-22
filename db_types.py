class UnknownUserException(Exception):
    pass


class Privilege:
    guest = -1
    user = 0
    moder = 1
    admin = 2

    def __init__(self, value):
        if value not in {Privilege.guest, Privilege.user, Privilege.moder, Privilege.admin}:
            raise "Incorrect enum value"
        self.value = value

    def __str__(self):
        return str(self.value)


class User:
    def __init__(self, uid, login, privilege):
        self.login = login
        self.uid = uid
        self.privilege = privilege

    @property
    def default_user(self):
        return User(None, None, Privilege.guest)
