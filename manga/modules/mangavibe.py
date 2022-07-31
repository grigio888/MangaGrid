# ---------------- DEFAULT IMPORTS ---------------- #
# make the script return to the main directory
import os, sys

sys.path.append(os.getcwd())


# ---------------- DEFAULT IMPORTS ---------------- #

from manga.mangascrapping import MangaScrapping

from requests_html import HTMLSession as requests
from tools.tools import pprint

from manga.models import Chapters, Mangas

# ------------------- STRUCTURE ------------------- #

class Mangavibe(MangaScrapping):
    def __init__(self):
        super().__init__()
        self.source = 'mangavibe'
        
    def refresh_routine(self):
        self.latest_updates()


    def latest_updates(self):
        first = requests().get('https://mangavibe.top/mangas?Ordem=Atualizados').html
        first.render(sleep=1)
        secnd = requests().get('https://mangavibe.top/mangas/2?Ordem=Atualizados').html
        secnd.render(sleep=1)

        updates = {}

        for page in [first, secnd]:

            latest_updates = page.find('div.MuiGrid-container')[-1]
            div = latest_updates.find('div.MuiGrid-item')

            for item in div:
                manga_link = item.find('a')[0]
                image = f"https://cdn.mangavibe.top/img/media/{manga_link.attrs['href'].split('/')[2]}/cover/m.jpg"
                title = item.find('div.MuiCardContent-root')[0].find('span')[0].text
                author = None

                try:
                    ext = item.find('div.d-flex.position-absolute.m-7')[0].find('span')
                    chapter = f'{ext[1].text} {ext[0].text}'
                except:
                    chapter = None

                updated = 'unknown'

                if updates.get(title):
                    if updates[title].get('chapter') > chapter:
                        continue
                
                updates[title] = {
                    'link' : self.link_manga_viewer(f'{manga_link.attrs["href"].split("/")[2]}___{manga_link.attrs["href"].split("/")[3]}'),
                    'author' : '',
                    'image' : image,
                    'chapter' : chapter,
                    'chapter_link' : self.link_chapter_viewer(f'{manga_link.attrs["href"].split("/")[2]}___{manga_link.attrs["href"].split("/")[3]}___{manga_link.attrs["href"].split("/")[-1]}'),
                    'updated' : f'{self.get_timestamp_from_string(updated, "mangaschan")}',
                    'source' : self.source,
                    'slug' : f'{manga_link.attrs["href"].split("/")[2]}___{manga_link.attrs["href"].split("/")[3]}'
                }

        # print(updates)
        self.dump_results('mangavibe_updates', updates)


    def search_title(self, string):
        string = self.sanitize_string('manganato', string)
        
        r = requests().get(f'https://mangavibe.top/mangas?s={string}').html
        r.render(sleep=1)

        search = {}

        latest_updates = r.find('div.MuiGrid-container')[-1]
        div = latest_updates.find('div.MuiGrid-item')

        for item in div:
            manga_link = item.find('a')[0]
            image = f"https://cdn.mangavibe.top/img/media/{manga_link.attrs['href'].split('/')[2]}/cover/m.jpg"
            title = item.find('div.MuiCardContent-root')[0].find('span')[0].text
            author = None

            try:
                ext = item.find('div.d-flex.position-absolute.m-7')[0].find('span')
                chapter = f'{ext[1].text} {ext[0].text}'
            except:
                chapter = None

            updated = 'unknown'

            if search.get(title):
                if search[title].get('chapter') > chapter:
                    continue
            
            search[title] = {
                'link' : self.link_manga_viewer(f'{manga_link.attrs["href"].split("/")[2]}___{manga_link.attrs["href"].split("/")[3]}'),
                'author' : '',
                'image' : image,
                'chapter' : '',
                'chapter_link' : '',
                'updated' : self.get_timestamp_from_string(updated, "mangaschan"),
                'source' : self.source,
                'slug' : f'{manga_link.attrs["href"].split("/")[2]}___{manga_link.attrs["href"].split("/")[3]}'
            }

        return search

    
    def access_manga(self, slug):
        r = requests().get(f'https://mangavibe.top/manga/{slug.replace("___","/")}').html
        r.render(sleep=1)

        test_404 = r.find('div.text-center')
        if test_404 and test_404[0].text == 'Essa página não existe':
            return 'not found'

        image = f'https://cdn.mangavibe.top/img/media/{slug.split("___")[0]}/cover/l.jpg'

        ext = r.find('div#media-info-desktop')[0]
        title = ext.find('div.mt-0')[0].text

        genres = ext.find('div.my-17')[0]
        genres = genres.find('button')
        if len(genres) > 0:
            genres = [genre.text for genre in genres]
        else:
            genres = []

        author = []
        status = ext.find('div')[10].text.replace('Status: ', '')
        views = ''
        description = ext.find('div')[-1].text.replace('Sinopse: ', '')

        chapter_grid = r.find('div#item-collection')[0]
        chapters = chapter_grid.find('a')

        try: 
            updated = chapters[-1].find('div')[0].text
            updated = self.get_date_from_string(updated)
        except: updated = self.get_timestamp_from_string('unknown')

        chapters_list = []
        for chapter in chapters[::-1]:
            c_link = chapter.attrs['href']
            c_slug = f'{c_link.split("/")[2]}___{c_link.split("/")[3]}___{c_link.split("/")[4]}'

            c_updt = chapter.find('div')[0].text

            try: c_updt = self.get_date_from_string(c_updt)
            except: c_updt = self.get_timestamp_from_string('unknown')
            
            c_title = chapter.find('div')[1].text

            chapters_list.append({
                'title' : c_title,
                'slug' : c_slug,
                'chapter_link' : self.link_chapter_viewer(c_slug),
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
            'chapters' : chapters_list,
            'source' : self.source,
            'slug' : slug
        }

    def get_chapter_content(self, ref):
        r = requests().get(f'https://mangavibe.top/chapter/{ref.replace("___","/")}').html
        r.render(sleep=1)

        test_404 = r.find('div.text-center')
        if test_404 and test_404.text == 'Essa página não existe':
            return 'not found'

        body = r.find('div.mx-7')[0]
            
        title = body.find('a')[0].text

        #capturing images
        content = r.find('div.mx-2')[0]
        imgs = content.find('img')
        spans = content.find('span')
        total = len(imgs) + len(spans)

        images = []
        for i in range(0, total):
            link = f'https://cdn.mangavibe.top/img/media/{ref.split("___")[0]}/chapter/{ref.split("___")[2]}/{i+1}.jpg'
            images.append(link)

        # discovering previous and next chapter
        container = body.find('div.d-flex')[0].find('button')

        prev_link, next_link = '#', '#'

        prev_ref = container[0]
        if prev_ref.attrs.get('disabled') == None:
            prev_link = ref.split('___')
            prev_link[2] = str(int(prev_link[2]) - 1)
            prev_link = '___'.join(prev_link)
            prev_link = self.link_chapter_viewer(prev_link)

        next_ref = container[1]
        if next_ref.attrs.get('disabled') == None:
            next_link = ref.split('___')
            next_link[2] = str(int(next_link[2]) + 1)
            next_link = '___'.join(next_link)
            next_link = self.link_chapter_viewer(next_link)

        try:
            manga = Mangas.query.join(Chapters).filter(Chapters.slug==ref).first()
            manga_title = manga.title
            manga_page = self.link_manga_viewer(manga.slug)
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
            'chapters' : images
        }

if __name__ == '__main__':
    manga = Mangavibe()
    # manga.latest_updates()
    # print(manga.search_title('god'))
    print(manga.access_manga('13632___kono-gomi-wo-nanto-yobu'))
    # manga.get_chapter_content('13632___kono-gomi-wo-nanto-yobu___1')
    # manga.get_chapter_content('13101___operation-name-pure-love___1')
    # manga.get_chapter_content('13843___shen-chong-you-gei-wo-kai-gua-le-godly-pet-has-opened-up-for-me-again___1')
    # manga.get_chapter_content('13844___say-the-spell-rose___1')
    # manga.get_chapter_content('13500___syu-gongnyeo___0')