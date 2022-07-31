# ---------------- DEFAULT IMPORTS ---------------- #

import concurrent.futures
import datetime

from flask import Blueprint, jsonify, session, request

from extensions import db
from tools.sources import sources
from tools.tools import c_response, pprint
from manga.mangascrapping import MangaScrapping as ms

from manga.models import ChapterBehavior, Sources, Mangas, Chapters
from users.models import Users, History



# -------------------- TOOLS ---------------------- #

def process_generator(func, args):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        task_1 = executor.submit(func, args)
        return task_1.result()



# ---------------- STARTING ROUTE ----------------- #
manga = Blueprint('manga', __name__)

@manga.route('/avaliable_sources')
def avaliable_sources():
    data = {
        s: sources[s]['language'] for s in sources.keys()
    }

    return jsonify(c_response(200, 'Sources avaliable', data))





# ----------------- SEARCHING TITLE ----------------- #
@manga.route('/search/<string:source>/<string:search>')
def search(source, search):
    try:
        task = process_generator(sources[source]['object']().search_title, search)
        for manga in task:
            task[manga]['updated'] = ms().get_string_from_timestamp(task[manga]['updated'])

        if task:
            return jsonify(c_response(200, 'Search results', task))

        else:
            pprint(f'[!] ERROR: {request.path} - No results for {search}', 'red')
            return jsonify(c_response(404, 'No results'))

    except KeyError:
        pprint(f'[!] ERROR: {request.path} - Source ({source}) not found', 'red')
        return jsonify(c_response(400, 'Source not avaliable'))

    except Exception as e:
        pprint(f'[!] ERROR: {request.path} - General exception. {e}', 'red')
        return jsonify(c_response(500, str(e)))



# ----------------- QUERYING MANGA ----------------- #
@manga.route('/view/<string:source>/<string:search>')
def view(source, search):
    try:
        manga = process_generator(sources[source]['object']().access_manga, search)

        if not manga:
            pprint(f'[!] ERROR: /api/manga/view - Manga not found for {search}')
            return jsonify(c_response(404, 'Manga not found')), 404

        ms().idx_manga(manga)

        manga['updated'] = ms().get_string_from_timestamp(manga['updated'])
        for chapter in manga['chapters']:
            chapter['updated'] = ms().get_string_from_timestamp(chapter['updated'])

        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first().id
            source = Sources.query.filter_by(slug=source).first().id
            mangas = Mangas.query.filter_by(slug=search, source=source).first().id

            history = History.query.filter_by(user_id=user, manga_id=mangas).first()
            if not history:
                history = History(user_id=user, manga_id=mangas)
                db.session.add(history)
                db.session.commit()
            else:
                for chapter in history.chapters.all():
                    for ch in manga['chapters']:
                        if ch['slug'] == chapter.slug:
                            ch['read'] = True
            
        return jsonify(c_response(200, 'Target captured', manga))

    except KeyError as e:
        pprint(f'[!] ERROR: {e}', 'red')
        pprint(f'[!] ERROR: /api/manga/view - Source ({source}) not found', 'red')
        return jsonify(c_response(404, 'Source not found')), 404

    except Exception as e:
        pprint(f'[!] ERROR: /api/manga/view - General exception. {e}', 'red')
        return jsonify(c_response(500, 'An thread exception, not communicable.')), 500



# ----------------- QUERYING CHAPTER ----------------- #
@manga.route('/chapter/<string:source>/<string:search>')
def chapter(source, search):
    try:
        obj = sources[source]['object']
        task = process_generator(obj().get_chapter_content, search)

        if not task:
            pprint(f'[!] ERROR: {request.path} - Chapter not found for {search}')
            return jsonify(c_response(404, 'No results'))

        chapter_obj = Chapters.query.filter_by(slug=search).first()

        if not chapter_obj or 'email' not in session:
            return jsonify(c_response(200, 'Chapter fetched succesfully', task))

        user = Users.query.filter_by(email=session['email']).first()
        manga = Mangas.query.filter(Mangas.chapters.contains(chapter_obj)).first()

        history = History.query.filter_by(user_id=user.id, manga_id=manga.id).first()
        if chapter_obj in history.chapters.all():
            history.chapters.remove(chapter_obj)
            history.chapters.append(chapter_obj)
        else:
            history.chapters.append(chapter_obj)
        history.updated_at = datetime.datetime.now()
        db.session.commit()

        return jsonify(c_response(200, 'Chapter fetched succesfully', task))

    except KeyError as e:
        print(e)
        pprint(f'[!] ERROR: {request.path} - Source ({source}) not found', 'red')
        return jsonify(c_response(400, 'Source not avaliable'))

    except Exception as e:
        pprint(f'[!] ERROR: {request.path} - General exception. {e}', 'red')
        return jsonify(c_response(500, str(e)))