import os.path
import pandas as pd
import numpy as np
from anki.Anki import Anki
from anki.Format import Format
from data_sources.Forvo import Forvo
from data_sources.DBUtil import DBUtil
from data_sources.General import General
from data_sources.Reibun import Reibun
from data_sources.JPDB import JPDB


def construct_kanji_list():
    con = DBUtil.get_con()
    
    if not os.path.isfile('temp_freq.csv'):
        cur = con.cursor()
        cur.execute(
            '''
            CREATE TEMPORARY TABLE temp_kanji_freq AS 
                SELECT kf.kanji, t.expression AS word, MIN(kf.freq) AS kanji_freq, MIN(f.freq) AS freq 
                FROM dict_kanji_frequency kf
                LEFT JOIN dict_term t ON instr(t.expression, kf.kanji) > 0
                LEFT JOIN dict_frequency f ON f.word = t.expression
                WHERE kf.freq <= 2500 AND f.dict IN ('Netflix', 'Anime & J-drama')
                GROUP BY kf.kanji, t.expression
            '''
        )
        cur.close()

        df = pd.read_sql(
            '''
            SELECT kanji, word, kanji_freq, freq FROM temp_kanji_freq t1
            WHERE RowID IN (
                SELECT RowID FROM temp_kanji_freq t2
                WHERE t2.kanji = t1.kanji
                ORDER BY t2.freq ASC
                LIMIT 5
            )
            ORDER BY kanji_freq ASC
            ''',
            con=con
        )
        print(df)
        # this sql takes ages to run (a couple of minutes)
        # so caching the result to avoid heating my room unnecessarily
        df.to_csv('temp_freq.csv', index=False, encoding='utf-8')

    # closing the connection to get rid of the temporary table
    DBUtil.close_con()


def fetch():
    jpdb = JPDB()
    jpdb.fetch_from_web()

def setup():
    DBUtil.temp_setup_freq()
    DBUtil.load_kanji_freqs()

if __name__ == '__main__':
    construct_kanji_list()
