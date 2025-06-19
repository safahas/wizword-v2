import json
import os
import bcrypt
from typing import Optional

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

# Helper to load all users
def load_all_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Helper to save all users
def save_all_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

# Register a new user
def register_user(email: str, username: str, password: str) -> Optional[str]:
    email = email.strip().lower()
    users = load_all_users()
    if any(u['email'] == email for u in users):
        return 'Email already registered.'
    if any(u['username'].lower() == username.lower() for u in users):
        return 'Username already taken.'
    if len(password) < 6:
        return 'Password must be at least 6 characters.'
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users.append({
        'email': email,
        'username': username,
        'password_hash': password_hash
    })
    save_all_users(users)
    return None  # Success

# Login user
def login_user(email: str, password: str) -> Optional[dict]:
    email = email.strip().lower()
    users = load_all_users()
    for user in users:
        if user['email'] == email:
            if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
                return user
            else:
                return None
    return None

# Load user profile by email
def load_user_profile(email: str) -> Optional[dict]:
    users = load_all_users()
    for user in users:
        if user['email'] == email:
            return user
    return None 