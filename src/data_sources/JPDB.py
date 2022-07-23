import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup

from data_sources.DBUtil import DBUtil

class JPDB:

    data_url = 'https://jpdb.io/kanji-by-frequency'
    
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def fetch_from_web(self):
        page = self.scraper.get(JPDB.data_url)
        soup = BeautifulSoup(page.content.decode('utf-8'), 'html.parser')
        kanji_container = soup.find('table')

        kanji_rows = kanji_container.find_all('tr')
        data = []
        # 1st one is the header
        for kanji_row in kanji_rows[1:]:
            kanji_cols = kanji_row.find_all('td')
            # collecting values
            pos = int(kanji_cols[0].div.string.replace('.', ''))
            kanji = kanji_cols[1].div.a.string
            kind = kanji_cols[2].div.string

            data.append({'freq': pos, 'kanji': kanji, 'kind': kind})

        df = pd.DataFrame(data=data)
        df.to_csv('source/kanji_freq.csv', index=False, encoding='utf-8')

    def get_kanji_frequency(self, kanji: str) -> dict:
        con = DBUtil.get_con()
        cur = con.cursor()
        rows = cur.execute('SELECT freq, kind FROM dict_kanji_frequency WHERE kanji = ?', [kanji]).fetchall()
        rows_dict = map(lambda x: {'freq': x[0], 'dict': x[1]}, rows)
        cur.close()
        return list(rows_dict)
