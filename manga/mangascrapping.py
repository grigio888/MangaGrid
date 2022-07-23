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

from tools import clear, pprint



# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class MangaScrapping():

    def __init__(self):
        self.debug = False 

        self.string_ts = {
            'seconds' : ['sec', 'seconds', 'second', 'secs', 'segundos', 'seg'],
            'minutes' : ['min', 'minutes', 'minut', 'mins'],
            'hours' : ['hour', 'hours', 'horas', 'hora', 'hrs'],
            'days' : ['day', 'days', 'dias', 'dia'],
            'weeks' : ['week', 'weeks', 'semanas', 'semana'],
            'months' : ['month', 'months', 'meses', 'mes'],
            'years' : ['year', 'years', 'anos', 'ano'],
        }

        self.string_ts2 = {
            '01' : ['Jan', 'jan', 'January', 'january'],
            '02' : ['Feb', 'Februari', 'Februari'],
            '03' : ['Mar', 'Mar', 'March'],
            '04' : ['Apr', 'April', 'April'],
            '05' : ['May', 'Mei', 'May'],
            '06' : ['Jun', 'Juni', 'June'],
            '07' : ['Jul', 'Juli', 'July'],
            '08' : ['Aug', 'Aug', 'August'],
            '09' : ['Sep', 'Sep', 'September'],
            '10' : ['Oct', 'Okt', 'October'],
            '11' : ['Nov', 'Nov', 'November'],
            '12' : ['Dec', 'Des', 'December'],
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

        for word in ['An', 'an']:
            if word in string:
                string = string.replace(word, '1')

        string = string.split(' ')
        for time in self.string_ts.keys():
            for param in self.string_ts[time]:
                if param in string:
                    output[time] = int(string[string.index(param) - 1])
                    break

        for month in self.string_ts2.keys():
            for param in self.string_ts2[month]:
                if param in string:
                    output['months'] = int(month)
                    output['days'] = int(string[string.index(param) + 1].replace(',', ''))
                    output['hours'] = int(string[-1].split(':')[0])
                    output['minutes'] = int(string[-1].split(':')[1])
                    break

        if 'months' in output:
            output['days'] = output.get('days', 0) + (output['months'] * 30)
            del output['months']
            
        return datetime.datetime.now() - datetime.timedelta(**output)


    def get_date_from_string(self, string):
        return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')


    def get_string_from_timestamp(self, timestamp):
        """
        This function will receive a time stamp and the output will be:
        'X secs ago', 'X hours ago' or 'X days ago'.
        """
        now = datetime.datetime.now()
        delta = now - timestamp
        if delta.days > 0:
            return f'{delta.days} days ago'
        elif delta.seconds > 0 and delta.seconds < 60:
            return f'{delta.seconds} secs ago'
        elif delta.seconds > 60 and delta.seconds < 3600:
            return f'{delta.seconds // 60} mins ago'
        elif delta.seconds > 3600 and delta.seconds < 86400:
            return f'{delta.seconds // 3600} hours ago'
        elif delta.seconds > 86400 and delta.seconds < 604800:
            return f'{delta.seconds // 86400} days ago'
        elif delta.seconds > 604800 and delta.seconds < 31536000:
            return f'{delta.seconds // 604800} weeks ago'
        elif delta.seconds > 31536000:
            return f'{delta.seconds // 31536000} years ago'


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


if __name__ == '__main__':
    pass