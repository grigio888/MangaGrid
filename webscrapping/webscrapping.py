# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #

import datetime
import json
import sys

import concurrent.futures

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import *



# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class MangaScrapping():

    def __init__(self):
        self.debug = False    

    @property
    def driver_path(self):
        if sys.platform == 'linux':
            return '/usr/bin/geckodriver'
        elif sys.platform == 'win32':
            return 'webscrapping/chromedriver.exe'


    # ------------------------------------------------- #
    # -------------------- TOOLS ---------------------- #
    # ------------------------------------------------- #

    def interacting(self, tag_name, click = False, writing = False, word = '', tag = By.XPATH):
        try:
            self.target = WebDriverWait(self.driver, 20).until(ec.presence_of_element_located((tag, tag_name)))
            if click: self.target.click()
            if writing: self.target.send_keys(word)
        except Exception as e:
            print(f'Error: {e}')


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
        string = string.split(' ')

        if 'An' in string:
            string[string.index('An')] = 1
        elif 'an' in string:
            string[string.index('an')] = 1

        if 'sec' in string:
            return datetime.datetime.now() - datetime.timedelta(seconds=int(string[0]))
        elif 'min' in string:
            return datetime.datetime.now() - datetime.timedelta(minutes=int(string[0]))
        elif 'hour' in string:
            return datetime.datetime.now() - datetime.timedelta(hours=int(string[0]))
        elif 'day' in string:
            return datetime.datetime.now() - datetime.timedelta(days=int(string[0]))
        elif 'month' in string:
            return datetime.datetime.now() - datetime.timedelta(days=int(string[0]) * 30)
        elif 'year' in string:
            return datetime.datetime.now() - datetime.timedelta(days=int(string[0]) * 365)
        else:
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
        with open(f"webscrapping/results/{archive}.json", "w") as mangas:  
            mangas.write(json.dumps(results, indent = 4))



    # ------------------------------------------------- #
    # ------------------ BEHAVIORS -------------------- #
    # ------------------------------------------------- #

    def routine_initialization(self):
        with concurrent.futures.ProcessPoolExecutor() as executor:
            task_1 = executor.submit(self.manganato)
            task_2 = executor.submit(self.mangalife)

            task_1.result()
            task_2.result()

    # ------------------ MANGANATO -------------------- #

    def manganato(self):
        self.manganato_updates()


    def manganato_updates(self):
        self.browser(self.debug)
        self.driver.get('https://manganato.com/index.php')

        updates = {}

        div = self.interacting('content-homepage-item', tag = By.CLASS_NAME)
        div = self.driver.find_elements(By.CLASS_NAME, 'content-homepage-item')

        for item in div:
            image = item.find_element(By.CLASS_NAME, 'img-loading')
            title = item.find_element(By.CLASS_NAME, 'item-title')
            link = item.find_element(By.CLASS_NAME, 'a-h')
            chapter = item.find_element(By.CLASS_NAME, 'item-chapter')
            
            try:
                author = item.find_element(By.CLASS_NAME, 'item-author')
                author = author.text
            except NoSuchElementException:
                author = None
            
            updated = self.get_timestamp_from_string(chapter.text.split('\n')[1])

            updates[title.text] = {
                'link' : link.get_attribute('href'),
                'author' : author,
                'image' : image.get_attribute('src'),
                'chapter' : chapter.text.split('\n')[0],
                'updated' : f'{updated}',
                'source' : 'Manganato'
            }

        self.dump_results('manganato_updates', updates)

        self.driver.quit()


    # ------------------ MANGALIFE -------------------- #

    def mangalife(self):
        self.mangalife_updates()


    def mangalife_updates(self):
        self.browser(self.debug)
        self.driver.get('https://manga4life.com/')

        updates = {}

        latest_updates = self.interacting('LatestChapters', tag = By.CLASS_NAME)
        latest_updates = self.driver.find_element(By.CLASS_NAME, 'LatestChapters')

        div = latest_updates.find_elements(By.CLASS_NAME, 'Chapter')

        for item in div:
            title = item.find_element(By.CLASS_NAME, 'SeriesName')
            image = item.find_element(By.CLASS_NAME, 'Image')
            link = image.find_element(By.TAG_NAME, 'a')
            image = image.find_element(By.TAG_NAME, 'img')
            chapter = item.find_element(By.CLASS_NAME, 'ChapterLabel')
            updated = item.find_element(By.CLASS_NAME, 'DateLabel')

            updated = self.get_timestamp_from_string(updated.text)

            updates[title.text] = {
                'link' : link.get_attribute('href'),
                'author' : 'none',
                'image' : image.get_attribute('src'),
                'chapter' : chapter.text,
                'updated' : f'{updated}',
                'source' : 'mangalife'
            }

        self.dump_results('mangalife_updates', updates)

        self.driver.quit()


if __name__ == '__main__':
    MangaScrapping().routine_initialization()