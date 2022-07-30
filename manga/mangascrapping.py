# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

import datetime
import json
import os
import sys

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

from manga.models import Sources, Mangas, Authors, Genres, Chapters
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


    def get_timestamp_from_string(self, string):
        output = {}

        string = string.replace('An', '1').replace('an', '1').split(' ')
        
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
                        output['year'] = int(datetime.datetime.now().year)
                        output['hour'] = int(string[-1].split(':')[0])
                        output['minute'] = int(string[-1].split(':')[1])
                    return datetime.datetime(**output)

        return datetime.datetime.now()


    def get_date_from_string(self, string):
        return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')


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
        else:
            return f'{int(delta.days / 365)} year ago'



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

    def link_manga_viewer(self, string):
        return f'/manga_viewer?source={self.source}&id={string}'

    def link_chapter_viewer(self, string):
        return f'/chapter_viewer?source={self.source}&id={string}'

    # -------------------- INDEXING BEHAVIORS -------------------- #
    def idx_manga(self, manga: dict):
        idx = Mangas.query.filter_by(slug=manga['slug']).first()

        if not idx:
            idx = Mangas(
                title = manga['title'],
                slug = manga['slug'],
                image = manga['image'],
                status = manga['status'],
                updated = self.get_timestamp_from_string(manga['updated']),
                views = manga['views'],
                description = manga['description'],
                source = manga['source'],
            )
            db.session.add(idx)
            pprint(f'[i] Info: Manga {idx.title} indexed.', 'green')

        else:
            pprint(f'[i] Info: Manga {idx.title} already indexed.', 'green')

        for genre in self.idx_genre(manga['genres']):
            if genre not in idx.genre:
                idx.genre.append(genre)
                pprint(f'[i] Info: Genre {genre.genre} added to {idx.title}.', 'green')

        for author in self.idx_author(manga['author']):
            if author not in idx.author:
                idx.author.append(author)
                pprint(f'[i] Info: Author {author.author} added to {idx.title}.', 'green')

        for chapter in self.idx_chapter(manga['chapters']):
            if chapter not in idx.chapters:
                idx.chapters.append(chapter)
                pprint(f'[i] Info: Chapter {chapter.title} added to {idx.title}.', 'green')
            else: break

        db.session.commit()

        return idx


    def idx_genre(self, genres: list):
        output = []

        for genre in genres:
            verif = Genres.query.filter_by(genre=genre).first()
            if not verif:
                genre_obj = Genres(genre)
                db.session.add(genre_obj)
                db.session.commit()
                output.append(genre_obj)
                pprint(f'[i] Info: Genre {genre} indexed.', 'green')

        return output

    def idx_author(self, authors: list):
        output = []
        
        for author in authors:
            idx = Authors.query.filter_by(author=author).first()
            if not idx:
                idx = Authors(author)
                db.session.add(idx)
                pprint(f'[i] Info: Author {idx.author} indexed.', 'green')
            output.append(idx)

        db.session.commit()

        return output

    def idx_chapter(self, chapters: list):
        output = []

        for chapter in chapters:
            idx = Chapters.query.filter_by(slug=chapter['slug']).first()
            if not idx:
                idx = Chapters(
                    title = chapter['title'],
                    slug = chapter['slug'],
                    chapter_link = chapter['chapter_link'],
                    updated = MangaScrapping().get_timestamp_from_string(chapter['updated']) if chapter['updated'] in chapter else datetime.datetime.now(),
                )
                db.session.add(idx)
                pprint(f'[i] Info: Chapter {chapter["title"]} indexed.', 'green')
            else: break
            output.append(idx)

        db.session.commit()

        return output

if __name__ == '__main__':
    pass