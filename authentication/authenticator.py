import hashlib
import os
from tkinter import messagebox
# Hash source from https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
# Make sure you do not store the password as that is the goal of all of this, not having to store the actual password.


class Authenticator(object):
    def __init__(self, db):
        self._db = db

    def validate_login(self, username, password):
        user = self._db.get_user(username)
        if user is None:
            messagebox.showinfo(title="Information", message="Invalid username or password")
            return None
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), user.salt, 100000)
        if user.key == new_key:
            return user
        else:
            messagebox.showinfo(title="Information", message="Invalid username or password")
            return None

    def register_user(self, username, password, oanda_account, oanda_api, news_api, alpha_vantage_api):
        if len(password)<5 or len(username)<5:
            messagebox.showinfo(title="Information", message="The username and password must be greater than 4 characters")
            return False

        is_valid_user = self._db.validate_registration(username)

        if is_valid_user:
            hash = self._hash_password(password)
            self._db.store_user_credentials(username, hash, oanda_account, oanda_api, news_api, alpha_vantage_api)
            messagebox.showinfo(title="Information", message=f"An account for {username} has now been created.")
            return True
        else:
            messagebox.showinfo(title="Information", message="This username already exists")
            return False


    def _hash_password(self, password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        hash = {"salt":salt, "key":key}
        return hash