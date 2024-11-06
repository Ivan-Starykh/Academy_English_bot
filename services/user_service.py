import os

USERS_FILE = 'users.txt'

def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, 'r') as file:
        users = {line.strip() for line in file}
    return users

def save_user(user_id):
    with open(USERS_FILE, 'a') as file:
        file.write(f"{user_id}\n")
