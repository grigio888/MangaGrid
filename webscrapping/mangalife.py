from selenium import webdriver
from selenium.webdriver.common.by import By
import json

driver = webdriver.Firefox()

driver.get('https://manga4life.com/')

div = driver.find_elements(By.CLASS_NAME, 'Chapter')

intel = {}

for item in div:
    title = item.find_element(By.CLASS_NAME, 'SeriesName')
    image = item.find_element(By.CLASS_NAME, 'Image')
    image = image.find_element(By.TAG_NAME, 'img')
    chapter = item.find_element(By.CLASS_NAME, 'ChapterLabel')
    updated = item.find_element(By.CLASS_NAME, 'DateLabel')

    intel[title.text] = {
        'image' : image.get_attribute('src'),
        'chapter' : chapter.text,
        'updated' : updated.text
    }

with open("mangalife.json", "w") as mangas:  
    mangas.write(json.dumps(intel, indent = 4))

driver.quit()
