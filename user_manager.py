from user import User

class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, user: User):
        self.users[user.id] = user

    def get_user(self, user_id: int):
        return self.users.get(user_id, None)

    def check_user_exist(self, user_id: int):
        return user_id in self.users
    
    def get_users(self):
        return self.users.values()
