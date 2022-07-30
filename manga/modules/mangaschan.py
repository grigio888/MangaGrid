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

class Mangaschan(MangaScrapping):
    def __init__(self):
        super().__init__()
        self.source = 'mangaschan'
        
    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        r = requests().get('https://mangaschan.com/').html
        # r.render(sleep=1)

        updates = {}

        latest_updates = r.find('div.postbody')[0]
        latest_updates = latest_updates.find('div.listupd')[0]
        div = latest_updates.find('div.bs.styletere.stylefiv')

        for item in div:
            manga_link = item.find('a')[0]
            title = manga_link.attrs['title']
            image = manga_link.find('img')[0].attrs['src'].split('?resize')[0]

            try:
                ext = item.find('div.bigor')[0]
                ext = ext.find('ul')[0]
                ext = ext.find('li')[0]

                chapter = ext.find('a')[0]
                updated = ext.find('span')[0]
            except:
                chapter = None
                updated = None
            
            updates[title.replace('\n', '')] = {
                'link' : f'/manga_viewer?source={self.source}&id={manga_link.attrs["href"].split("/")[-2]}',
                'author' : '',
                'image' : image,
                'chapter' : chapter.text.replace('\n', '') if chapter else '',
                'chapter_link' : f"chapter_viewer?source={self.source}&id={chapter.attrs['href'].split('/')[-2]}",
                'updated' : f'{self.get_timestamp_from_string(updated.text)}' if updated else '',
                'source' : self.source,
                'ref' : manga_link.attrs['href'].split('/')[-2]
            }

        self.dump_results(f'{self.source}_updates', updates)


    def search_title(self, string):
        string = self.sanitize_string(self.source, string)
        
        r = requests().get(f'https://mangaschan.com/?s={string}').html

        search = {}

        grid_result = r.find('div.postbody')[0]
        grid_result = grid_result.find('div.listupd')[0]
        div = grid_result.find('div.bs')

        for item in div:
            manga_link = item.find('a')[0]
            title = manga_link.attrs['title']
            image = manga_link.find('img')[0].attrs['src'].split('?resize')[0]
            
            search[title.replace('\n', '')] = {
                'link' : f'/manga_viewer?source={self.source}&id={manga_link.attrs["href"].split("/")[-2]}',
                'author' : '',
                'image' : image,
                'chapter' : '',
                'chapter_link' : '',
                'updated' : '',
                'source' : self.source,
                'ref' : manga_link.attrs['href'].split('/')[-2]
            }

        return search

    
    def access_manga(self, ref):
        r = requests().get(f'https://mangaschan.com/manga/{ref}').html

        r = r.find('div.wrapper')[0]

        test_404 = r.find('div.notf')
        if test_404:
            return 'not found'

        panel = r.find('div.terebody')[0]
        panel = panel.find('div.postbody')[0]
        panel = panel.find('div.seriestucon')[0]

        image = panel.find('img.wp-post-image')[0].attrs['src']

        title = panel.find('div.seriestuheader')[0].find('h1.entry-title')[0].text

        description = panel.find('div.entry-content')[0].text

        ext = panel.find('tbody')[0]
        ext = ext.find('tr')

        relation = {
            div.find('td')[0].text
            :
            div.find('td')[1].text for div in ext
        }

        author = [relation['Autor'],] if relation.get('Autor') else []
        updated = relation['Atualizado em'] if relation.get('Atualizado em') else ''
        status = relation['Status'] if relation.get('Status') else ''
        views = ''

        genres = panel.find('div.seriestugenre')[0].find('a')
        genres = [genre.text for genre in genres]


        chapter_list = r.find('div#chapterlist')[0].find('li')

        ch_list = []
        for chapter in chapter_list:
            c_link = chapter.find('a')[0]
            c_title = c_link.find('span.chapternum')[0].text
            c_updt = c_link.find('span.chapterdate')[0].text

            ch_list.append({
                'title' : c_title.replace(title, ''),
                'slug' : c_link.attrs['href'].split('/')[-2],
                'chapter_link' : f"chapter_viewer?source={self.source}&id={c_link.attrs['href'].split('/')[-2]}",
                'updated' : c_updt
            })
            
        return {
            'title' : title.replace('\n', ''),
            'image' : image,
            'author' : author,
            'status' : status,
            'genres' : genres,
            'updated' : updated,
            'views' : views,
            'description' : description.replace('<br>', ' '),
            'chapters' : ch_list,
            'source' : 'mangaschan',
            'slug' : ref
        }

    def get_chapter_content(self, ref):
        r = requests().get(f'https://mangaschan.com/{ref}').html
        # r.render(sleep=0.2)

        test_404 = r.find('div.notf')
        if test_404:
            return 'not found'
            
        # title = r.find('div.wrapper')[0]
        title = r.find('h1.entry-title')[0].text

        content = r.find('div#readerarea')[0]
        content = content.find('img')


        # discovering previous and next chapter
        new_ref = ref.replace('/', '').split("-")
        new_ref[-1] = str(int(new_ref[-1]) - 1)
        prev_ref = '-'.join(new_ref)

        r = requests().get(f'https://mangaschan.com/{prev_ref}').html

        test_404 = r.find('div.notf')
        if test_404:
            prev_link = '#'
        else:
            prev_link = f"chapter_viewer?source={self.source}&id={prev_ref}"

        new_ref = ref.replace('/', '').split("-")
        new_ref[-1] = str(int(new_ref[-1]) + 1)
        next_ref = '-'.join(new_ref)

        r = requests().get(f'https://mangaschan.com/{next_ref}').html
        
        test_404 = r.find('div.notf')
        if test_404:
            next_link = '#'
        else:
            next_link = f"chapter_viewer?source={self.source}&id={next_ref}"

        try:
            manga = Mangas.query.filter(Mangas.source==self.source, Mangas.chapters.any(Chapters.slug==ref)).first()
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
            'title' : title.replace(manga_title, '').replace('\n', ''),
            'prev_chapter' : prev_link,
            'next_chapter' : next_link,
            'chapters' : [p.attrs['src'] for p in content]
        }

if __name__ == '__main__':
    manga = Mangaschan()
    manga.latest_updates()
    # print(manga.search_title('i became a crow'))
    # print(manga.access_manga('of-all-things-i-became-a-crow'))
    # manga.get_chapter_content('rouhou-ore-no-iinazuke-ni-natta-jimiko-ie-de-wa-kawaii-shika-nai-capitulo-1')
    # print(manga.get_chapter_content('osabori-jouzuna-koumukai-san-wa-ore-wo-nogasanai-capitulo-2'))