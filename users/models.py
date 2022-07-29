# -------------- ALLOW SELF EXECUTE --------------- #
import os, sys
sys.path.append(os.getcwd())


# ------------------ IMPORTING -------------------- #
import datetime
import requests

from extensions import db


# -------------------- MODELS --------------------- #

# -------------------- USERS --------------------- #
class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(255), unique=True, nullable=False, default='')
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    main_page = db.Column(db.String(255), default='/latest_updates')
    theme = db.Column(db.String(255), default='light')

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.username = self.randomUsername()

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
            'user_id': self.id,
            'user_active': self.active,
            'user_username': self.username,
            'user_email': self.email,
            'user_created_at': self.created_at,
            'user_updated_at': self.updated_at,
            'user_main_page': self.main_page,
            'user_theme': self.theme
        }




# -------------------- HISTORY --------------------- #
history_fk_chapter = db.Table('history_fk_chapter',
    db.Column('history_id', db.Integer, db.ForeignKey('history.id')),
    db.Column('chapter_id', db.Integer, db.ForeignKey('chapters.id'))
)


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    # -- relationships -- #
    # user = db.relationship('Users', backref=db.backref('history', lazy='dynamic'))
    # manga = db.relationship('Mangas', backref=db.backref('history', lazy='dynamic'))
    # chapters = db.relationship('Chapters', secondary=history_fk_chapter, backref='history', lazy='dynamic')

    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id

    def __repr__(self):
        return '<History %r>' % self.id

    def serialize(self):
        return {
            'history_id': self.id,
            'history_user_id': self.user_id,
            'history_manga_id': self.manga_id,
            'history_created_at': self.created_at,
            'history_updated_at': self.updated_at
        }




# -------------------- FAVORITES --------------------- #
class Favorites(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    # -- relationships -- #
    # user = db.relationship('Users', backref=db.backref('favorites', lazy='dynamic'))
    # manga = db.relationship('Mangas', backref=db.backref('favorites', lazy='dynamic'))

    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id

    def __repr__(self):
        return '<Favorite %r>' % self.id

    def serialize(self):
        return {
            'favorites_id': self.id,
            'favorites_user_id': self.user_id,
            'favorites_manga_id': self.manga_id,
            'favorites_updated_at': self.updated_at
        }





# -------------------- RATINGS --------------------- #
class Ratings(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    # -- relationships -- #
    # user = db.relationship('Users', backref=db.backref('ratings', lazy='dynamic'))
    # manga = db.relationship('Mangas', backref=db.backref('ratings', lazy='dynamic'))

    def __init__(self, user_id, manga_id, rating):
        self.user_id = user_id
        self.manga_id = manga_id
        self.rating = rating

    def __repr__(self):
        return '<Rating %r>' % self.id

    def serialize(self):
        return {
            'ratings_id': self.id,
            'ratings_user_id': self.user_id,
            'ratings_manga_id': self.manga_id,
            'ratings_rating': self.rating,
            'ratings_created_at': self.created_at,
            'ratings_updated_at': self.updated_at
        }    



if __name__ == '__main__':
    print(Users.query.first().serialize())