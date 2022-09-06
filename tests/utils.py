from models import User

from manager import get_database

db = get_database()

def create_user(user_id: str):
    # create user in DB
    return User.create(user_id=user_id)