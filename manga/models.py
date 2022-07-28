# -------------- ALLOW SELF EXECUTE --------------- #
import os, sys
sys.path.append(os.getcwd())


# ------------------ IMPORTING -------------------- #
import datetime

from extensions import db

# -------------------- MODELS --------------------- #



# ------- SOURCES -------- #
class Sources(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), unique=True, nullable=False)
    source_slug = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, source, source_slug, language, url):
        self.source = source
        self.source_slug = source_slug
        self.language = language
        self.url = url

    def __repr__(self):
        return f'<Source {self.name}>'



# ------- MANGAS -------- #
mangas_authors = db.Table('mangas_authors',
    db.Column('manga_id', db.Integer, db.ForeignKey('mangas.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'), primary_key=True)
)

mangas_genres = db.Table('mangas_genres',
    db.Column('manga_id', db.Integer, db.ForeignKey('mangas.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'))
)

class Mangas(db.Model):
    __tablename__ = 'mangas'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(1000), nullable=False)
    image = db.Column(db.String(400), nullable=False)
    author = db.relationship('Authors', secondary=mangas_authors, backref='mangas')
    status = db.Column(db.String(100), default=True)
    genre = db.relationship('Genres', secondary=mangas_genres, backref='mangas')
    updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    description = db.Column(db.String(2000), nullable=False)
    source = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    favorites = db.relationship('Favorites', backref='mangas', lazy='dynamic')
    ratings = db.relationship('Ratings', backref='mangas', lazy='dynamic')
    history = db.relationship('History', backref='mangas', lazy='dynamic')

    def __init__(self, title, slug, image, status, updated, views, description, source):
        self.title = title
        self.slug = slug
        self.image = image
        self.status = status
        self.updated = updated
        self.views = views
        self.description = description
        self.source = source

    def __repr__(self):
        return f'<Manga {self.title}>'

    def serialize(self):
        return {
            'title' : self.title,
            'slug' : self.slug,
            'image' : self.image,
            'status' : self.status,
            'updated' : self.updated,
            'views' : self.views,
            'description' : self.description,
            'source' : self.source
        }



# ------- AUTHORS -------- #
class Authors(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)

    def __init__(self, author):
        self.author = author

    def __repr__(self):
        return f'<Author {self.author}>'

    def serialize(self):
        return {
            'author' : self.author
        }



# ------- GENRES -------- #s
class Genres(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100), nullable=False)

    def __init__(self, genre):
        self.genre = genre

    def __repr__(self):
        return f'<Genre {self.genre}>'

    def serialize(self):
        return {
            'genre' : self.genre
        }



# ------- CHAPTERS -------- #
mangas_chapters = db.Table('mangas_chapters',
    db.Column('manga_id', db.Integer, db.ForeignKey('mangas.id'), primary_key=True),
    db.Column('chapter_id', db.Integer, db.ForeignKey('chapters.id'), primary_key=True)
)

class Chapters(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    chapter_link = db.Column(db.String(300), nullable=False)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    manga = db.relationship('Mangas', secondary=mangas_chapters, backref=db.backref('chapters', lazy='dynamic'))
    history = db.relationship('History', backref='chapters', lazy='dynamic')

    def __init__(self, title, slug, chapter_link, updated):
        self.title = title
        self.slug = slug
        self.chapter_link = chapter_link
        self.updated = updated

    def __repr__(self):
        return f'<Chapter {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'chapter_link': self.chapter_link,
            'updated': self.updated
        }

if __name__ == '__main__':
    print(Mangas.query.filter_by(title='Martial Peak').first().chapters.all())