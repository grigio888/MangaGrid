# ------------------------------------------------- #
# ---------------- DEFAULT IMPORTS ---------------- #
# ------------------------------------------------- #
# make the script return to the main directory
import os, sys
sys.path.append(os.getcwd())

import datetime

from manga.mangascrapping import MangaScrapping

from requests_html import HTMLSession as requests
from tools.tools import clear, pprint


from manga.models import Chapters, Mangas, Authors, Genres

# ------------------------------------------------- #
# ------------------- STRUCTURE ------------------- #
# ------------------------------------------------- #

class Kissmanga(MangaScrapping):
    def __init__(self):
        super().__init__()
        self.source = 'kissmanga'
        
    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        r = requests().get('http://kissmanga.nl/').html
        # r.render(sleep=1)

        updates = {}

        # upd_container = r.find('div.bodycontainer')[0]
        upd_container = r.find('div.col-md-8')[0]
        upd_container = upd_container.find('div.row')[0]
        upd_container = upd_container.find('div.col-md-6')

        for item in upd_container:
            link = item.find('div.media-left')[0].find('a')[0]
            author = ''
            image = link.find('img')[0]
            title = item.find('h4.manga-newest')[0]

            chapter = item.find('div.hotup-list')[0]
            chapter_link = chapter.find('a')[0]
            chapter_updated = chapter.find('i')[0]

            updates[title.text] = {
                'link' : f'/manga_viewer?source={self.source}&id={link.attrs["href"].split("/")[-1]}',
                'author' : author,
                'image' : image.attrs['src'],
                'chapter' : chapter_link.text.replace('\n', '') if chapter else '',
                'chapter_link' : f"chapter_viewer?source={self.source}&id={chapter_link.attrs['href'].split('/')[-1]}",
                'updated' : f'{self.get_timestamp_from_string(chapter_updated.text)}',
                'source' : self.source,
                'slug' : link.attrs["href"].split("/")[-1]
            }

        self.dump_results(f'{self.source}_updates', updates)


    def search_title(self, string):
        string = self.sanitize_string('mangaschan', string)
        r = requests().get(f'http://kissmanga.nl/search?q={string}').html

        search = {}

        search_container = r.find('div.cate-manga')[0].find('div.col-md-6')

        for item in search_container:
            link = item.find('div.media-left')[0].find('a')[0]
            image = link.find('img')[0]
            title = item.find('h4.manga-newest')[0]

            author = item.find('p.description')[0].text.split('\n')
            for a in author:
                if 'Author' in a:
                    author = a.replace('Author: ', '').split(';')
                    break

            chapter = item.find('div.hotup-list')[0]
            chapter_link = chapter.find('a')[0]
            chapter_updated = chapter.find('i')[0]
            
            search[title.text] = {
                'link' : f'/manga_viewer?source={self.source}&id={link.attrs["href"].split("/")[-1].split("?")[0]}',
                'author' : ', '.join(author),
                'image' : image.attrs['src'],
                'chapter' : chapter_link.text,
                'chapter_link' : f"/chapter_viewer?source={self.source}&id={chapter_link.attrs['href'].split('/')[-1]}",
                'updated' : self.get_timestamp_from_string(chapter_updated.text),
                'source' : self.source,
                'slug' : link.attrs['href'].split('/')[-1]
            }

        return search

    
    def access_manga(self, ref):
        r = requests().get(f'http://kissmanga.nl/manga/{ref}').html
        # r.render(sleep=2)

        # try:
        r = r.find('div.col-md-8')[0]
        
        manga_dt = r.find('div.manga-detail')[0]
        image = manga_dt.find('img')[0]
        title = image.attrs['alt']

        desc_container = manga_dt.find('p.description-update')[0]

        author = ''
        genres = ''
        status = ''
        views = ''
        for a in desc_container.text.split('\n'):
            if 'Author' in a:
                author = a.replace('Author(s): ', '').split(',')

            elif 'Genre' in a:
                genres = a.replace('Genre: ', '').replace(' ', '').split(',')
                if '' in genres:
                    genres.remove('')

            elif 'Status' in a:
                status = a.replace('Status: ', '')

            elif 'View' in a:
                views = a.replace('View: ', '').replace('views', '')

        updated = 'Unknown'
        description = r.find('div.manga-content')[0].text.replace('\n', '').replace('...', '').replace('Hide content', '')

        chapter_container = r.find('div.mCustomScrollbar')[0].find('li')

        ch_list = []
        for chapter in chapter_container:
            c_link = chapter.find('a')[0]
            c_title = c_link.text
            c_updt = chapter.find('span')[0].text.replace(':', '')

            ch_list.append({
                'title' : c_title.replace(title, ''),
                'slug' : c_link.attrs['href'].split('/')[-1],
                'chapter_link' : f"chapter_viewer?source={self.source}&id={c_link.attrs['href'].split('/')[-1]}",
                'updated' : self.get_date_from_string('2010-01-01 00:00:00')
            })
            
        return {
            'title' : title.replace('\n', ''),
            'image' : image.attrs['src'],
            'author' : author,
            'status' : status if status else 'Unknown',
            'genres' : genres,
            'updated' : self.get_timestamp_from_string(updated),
            'views' : views,
            'description' : description.replace('<br>', ' '),
            'chapters' : ch_list,
            'source' : self.source,
            'slug' : ref
        }
        
        # except:
        #     return 'not found'

    def get_chapter_content(self, ref):
        r = requests().get(f'https://manganatos.com/{ref}').html
        # r.render(sleep=0.2)

        try:
            title = r.find('h1#chapter-heading')[0].text.replace('\n', '')
            chapter_container = r.find('div.reading-content')[0].find('p#arraydata')[0]

            content = chapter_container.text.split(',')

            try:
                prev_link = r.find('a.prev_page')[-1].attrs['href']
                prev_link = f"chapter_viewer?source={self.source}&id={prev_link.split('/')[-1]}"
            except:
                prev_link = '#'
            
            try:
                next_link = r.find('a.next_page')[-1].attrs['href']
                next_link = f"chapter_viewer?source={self.source}&id={next_link.split('/')[-1]}"
            except:
                next_link = '#'

            try:
                manga = Mangas.query.filter(Mangas.chapters.any(Chapters.slug==ref)).first()
                manga_title = manga.title
                manga_page = f"manga_viewer?source={self.source}&id={manga.slug}"
            except Exception as e:
                print(e)
                pprint(f'[i] {self.source.capitalize()}/get_chapter_content - Manga not found in database', 'yellow')
                manga_title = ''
                manga_page = '#'
                

            return {
                'manga_title' : manga_title,
                'manga_page' : manga_page,
                'title' : title.replace(manga_title, ''),
                'prev_chapter' : prev_link,
                'next_chapter' : next_link,
                'chapters' : content
            }

        except:
            return 'not found'

if __name__ == '__main__':
    manga = Kissmanga()
    # manga.latest_updates()
    # print(manga.search_title('i became a crow'))
    print(manga.access_manga('martial-peak'))
    # print(manga.get_chapter_content('bijin-onna-joushi-takizawa-san-chapter-133'))