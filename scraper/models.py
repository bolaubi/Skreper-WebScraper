from scraper import bcrypt, login_manager, dbs
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(dbs.Model, UserMixin):
    __tablename__ = 'user_data'
    id = dbs.Column(dbs.Integer(), primary_key=True)
    email = dbs.Column(dbs.String(length=50), nullable=False, unique=True)
    username = dbs.Column(dbs.String(length=30), nullable=False, unique=True)
    password_hash = dbs.Column(dbs.String(length=60), nullable=False)

    # safe register
    @property
    def password(self):
        return self.password
    @password.setter
    def password(self, unformatted_password):
        self.password_hash = bcrypt.generate_password_hash(unformatted_password).decode('utf-8')

    # safe login
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)