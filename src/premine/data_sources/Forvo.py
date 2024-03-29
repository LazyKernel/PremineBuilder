import re
import os.path
import cloudscraper
import base64
import bs4
from bs4 import BeautifulSoup
from premine import _logger

class Forvo:
    base_url = 'https://forvo.com/word'
    lang = 'ja'

    audio_base_url1 = 'https://audio00.forvo.com/audios/mp3'
    audio_base_url2 = 'https://audio00.forvo.com/mp3'
    audio_regex = re.compile(r"Play\(\d+?,'(.*?)','.*?',(?:false|true),'(.*?)','.+?'\)")

    def __init__(self, user_priority_list=[], drop_if_not_on_list=False, use_cached_id=None):
        self.scraper = cloudscraper.create_scraper()
        self.user_prio_list = user_priority_list
        self.drop_if_not_on_list = drop_if_not_on_list
        self.cache = use_cached_id

    def download_audio(self, mp3_path: str, word: str):
        data = self.scraper.get(mp3_path)
        if data.status_code != 200:
            _logger.error('something broke with %s path %s status code %d', word, mp3_path, data.status_code)
            return None
        return data.content

    def download_audio_cached(self, word: str):
        path = f'media_tmp/{self.cache}/{word}.mp3'
        if not os.path.isfile(path):
            _logger.warning('1: no audio for word %s', word)
            return None
        
        with open(path, 'rb') as f:
            return f.read()

    def get_audio_for_word(self, word: str):
        if self.cache:
            return self.download_audio_cached(word)

        def find_user(element: bs4.Tag):
            if element:
                return element.text
            return ''

        def sort_users(item):
            size = len(self.user_prio_list)
            if item['user'] in self.user_prio_list:
                value = size - self.user_prio_list.index(item['user'])
                return value
            return -1

        page = self.scraper.get(f'{Forvo.base_url}/{word}')
        soup = BeautifulSoup(page.text, 'html.parser')
        lang_container = soup.find('div', {'id': 'language-container-ja'})
        if not lang_container:
            _logger.warning('2: No audio for word %s', word)
            return None

        pronunciation_container = lang_container.find('ul', {'class': 'pronunciations-list-ja'})
        if not pronunciation_container:
            _logger.warning('3: No audio for word %s', word)
            return None

        play_buttons = pronunciation_container.find_all('div', {'class': 'play'})
        list_of_audio = [{'user': find_user(button.find_next('span', {'class': 'ofLink'})), 'elem': button} for button in play_buttons]

        list_of_audio = sorted(list_of_audio, key=sort_users, reverse=True)

        audio = None
        if len(list_of_audio) > 0 and (not self.drop_if_not_on_list or list_of_audio[0]['user'] in self.user_prio_list):
            btn = list_of_audio[0]['elem']
            match = Forvo.audio_regex.match(btn['onclick'])
            if match:
                base = Forvo.audio_base_url1
                filename = match.group(2)
                prio2 = match.group(1)

                if not filename or not filename.strip():
                    base = Forvo.audio_base_url2
                    filename = prio2

                decoded_url = base64.b64decode(filename).decode('ascii')
                audio = self.download_audio(f'{base}/{decoded_url}', word)

        if not audio:
            _logger.warning('4: No audio for word %s', word)
        
        return audio
