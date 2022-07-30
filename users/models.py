# -------------- ALLOW SELF EXECUTE --------------- #
import os, sys
sys.path.append(os.getcwd())


# ------------------ IMPORTING -------------------- #
import datetime
import requests

from extensions import db
from tools.tools import BehaviorStructure

from manga.models import Sources, Mangas, Authors, Genres, Chapters

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

    # -- relationships -- #
    favorites = db.relationship('Favorites', backref='user', lazy='dynamic')
    history = db.relationship('History', backref='user', lazy='dynamic')
    ratings = db.relationship('Ratings', backref='user', lazy='dynamic')

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

    def __name__(self):
        return 'User'

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

class UserBehavior(BehaviorStructure):
    def __init__(self, email, password=None):
        self.email = email
        self.password = password

        self.every_field = [self.email, self.password]
        self.object = Users
        self.primary_identifier = [self.object.email==self.email]

    def update(self):
        if self.check_all_fields() and self.read() is not None:
            user = self.read()
            user.email = self.email
            user.password = self.password
            db.session.commit()
            return user

        elif not self.check_all_fields():
            raise Exception(f'Missing fields in order to update a {self.object.__name__}')

        else:
            raise Exception(f'{self.object.__name__} does not exist')




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

    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id

    def __repr__(self):
        return '<History %r>' % self.id

    def __name__(self):
        return 'History'

    def serialize(self):
        return {
            'history_id': self.id,
            'history_user_id': self.user_id,
            'history_manga_id': self.manga_id,
            'history_created_at': self.created_at,
            'history_updated_at': self.updated_at
        }

class HistoryBehavior(BehaviorStructure):
    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id

        self.every_field = [self.user_id, self.manga_id]
        self.object = History
        self.primary_identifier = [self.object.user_id==self.user_id, self.object.manga_id==self.manga_id]

    def update(self):
        if self.check_all_fields() and self.read() is not None:
            history = self.read()
            history.user_id = self.user_id
            history.manga_id = self.manga_id
            db.session.commit()
            return history

        elif not self.check_all_fields():
            raise Exception(f'Missing fields in order to update a {self.object.__name__}')

        else:
            raise Exception(f'{self.object.__name__} does not exist')
        
    def delete(self):
        if self.check_all_fields() and self.read() is not None:
            history = self.read()
            history.chapters = []
            db.session.commit()
            return history
        super().delete()

    # -- Generic Behavior -- #
    def get_readed_chapters(self):
        if self.check_all_fields() and self.read() is not None:
            return self.read().chapters
        else:
            raise Exception(f'{self.object.__name__} does not exist')
            
    def add_readed_chapter(self, chapter_slug):
        chapter = Chapters.query.filter_by(slug=chapter_slug).first()

        if self.check_all_fields() and chapter is not None and self.read() is not None:
            history = self.read()
            history.chapters.append(chapter)
            db.session.commit()
            return history

        elif not self.check_all_fields():
            raise Exception(f'Missing fields in order to update a {self.object.__name__}')

        elif chapter is None:
            raise Exception(f'Chapter {chapter_slug} does not exist')

        else:
            raise Exception(f'{self.object.__name__} does not exist')

    def remove_readed_chapter(self, chapter_slug):
        chapter = Chapters.query.filter_by(slug=chapter_slug).first()

        if self.check_all_fields() and chapter is not None and self.read() is not None:
            history = self.read()
            history.chapters.remove(chapter)
            db.session.commit()
            return history

        elif not self.check_all_fields():
            raise Exception(f'Missing fields in order to update a {self.object.__name__}')

        elif chapter is None:
            raise Exception(f'Chapter {chapter_slug} does not exist')

        else:
            raise Exception(f'{self.object.__name__} does not exist')

    def add_all_chapters(self):
        if self.check_all_fields() and self.read() is not None:
            history = self.read()
            history.chapters = []
            for chapter in Mangas.query.filter_by(id=self.manga_id).first().chapters:
                history.chapters.append(chapter)
            db.session.commit()
            return history

        elif not self.check_all_fields():
            raise Exception(f'Missing fields in order to update a {self.object.__name__}')

        else:
            raise Exception(f'{self.object.__name__} does not exist')

    def remove_all_chapters(self):
        if self.check_all_fields() and self.read() is not None:
            history = self.read()
            history.chapters = []
            db.session.commit()
            return history

        elif not self.check_all_fields():
            raise Exception(f'Missing fields in order to update a {self.object.__name__}')

        else:
            raise Exception(f'{self.object.__name__} does not exist')





# -------------------- FAVORITES --------------------- #
class Favorites(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, user_id, manga_id):
        self.user_id = user_id
        self.manga_id = manga_id

    def __repr__(self):
        return '<Favorite %r>' % self.id

    def __name__(self):
        return 'Favorite'

    def serialize(self):
        return {
            'favorites_id': self.id,
            'favorites_user_id': self.user_id,
            'favorites_manga_id': self.manga_id,
            'favorites_created_at': self.created_at
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

    def __init__(self, user_id, manga_id, rating):
        self.user_id = user_id
        self.manga_id = manga_id
        self.rating = rating

    def __repr__(self):
        return '<Rating %r>' % self.id

    def __name__(self):
        return 'Rating'

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
    user = UserBehavior('admin@admin.com')
    print(user.read())