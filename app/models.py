from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True, index=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    folders = db.relationship('Folder', backref='user', lazy=True)
    articles = db.relationship('Article', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, salt_length=32)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Folder(db.Model):
    __tablename__ = 'folders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    articles = db.relationship('Article', backref='folder', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Folder(id={self.id}, name={self.name}, user_id={self.user_id})>"

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(500))
    author = db.Column(db.String(200))
    date = db.Column(db.String(100))
    summary = db.Column(db.Text, nullable=False)
    senti_score = db.Column(db.Float, nullable=False)
    senti_label = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=False)

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title}, user_id={self.user_id}, folder_id={self.folder_id})>"






