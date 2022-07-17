# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
import concurrent.futures
import threading

from flask import Blueprint, jsonify

from extensions import sources
from tools import c_response, pprint

# ------------------------------------------------- #
# -------------------- TOOLS ---------------------- #
# ------------------------------------------------- #

def process_generator(func, args):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        task_1 = executor.submit(func, args)
        return task_1.result()

# ------------------------------------------------- #
# ---------------- STARTING ROUTE ----------------- #
# ------------------------------------------------- #
manga = Blueprint('manga', __name__)

@manga.route('/avaliable_sources')
def avaliable_sources():
    data = {}
    for s in sources:
        data[s] = sources[s]['language']

    return jsonify(c_response(200, 'Sources avaliable', data))

@manga.route('/chapter/<string:source>/<string:search>')
def chapter(source, search):
    try:
        obj = sources[source]['object']
        task = process_generator(obj().get_chapter_content, search)

        if task:
            return jsonify(c_response(200, 'Chapter fetched succesfully', task))

        else:
            pprint(f'[!] ERROR: /api/manga/chapter - Chapter not found for {search}')
            return jsonify(c_response(404, 'No results'))

    except KeyError:
        pprint(f'[!] ERROR: /api/manga/chapter - Source ({source}) not found', 'red')
        return jsonify(c_response(400, 'Source not avaliable'))

    except Exception as e:
        pprint(f'[!] ERROR: /api/manga/chapter - General exception. {e}', 'red')
        return jsonify(c_response(500, str(e)))

@manga.route('/search/<string:source>/<string:search>')
def search(source, search):
    try:
        obj = sources[source]['object']
        task = process_generator(obj().search_title, search)

        if task:
            return jsonify(c_response(200, 'Search results', task))

        else:
            pprint(f'[!] ERROR: /api/manga/search - No results for {search}')
            return jsonify(c_response(404, 'No results'))

    except KeyError:
        pprint(f'[!] ERROR: /api/manga/search - Source ({source}) not found', 'red')
        return jsonify(c_response(400, 'Source not avaliable'))

    except Exception as e:
        pprint(f'[!] ERROR: /api/manga/search - General exception. {e}', 'red')
        return jsonify(c_response(500, str(e)))

@manga.route('/view/<string:source>/<string:search>')
def view(source, search):
    try:
        manga = process_generator(sources[source]['object']().access_manga, search)

        if manga is None:
            pprint(f'[!] ERROR: /api/manga/view - Manga not found for {search}')
            return jsonify(c_response(404, 'Manga not found')), 404

        else: return jsonify(c_response(200, 'Target captured', manga))

    except KeyError:
        pprint(f'[!] ERROR: /api/manga/view - Source ({source}) not found', 'red')
        return jsonify(c_response(404, 'Source not found')), 404

    except Exception as e:
        pprint(f'[!] ERROR: /api/manga/view - General exception. {e}', 'red')
        return jsonify(c_response(500, 'An thread exception, not communicable.')), 500