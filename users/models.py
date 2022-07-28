# ------------------ IMPORTING -------------------- #
import datetime
import requests

from extensions import db


# -------------------- MODELS --------------------- #

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False, default='')
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    main_page = db.Column(db.String(255), default='/latest_updates')
    history = db.relationship('History', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorites', backref='user', lazy='dynamic')
    ratings = db.relationship('Ratings', backref='user', lazy='dynamic')
    theme = db.Column(db.String(255), default='light')

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.username = self.randomUsername()
        self.main_page = '/latest_updates'

    def randomUsername(self):
        output = [
            requests.get('https://random-word-api.herokuapp.com/word').json(),
            requests.get('https://random-word-api.herokuapp.com/word').json(),
            requests.get('https://random-word-api.herokuapp.com/word').json(),
        ]
        return ''.join([x[0].capitalize() for x in output])

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'main_page': self.main_page
        }

    
class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, manga_id, chapter_id):
        self.user_id = user_id
        self.manga_id = manga_id
        self.chapter_id = chapter_id
        self.updated_at = datetime.datetime.now()

    def __repr__(self):
        return '<History %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'manga_id': self.manga_id,
            'chapter_id': self.chapter_id,
            'updated_at': self.updated_at
        }


class Favorites(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id
        self.updated_at = datetime.datetime.now()

    def __repr__(self):
        return '<Favorite %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'manga_id': self.manga_id,
            'updated_at': self.updated_at
        }


class Ratings(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, manga_id, rating):
        self.user_id = user_id
        self.manga_id = manga_id
        self.rating = rating
        self.updated_at = datetime.datetime.now()

    def __repr__(self):
        return '<Rating %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'manga_id': self.manga_id,
            'rating': self.rating,
            'updated_at': self.updated_at
        }    