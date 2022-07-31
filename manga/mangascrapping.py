# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

import datetime
import json
import os
import sys
from turtle import update

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *

from extensions import db
from tools.tools import clear, pprint

from manga.models import MangaBehavior, SourcesBehavior, StatusBehavior, AuthorsBehavior,\
                         GenresBehavior, ChapterBehavior, Mangas
from users.models import Users, History

# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class MangaScrapping():

    def __init__(self):
        self.debug = False 
        self.source = None

        self.string_ts = {
            'seconds' : ['sec', 'seconds', 'second', 'secs', 'segundos', 'seg'],
            'minutes' : ['min', 'minutes', 'minut', 'mins', 'minutos', 'min'],
            'hours' : ['hour', 'hours', 'horas', 'hora', 'hrs'],
            'days' : ['day', 'days', 'dias', 'dia'],
            'weeks' : ['week', 'weeks', 'semanas', 'semana'],
            'months' : ['month', 'months', 'meses', 'mes'],
            'years' : ['year', 'years', 'anos', 'ano'],
        }

        self.string_ts2 = {
            '01' : ['Jan', 'jan', 'January', 'january', 'Janeiro', 'janeiro'],
            '02' : ['Feb', 'Februari', 'Februari', 'Fevereiro', 'fevereiro'],
            '03' : ['Mar', 'Mar', 'March', 'mar', 'Março', 'março'],
            '04' : ['Apr', 'April', 'April', 'Abril', 'abril'],
            '05' : ['May', 'Mei', 'May', 'Mai', 'Maio', 'maio'],
            '06' : ['Jun', 'Juni', 'June', 'jun', 'Junho', 'junho'],
            '07' : ['Jul', 'Juli', 'July', 'jul', 'Julho', 'julho'],
            '08' : ['Aug', 'Aug', 'August', 'aug', 'Agosto', 'agosto'],
            '09' : ['Sep', 'Sep', 'September', 'sep', 'Setembro', 'setembro'],
            '10' : ['Oct', 'Okt', 'October', 'oct', 'Outubro', 'outubro'],
            '11' : ['Nov', 'Nov', 'November', 'nov', 'Novembro', 'novembro'],
            '12' : ['Dec', 'Des', 'December', 'dec', 'Dezembro', 'dezembro'],
        }

    @property
    def driver_path(self):
        if sys.platform == 'linux':
            return '/usr/bin/geckodriver'
        elif sys.platform == 'win32':
            return 'manga/chromedriver.exe'


    # ------------------------------------------------- #
    # -------------------- TOOLS ---------------------- #
    # ------------------------------------------------- #

    def waiting(self, driver, tag = By.XPATH, tag_name = '', plural = False):
        if plural:
            return WebDriverWait(driver, 20).until(ec.presence_of_all_elements_located((tag, tag_name)))
        else:
            return WebDriverWait(driver, 20).until(ec.presence_of_element_located((tag, tag_name)))


    def browser(self, showing = False):
        if sys.platform == 'linux':
            c = DesiredCapabilities.FIREFOX
            c["pageLoadStrategy"] = "none"
            self.driver = webdriver.Firefox(service=Service(self.driver_path), desired_capabilities=c)

        elif sys.platform == 'win32':
            c = DesiredCapabilities.CHROME
            options = Options()
            if not showing:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(service=Service(self.driver_path), desired_capabilities=c, options=options)
            self.driver.minimize_window()


    def get_timestamp_from_string(self, string, where = 'all'):
        output = {}

        if where == 'mangaschan':
            string = string.replace(',', '').split(' ')
        else:
            string = string.replace(',', '').split(' ')
            if 'an' in string:
                string[string.index('an')] = '1'
            elif 'An' in string:
                string[string.index('An')] = '1'

        for time in self.string_ts.keys():
            for param in self.string_ts[time]:
                if param in string:
                    output[time] = int(string[string.index(param) - 1])
                    return datetime.datetime.now() - datetime.timedelta(**output)

        for month in self.string_ts2.keys():
            for param in self.string_ts2[month]:
                if param in string:
                    output['month'] = int(month)
                    output['day'] = int(string[string.index(param) + 1].replace(',', ''))
                    try:
                        output['year'] = int(string[string.index(param) + 2])
                    except:
                        output['year'] = int(datetime.datetime.now().year) if output['month'] < int(datetime.datetime.now().month) else int(datetime.datetime.now().year) - 1
                        output['hour'] = int(string[-1].split(':')[0])
                        output['minute'] = int(string[-1].split(':')[1])

                    return datetime.datetime(**output)

        # raise Exception('Timestamp not found')
        return datetime.datetime(year=2010, month=1, day=1)


    def get_date_from_string(self, string):
        datetime_expected = [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y'
        ]

        for format in datetime_expected:
            try:
                return datetime.datetime.strptime(string, format)
            except:
                pass
        
        raise Exception('Date not found')


    def get_string_from_timestamp(self, timestamp):
        """
        This function will receive a time stamp and the output will be:
        'X secs ago', 'X hours ago' or 'X days ago'.
        """
        now = datetime.datetime.now()
        delta = now - timestamp

        if delta.days == 0:
            return 'Today'
        elif delta.days == 1:
            return 'Yesterday'
        elif delta.days < 7:
            return f'{delta.days} days ago'
        elif delta.days < 30:
            return f'{int(delta.days / 7)} weeks ago'
        elif delta.days < 365:
            return f'{int(delta.days / 30)} months ago'
        elif delta.days < 365 * 10:
            return f'{int(delta.days / 365)} year ago'
        else:
            return 'Unknown'



    def dump_results(self, archive, results):
        with open(f"manga/results/{archive}.json", "w") as mangas:  
            mangas.write(json.dumps(results, indent = 4))

        pprint(f'[!] LOG: Results saved {archive}.json', 'green')

    def sanitize_string(self, source, string):
        dic = {
            'manganato' : {
                "_" : [" ", "'", ",", "-"],
                "" : ["?", "!", '"', ".", "~"],
            },
            'mangahere' : {
                "_" : [" ", "-"],
                "" : [":", "!", "?", ";", ",", "."],
            },
            'mangaschan' : {
                "%21" : ["!",],
                "%3F" : ["?",],
                "%2C" : [",",],
                "%2F" : ["/",],
                "%2D" : ["-",],
                "%27" : ["'",],
                "%3A" : [":",],
                "%3B" : [";",],
                "%3D" : ["=",],
                "%2B" : ["+",],
                "%2A" : ["*",],
                "%25" : ["%",],
                "%7C" : ["|",],
                "+" : [" ",],
            }
        }

        for key in dic[source].keys():
            for value in dic[source][key]:
                string = string.replace(value, key)

        return string.lower()

    def creating_manga_and_chapter_folder(self, manga, chapter):
        fmanga, fchapter = False, False
        if not os.path.exists(f'static/manga/results/{manga}'):
            os.makedirs(f'static/manga/results/{manga}')
            fmanga = True
        if not os.path.exists(f'static/manga/results/{manga}/{chapter}'):
            os.makedirs(f'static/manga/results/{manga}/{chapter}')
            open(f'static/manga/results/{manga}/{chapter}/relation.json', 'w').close()
            fchapter = True

        return [fmanga, fchapter]

    def link_manga_viewer(self, slug):
        return f'/manga_viewer?source={self.source}&id={slug}'

    def link_chapter_viewer(self, slug):
        return f'/chapter_viewer?source={self.source}&id={slug}'

    # -------------------- INDEXING BEHAVIORS -------------------- #
    def idx_manga(self, manga: dict):        
        status = StatusBehavior(manga['status']).read()
        if not status:
            status = StatusBehavior(manga['status']).create()
            pprint(f'[i] Info: Status {status.slug} created.', 'green')

        manga_obj = MangaBehavior(manga['slug']).read()

        if not manga_obj:
            manga_obj = MangaBehavior(
                slug = manga['slug'],
                title = manga['title'],
                image = manga['image'],
                status = status.id,
                views = manga['views'],
                description = manga['description'],
                source = SourcesBehavior(manga['source']).read().id,
            ).create()
            pprint(f'[i] Info: Manga status {manga_obj.title} is {status.slug}.', 'green')
            pprint(f'[i] Info: Manga {manga_obj.title} indexed.', 'green')

        else:
            manga_obj.image = manga['image']
            db.session.commit()
            pprint(f'[i] Info: Manga {manga_obj.title} already indexed.', 'yellow')

        for author in manga['author']:
            author_obj = AuthorsBehavior(author).read()
            if not author_obj:
                author_obj = AuthorsBehavior(author).create()
                pprint(f'[i] Info: Author {author_obj.slug} created.', 'green')

            try:
                MangaBehavior(manga_obj.slug).add_author(author_obj)
                pprint(f'[i] Info: Author {author_obj.slug} added to {manga_obj.title}.', 'green')
            except:
                pprint(f'[i] Info: Author {author_obj.slug} already added to {manga_obj.title}.', 'yellow')

        for genre in manga['genres']:
            genre_obj = GenresBehavior(genre).read()
            if not genre_obj:
                genre_obj = GenresBehavior(genre).create()
                pprint(f'[i] Info: Genre {genre_obj.slug} created.', 'green')

            try:
                MangaBehavior(manga_obj.slug).add_genre(genre_obj)
                pprint(f'[i] Info: Genre {genre_obj.slug} added to {manga_obj.title}.', 'green')
            except:
                pprint(f'[i] Info: Genre {genre_obj.slug} already added to {manga_obj.title}.', 'yellow')


        try:
            chapter_obj = ChapterBehavior(manga['chapters'][-1]['slug']).read()
            if not chapter_obj:
                pprint(f'[i] Info: Last chapter of {manga_obj.title} not indexed. Starting routine.', 'yellow')
                for chapter in manga['chapters'][::-1]:
                    chapter_obj = ChapterBehavior(chapter['slug']).read()
                    if not chapter_obj:
                        chapter_obj = ChapterBehavior(
                            slug = chapter['slug'],
                            title = chapter['title'],
                            link = chapter['chapter_link'],
                            manga_id = manga_obj.id,
                            updated_on_source= chapter['updated'],
                        ).create()
                        pprint(f'[i] Info: Chapter {chapter_obj.title} of {manga_obj.title} created.', 'green')

                    else:
                        pprint(f'[i] Info: Chapter {chapter_obj.title} of {manga_obj.title} already indexed.', 'yellow')
            else:
                pprint(f'[i] Info: Last chapter of {manga_obj.title} indexed. Skipping routine.', 'yellow')

        except:
            pprint(f'[i] Info: Manga {manga_obj.title} doesnt have chapters. Skipping routine.', 'yellow')
                
        return manga_obj

if __name__ == '__main__':
    pass