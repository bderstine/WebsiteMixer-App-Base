from flask_login import LoginManager
from websitemixer.models import User

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
