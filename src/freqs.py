import os.path
import inflection
import pandas as pd
from data_sources.General import General
from data_sources.DBUtil import DBUtil
from data_sources.JPDB import JPDB


def construct_kanji_list(frequency_list_name: str) -> pd.DataFrame:
    name_snake = inflection.underscore(frequency_list_name)
    if not os.path.isfile(f'source/temp_kanji_freq_{name_snake}.csv'):
        con = DBUtil.get_con()
        cur = con.cursor()
        cur.execute(
            f'''
            CREATE TEMPORARY TABLE temp_kanji_freq AS 
                SELECT kf.kanji, t.expression AS word, MIN(kf.freq) AS kanji_freq, MIN(f.freq) AS freq 
                FROM dict_kanji_frequency kf
                LEFT JOIN dict_term t ON instr(t.expression, kf.kanji) > 0
                LEFT JOIN dict_frequency f ON f.word = t.expression
                WHERE kf.freq <= 2500 AND f.dict = '{frequency_list_name}'
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
        df.to_csv(f'source/temp_kanji_freq_{name_snake}.csv', index=False, encoding='utf-8')

        # closing the connection to get rid of the temporary table
        DBUtil.close_con()
    else:
        # read from cache
        df = pd.read_csv(f'source/temp_kanji_freq_{name_snake}.csv', encoding='utf-8')

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
    
    df.to_csv(f'out/kanji_freq_{name_snake}.csv', index=False, encoding='utf-8')
    return df


def fetch():
    jpdb = JPDB()
    jpdb.fetch_from_web()

def construct_full_list():
    freq_lists = [
        'Anime & J-drama',
        'Netflix',
        'Novels',
        'Wikipedia',
        'Youtube'
    ]

    for freq_list in freq_lists:
        construct_kanji_list(freq_list)

def freqs_for_wanikani():
    with open('source/wanikani_vocab_list.txt', 'r', encoding='utf-8') as f:
        words = f.readlines()
    
    general = General()
    words = [word.strip().replace('〜', '') for word in words]
    freqs = [general.get_frequencies_for_word(word) for word in words]

    data = {
        'word': words,
        'Anime & J-drama': [],
        'Netflix': [],
        'Novels': [],
        'Wikipedia': [],
        'Youtube': []
    }

    # add the freqs to each word
    for word_freqs in freqs:
        freq_delta = {
            'Anime & J-drama': None,
            'Netflix': None,
            'Novels': None,
            'Wikipedia': None,
            'Youtube': None
        }
        for freq in word_freqs:
            freq_delta[freq['dict']] = freq['freq']

        for d, f in freq_delta.items():
            data[d].append(f)

    df = pd.DataFrame(data=data)
    df = df.rename(columns={
        'Anime & J-drama': 'anime_and_j_drama',
        'Netflix': 'netflix',
        'Novels': 'novels',
        'Wikipedia': 'wikipedia',
        'Youtube': 'youtube'
    })
    print(df)
    df.to_csv('out/wanikani_freqs.csv', index=False, encoding='utf-8')


if __name__ == '__main__':
    freqs_for_wanikani()
