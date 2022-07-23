import os.path
import pandas as pd
from data_sources.DBUtil import DBUtil
from data_sources.JPDB import JPDB


def construct_kanji_list():
    if not os.path.isfile('source/temp_freq.csv'):
        con = DBUtil.get_con()
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
        # this sql takes ages to run (hours) so caching the result
        df.to_csv('source/temp_freq.csv', index=False, encoding='utf-8')

        # closing the connection to get rid of the temporary table
        DBUtil.close_con()
    else:
        # read from cache
        df = pd.read_csv('source/temp_freq.csv', encoding='utf-8')

    # first sort the words within groups
    df = df.groupby(['kanji', 'kanji_freq']).apply(lambda x: x.sort_values('freq'))
    # reset index to get back flat df
    df = df.reset_index(drop=True)
    # save the order within groups for pivot
    df['order'] = df.groupby(['kanji', 'kanji_freq']).cumcount() + 1
    # pivot the table to have 5 columns for each of the words + freqs
    df = df.pivot(index=['kanji', 'kanji_freq'], columns=['order'], values=['word', 'freq'])
    # reset index and fix columns to remove multi index for both
    df = df.reset_index()
    df.columns = [''.join([str(c) for c in col]).strip() for col in df.columns.values]
    # finally sort the rows by kanji frequency
    df = df.sort_values('kanji_freq').reset_index(drop=True)
    
    df.to_csv('out/kanjis_with_words_by_freq.csv', index=False, encoding='utf-8')


def fetch():
    jpdb = JPDB()
    jpdb.fetch_from_web()

def setup():
    DBUtil.temp_setup_freq()
    DBUtil.load_kanji_freqs()

if __name__ == '__main__':
    construct_kanji_list()
