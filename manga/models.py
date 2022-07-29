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
    title = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, title, slug, language, url):
        self.title = title
        self.slug = slug
        self.language = language
        self.url = url

    def __repr__(self):
        return f'<Source {self.slug}>'

    def serialize(self):
        return {
            'source_id': self.id,
            'source_title': self.title,
            'source_slug': self.slug,
            'source_language': self.language,
            'source_url': self.url,
            'source_created_at': self.created_at,
            'source_updated_at': self.updated_at
        }





# -------- STATUS -------- #
class Status(db.Model):
    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, status):
        self.status = status

    def __repr__(self):
        return f'<Status {self.status}>'

    def serialize(self):
        return {
            'status_status' : self.status
        }





# ------- AUTHORS -------- #
class Authors(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, author):
        self.author = author

    def __repr__(self):
        return f'<Author {self.author}>'

    def serialize(self):
        return {
            'authors_author' : self.author
        }





# ------- GENRES -------- #s
class Genres(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, genre):
        self.genre = genre

    def __repr__(self):
        return f'<Genre {self.genre}>'

    def serialize(self):
        return {
            'genres_genre' : self.genre
        }





# ------- MANGAS -------- #
mangas_fk_author = db.Table('mangas_fk_author',
    db.Column('manga_id', db.Integer, db.ForeignKey('mangas.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'), primary_key=True)
)

mangas_fk_genre = db.Table('mangas_fk_genre',
    db.Column('manga_id', db.Integer, db.ForeignKey('mangas.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'))
)

class Mangas(db.Model):
    __tablename__ = 'mangas'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(1000), nullable=False)
    image = db.Column(db.String(400), nullable=False)
    status = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    views = db.Column(db.Integer, default=0)
    description = db.Column(db.String(4000), nullable=False)
    source = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    # -- relationships -- #
    author = db.relationship('Authors', secondary=mangas_fk_author, backref='mangas')
    genre = db.relationship('Genres', secondary=mangas_fk_genre, backref='mangas')

    def __init__(self, title, slug, image, status, views, description, source):
        self.title = title
        self.slug = slug
        self.image = image
        self.status = status
        self.views = views
        self.description = description
        self.source = source

    def __repr__(self):
        return f'<Manga {self.title}>'

    def serialize(self):
        return {
            'manga_id': self.id,
            'manga_title': self.title,
            'manga_slug': self.slug,
            'manga_image': self.image,
            'manga_status': self.status,
            'manga_views': self.views,
            'manga_description': self.description,
            'manga_source': self.source,
            'manga_created_at': self.created_at,
            'manga_updated_at': self.updated_at
        }





# ------- CHAPTERS -------- #
class Chapters(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(300), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, title, slug, link, manga_id):
        self.title = title
        self.slug = slug
        self.link = link
        self.manga_id = manga_id

    def __repr__(self):
        return f'<Chapter {self.title}>'

    def serialize(self):
        return {
            'chapter_id': self.id,
            'chapter_title': self.title,
            'chapter_slug': self.slug,
            'chapter_link': self.link,
            'chapter_manga_id': self.manga_id,
            'chapter_created_at': self.created_at,
            'chapter_updated_at': self.updated_at
        }

if __name__ == '__main__':
    ...
    # print(Mangas.query.filter_by(title='Martial Peak').first().chapters.all())