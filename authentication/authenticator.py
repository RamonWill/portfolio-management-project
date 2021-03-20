from tkinter import messagebox
import bcrypt


class Authenticator(object):
    def __init__(self, db):
        self._db = db

    def validate_login(self, username, password):
        user = self._db.get_user(username)
        if user is None:
            messagebox.showinfo(
                title="Information", message="Invalid username or password"
            )
            return None

        password_bytes = password.encode("utf-8")
        new_key = bcrypt.hashpw(password_bytes, user.salt)
        if bcrypt.hashpw(password_bytes, new_key) == user.salt:
            return user
        else:
            messagebox.showinfo(
                title="Information", message="Invalid username or password"
            )
            return None

    def register_user(
        self, username, password, oanda_account, oanda_api, news_api, alpha_vantage_api
    ):
        if len(password) < 4 or len(username) < 4:
            messagebox.showinfo(
                title="Information",
                message="The username and password must be greater than 3 characters",
            )
            return False

        is_valid_user = self._db.validate_registration(username)

        if is_valid_user:
            hash = self._hash_password(password)
            self._db.store_user_credentials(
                username, hash, oanda_account, oanda_api, news_api, alpha_vantage_api
            )
            messagebox.showinfo(
                title="Information",
                message=f"An account for {username} has now been created.",
            )
            return True
        else:
            messagebox.showinfo(
                title="Information", message="This username already exists"
            )
            return False

    def _hash_password(self, password):
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        key = bcrypt.hashpw(password_bytes, salt)
        hash = {"salt": salt, "key": key}
        return hash
