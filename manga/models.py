# -------------- ALLOW SELF EXECUTE --------------- #
import os, sys
sys.path.append(os.getcwd())


# ------------------ IMPORTING -------------------- #
import datetime

from extensions import db


# -------------- BEHAVIOR STRUCTURE --------------- #

class BehaviorStructure():
    # every behavior must have a self.object = Object and
    # self.every_field = [self.with, self.every, self.field]

    # -- General Behavior -- #
    def create(self):
        if self.check_all_fields() and self.read() is None:
            object_created = self.object(*self.every_field)
            db.session.add(object_created)
            db.session.commit()
            return object_created

        elif not self.check_all_fields():
            raise Exception(f'Missing field in order to create a object {self.object.__name__}')

        else:
            raise Exception(f'{self.object.__name__} already exists')

    def read(self):
        return self.object.query.filter_by(slug=self.slug).first()

    def update(self):
        ...
        # must be implemented in the child class

    def delete(self):
        object_query = self.object.query.filter_by(slug=self.slug).first()

        if object_query is not None:
            db.session.delete(object_query)
            db.session.commit()
            return object_query

        else:
            raise Exception(f'{self.object.__name__} does not exist')


    # -- Checks -- #
    def check_all_fields(self):
        if self.every_field is None:
            return False

        for field in self.every_field:
            if field is None:
                return False
        
        return True





# -------------------- MODELS --------------------- #

# ------- SOURCES -------- #
class Sources(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), unique=True, nullable=False)
    language = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, slug, title, language, url):
        self.slug = slug
        self.title = title
        self.language = language
        self.url = url

    def __repr__(self):
        return f'<Source {self.slug}>'

    def __name__(self):
        return 'Sources'

    def serialize(self):
        return {
            'source_id': self.id,
            'source_slug': self.slug,
            'source_title': self.title,
            'source_language': self.language,
            'source_url': self.url,
            'source_created_at': self.created_at,
            'source_updated_at': self.updated_at
        }

class SourcesBehavior(BehaviorStructure):
    def __init__(self, slug, title=None, language=None, url=None):
        self.slug = slug
        self.title = title
        self.language = language
        self.url = url

        self.every_field = [self.slug, self.title, self.language, self.url]
        self.object = Sources

    # -- General Behavior -- #
    def update(self):
        if self.check_all_fields() and self.read() is not None:
            source = self.read()
            source.title = self.title
            source.language = self.language
            source.url = self.url
            db.session.commit()
            return source

        elif not self.check_all_fields():
            raise Exception('Missing field in order to update a source')

        else:
            raise Exception('Source does not exist')



# -------- STATUS -------- #
class Status(db.Model):
    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, slug):
        self.slug = slug

    def __repr__(self):
        return f'<Status {self.slug}>'

    def __name__(self):
        return 'Status'

    def serialize(self):
        return {
            'status_status' : self.slug
        }

class StatusBehavior(BehaviorStructure):
    def __init__(self, slug):
        self.slug = slug

        self.every_field = [self.slug,]
        self.object = Status

    # -- General Behavior -- #
    def update(self):
        if self.check_all_fields() and self.read() is not None:
            status = self.read()
            status.slug = self.slug
            db.session.commit()
            return status

        elif not self.check_all_fields():
            raise Exception('Missing field in order to update a status')

        else:
            raise Exception('Status does not exist')





# ------- AUTHORS -------- #
class Authors(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, slug):
        self.slug = slug

    def __repr__(self):
        return f'<Author {self.slug}>'

    def __name__(self):
        return 'Authors'

    def serialize(self):
        return {
            'authors_author' : self.slug
        }

class AuthorsBehavior(BehaviorStructure):
    def __init__(self, slug):
        self.slug = slug

        self.every_field = [self.slug]
        self.object = Authors

    # -- General Behavior -- #
    def update(self):
        if self.check_all_fields() and self.read() is not None:
            author = self.read()
            author.slug = self.slug
            db.session.commit()
            return author

        elif not self.check_all_fields():
            raise Exception('Missing field in order to update an author')

        else:
            raise Exception('Author does not exist')





# ------- GENRES -------- #s
class Genres(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, slug):
        self.slug = slug

    def __repr__(self):
        return f'<Genre {self.slug}>'

    def __name__(self):
        return 'Genres'

    def serialize(self):
        return {
            'genres_genre' : self.slug
        }

class GenresBehavior(BehaviorStructure):
    def __init__(self, slug):
        self.slug = slug

        self.every_field = [self.slug]
        self.object = Genres

    # -- General Behavior -- #
    def update(self):
        if self.check_all_fields() and self.read() is not None:
            genre = self.read()
            genre.slug = self.slug
            db.session.commit()
            return genre

        elif not self.check_all_fields():
            raise Exception('Missing field in order to update a genre')

        else:
            raise Exception('Genre does not exist')





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
    slug = db.Column(db.String(1000), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(400), nullable=False)
    status = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    updated = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    views = db.Column(db.Integer, default=0)
    description = db.Column(db.String(4000), nullable=False)
    source = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    # -- relationships -- #
    author = db.relationship('Authors', secondary=mangas_fk_author, backref='mangas')
    genre = db.relationship('Genres', secondary=mangas_fk_genre, backref='mangas')

    def __init__(self, slug, title, image, status, views, description, source):
        self.slug = slug
        self.title = title
        self.image = image
        self.status = status
        self.views = views
        self.description = description
        self.source = source

    def __repr__(self):
        return f'<Manga {self.title}>'

    def __name__(self):
        return 'Mangas'

    def serialize(self):
        return {
            'manga_id': self.id,
            'manga_slug': self.slug,
            'manga_title': self.title,
            'manga_image': self.image,
            'manga_status': self.status,
            'manga_views': self.views,
            'manga_description': self.description,
            'manga_source': self.source,
            'manga_created_at': self.created_at,
            'manga_updated_at': self.updated_at
        }


class MangaBehavior(BehaviorStructure):
    def __init__(self, slug, title=None, image=None, status=None, views=None, description=None, source=None):
        self.slug = slug
        self.title = title
        self.image = image
        self.status = status
        self.views = views
        self.description = description
        self.source = source

        self.every_field = [self.slug, self.title, self.image, self.status, self.views, self.description, self.source]
        self.object = Mangas

    # -- General Behavior -- #
    def update(self):
        if self.check_all_fields() and self.read() is not None:
            manga = self.read()
            manga.title = self.title
            manga.image = self.image
            manga.status = self.status
            manga.views = self.views
            manga.description = self.description
            manga.source = self.source
            db.session.commit()
            return manga

        elif not self.check_all_fields():
            raise Exception('Missing fields in order to update a manga')

        else:
            raise Exception('Manga does not exist')

    # -- Relations Behavior -- #
    # -- Authors -- #
    def add_author(self, author):
        manga = self.read()

        if manga is not None and author not in manga.author and type(author) is Authors:
            manga.author.append(author)
            db.session.commit()
            return manga

        elif manga is None:
            raise Exception('Manga does not exist')

        elif author in manga.author:
            raise Exception('Author already registered in manga')

        else:
            raise Exception('Invalid object for author')

    def remove_author(self, author):
        manga = self.read()

        if manga is not None and author in manga.author and type(author) is Authors:
            manga.author.remove(author)
            db.session.commit()
            return manga

        elif manga is None:
            raise Exception('Manga does not exist')

        elif author not in manga.author:
            raise Exception('Author not registered in manga')

        else:
            raise Exception('Invalid object for author')

    def remove_all_authors(self):
        manga = self.read()

        if manga is not None:
            manga.author = []
            db.session.commit()
            return manga

        else:
            raise Exception('Manga does not exist')

    # -- Genres -- #
    def add_genre(self, genre):
        manga = self.read()

        if manga is not None and genre not in manga.genre and type(genre) is Genres:
            manga.genre.append(genre)
            db.session.commit()
            return manga

        elif manga is None:
            raise Exception('Manga does not exist')

        elif genre in manga.genre:
            raise Exception('Genre already registered in manga')

        else:
            raise Exception('Invalid object for genre')

    def remove_genre(self, genre):
        manga = self.read()

        if manga is not None and genre in manga.genre and type(genre) is Genres:
            manga.genre.remove(genre)
            db.session.commit()
            return manga

        elif manga is None:
            raise Exception('Manga does not exist')

        elif genre not in manga.genre:
            raise Exception('Genre not registered in manga')

        else:
            raise Exception('Invalid object for genre')

    def remove_all_genres(self):
        manga = self.read()

        if manga is not None:
            manga.genre = []
            db.session.commit()
            return manga

        else:
            raise Exception('Manga does not exist')

    # -- Status -- #
    def update_status(self, status):
        manga = self.read()

        if manga is not None and type(status) is Status:
            manga.status = status.id
            db.session.commit()
            return manga

        elif manga is None:
            raise Exception('Manga does not exist')

        else:
            raise Exception('Invalid object for status')



# ------- CHAPTERS -------- #
class Chapters(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(300), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('mangas.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    updated_on_source = db.Column(db.DateTime)

    # -- Relations -- #
    manga = db.relationship('Mangas', backref=db.backref('chapters', lazy='dynamic'))

    def __init__(self, slug, title, link, manga_id, updated_on_source):
        self.slug = slug
        self.title = title
        self.link = link
        self.manga_id = manga_id
        self.updated_on_source = updated_on_source

    def __repr__(self):
        return f'<Chapter {self.title}>'

    def __name__(self):
        return f'Chapter'

    def serialize(self):
        return {
            'chapter_id': self.id,
            'chapter_slug': self.slug,
            'chapter_title': self.title,
            'chapter_link': self.link,
            'chapter_manga_id': self.manga_id,
            'chapter_created_at': self.created_at,
            'chapter_updated_at': self.updated_at,
            'chapter_updated_on_source': self.updated_on_source
        }

class ChapterBehavior(BehaviorStructure):
    def __init__(self, slug, title=None, link=None, manga_id=None, updated_on_source=None):
        self.slug = slug
        self.title = title
        self.link = link
        self.manga_id = manga_id
        self.updated_on_source = updated_on_source

        self.every_field = [self.slug, self.title, self.link, self.manga_id, self.updated_on_source]
        self.object = Chapters

    # -- General Behavior -- #
    def update(self):
        if self.check_all_fields() and self.read() is not None:
            chapter = self.read()
            chapter.title = self.title
            chapter.link = self.link
            chapter.manga_id = self.manga_id
            chapter.updated_on_source = self.updated_on_source
            db.session.commit()
            return chapter

        elif not self.check_all_fields():
            raise Exception('Missing fields in order to update a chapter')

        else:
            raise Exception('Chapter does not exist')





if __name__ == '__main__':
    manga = Mangas.query.filter_by(title='I Became the Tyrant’s Translator').first()
    print(manga.status)