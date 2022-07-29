# ---------------- DEFAULT IMPORTS ---------------- #
# make the script return to the main directory
import os, sys

sys.path.append(os.getcwd())

import concurrent.futures
import datetime
import json
import time

from extensions import db
from tools.sources import sources
from tools.tools import clear, pprint

from manga.mangascrapping import MangaScrapping as ms
from manga.models import Sources, Mangas, Authors, Genres, Chapters
from users.models import Users, History, Favorites


# -------------------- TOOLS ---------------------- #

def process_generator(func, args):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        task_1 = executor.submit(func, args)
        return task_1.result()


# ------------------- STRUCTURE ------------------- #

def refresh_routine():
    try:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for obj in sources:
                executor.submit(sources[obj]['object']().refresh_routine)

    except Exception as e:
        print(f'Error: {e}')

def indexing_routine():
    results = {}
    for manga in sources.keys():
        try:
            manga = f'{manga.capitalize()} ({sources[manga]["language"].split("_")[0].upper()})'
            results[manga] = {}
            with open(f'manga/results/{manga.split(" ")[0].lower()}_updates.json') as json_file:
                results[manga].update(json.load(json_file))

            for entrada in results[manga]:
                if results[manga][entrada]['updated']:
                    date = ms().get_date_from_string(results[manga][entrada]['updated'])
                    results[manga][entrada]['updated'] = ms().get_string_from_timestamp(date)
        
        except Exception as e:
            print(f'Error: {e}')
            pprint(f'[!] ERROR: / - Archive not found for {manga}', 'red')

    targets = []
    for source in results:
        for manga in results[source]:
            targets.append([results[source][manga]['source'], results[source][manga]['slug']])

    for target in targets:
        manga = sources[target[0]]['object']().access_manga(target[1])

        ms().idx_manga(manga)

if __name__ == '__main__':

    allow = True

    interval = 60 * 30
    interval_remaining = 0

    while allow:
        clear()
        pprint(f'[i] Current time to auto update: {interval}s.')
        pprint(f'[+] Refreshing in {interval_remaining}s.', 'green')

        if interval_remaining == 0:
            clear()
            pprint('[i] Initialiazing refreshing sources...\n', 'yellow')
            refresh_routine()
            pprint('[!] Refresh doned.\n', 'green')
            pprint('[i] Initialiazing indexing titles...\n\n', 'yellow')
            time.sleep(5)
            indexing_routine()
            pprint('\n[!] Refresh doned.\n[.] Restarting routine...', 'green')
            time.sleep(5)
            interval_remaining = interval

        time.sleep(1)
        interval_remaining -= 1