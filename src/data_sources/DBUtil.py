import sqlite3
import zipfile
import json
import pandas as pd
import requests

class DBUtil:
    db_path = 'source/dictionary.db'

    all_sentences_json_url = 'https://sentencesearch.neocities.org/data/all_v11.json'

    jlpt_path = 'source/jlpt_words.xlsx'
    reibun_path = 'source/reibun.zip'
    kanji_freq_path = 'source/kanji_freq.csv'
    frequency_lists = [
        'source/frequency/Anime and Drama/Anime&Drama V2.zip',
        'source/frequency/Wikipedia/Wikipedia v2.zip',
        'source/frequency/Novels/Novels.zip',
        'source/frequency/Netflix/Netflix V2.zip',
        'source/frequency/Youtube/YouTube_Frequency_1.3_.zip'
    ]
    pitch_accent_dicts = [
        'source/kanjium_pitch_accents.zip'
    ]
    term_dicts = [
        'source/dicts/jmdict_english.zip',
        'source/dicts/三省堂　スーパー大辞林.zip',
        'source/dicts/明鏡国語辞典.zip'
    ]
    kanji_dicts = [
        'source/kanjidic_english.zip'
    ]
    
    _con = None

    @staticmethod
    def get_con():
        if not DBUtil._con:
            DBUtil._con = sqlite3.connect(DBUtil.db_path)
        return DBUtil._con

    @staticmethod
    def close_con():
        if DBUtil._con:
            DBUtil._con.close()
            DBUtil._con = None

    @staticmethod
    def load_jlpt_words():
        print('Loading JLPT words')
        con = DBUtil.get_con()
        cur = con.cursor()

        sheets = [('JLPT N5', 5), ('JLPT N4', 4), ('JLPT N3', 3), ('JLPT N2', 2), ('JLPT N1', 1)]
        for sheet in sheets:
            df = pd.read_excel(DBUtil.jlpt_path, sheet_name=sheet[0])
            df['jlpt_level'] = sheet[1]
            df = df.drop(['JLPT'], axis=1, errors='ignore')
            df = df[['Word', 'Reading', 'Meaning', 'jlpt_level']]
            
            cur.executemany('INSERT INTO dict_jlpt_words(word, reading, meaning, jlpt_level) VALUES (?, ?, ?, ?)', df.values.tolist())

        con.commit()
        cur.close()
        DBUtil.close_con()

    @staticmethod
    def load_reibun():
        print('Loading example sentences')
        con = DBUtil.get_con()
        cur = con.cursor()

        sentences = requests.get(DBUtil.all_sentences_json_url).json()
        rows = map(lambda x: (x['jap'], x['eng'], x['audio_jap'], x['source']), sentences)
        cur.executemany('INSERT INTO dict_reibun(jp, en, audio_jp, source) VALUES (?, ?, ?, ?)', rows)

        con.commit()
        cur.close()
        DBUtil.close_con()

    @staticmethod
    def load_frequency_lists():
        print('Loading frequency lists')
        con = DBUtil.get_con()
        cur = con.cursor()

        for freq in DBUtil.frequency_lists:
            with zipfile.ZipFile(freq, 'r') as f:
                index_json = json.loads(f.read('index.json').decode('utf-8'))
                title = index_json['title']
                for name in f.namelist():
                    if name != 'index.json':
                        data_json = json.loads(f.read(name).decode('utf-8'))
                        data_mapped = map(lambda x: (x[0], x[2], title), data_json)
                        cur.executemany('INSERT INTO dict_frequency(word, freq, dict) VALUES (?, ?, ?)', data_mapped)

        con.commit()
        cur.close()
        DBUtil.close_con()
        

    @staticmethod
    def load_pitch_accents():
        print('Loading pitch accents')
        con = DBUtil.get_con()
        cur = con.cursor()

        for pitch in DBUtil.pitch_accent_dicts:
            with zipfile.ZipFile(pitch, 'r') as f:
                for name in f.namelist():
                    if name.startswith('tag_bank'):
                        data_json = json.loads(f.read(name).decode('utf-8'))
                        cur.executemany('INSERT INTO dict_tag(name, cat, sort, notes, score) VALUES (?, ?, ?, ?, ?)', data_json)
                    elif name.startswith('term_meta_bank'):
                        data_json = json.loads(f.read(name).decode('utf-8'))
                        data_mapped = map(lambda x: (x[0], json.dumps(x[2])), data_json)
                        cur.executemany('INSERT INTO dict_pitch_accent(word, pitches) VALUES (?, ?)', data_mapped)

        con.commit()
        cur.close()
        DBUtil.close_con()

    @staticmethod
    def load_terms():
        print('Loading terms')
        con = DBUtil.get_con()
        cur = con.cursor()

        for term in DBUtil.term_dicts:
            with zipfile.ZipFile(term, 'r') as f:
                title = None
                with f.open('index.json', mode='r') as index_f:
                    index_data = json.loads(index_f.read().decode('utf-8'))
                    title = index_data['title']

                for name in f.namelist():
                    if name.startswith('term_bank'):
                        data_json = json.loads(f.read(name).decode('utf-8'))
                        data_mapped = map(lambda x: (x[0], x[1], x[3], x[4], json.dumps(x[5]), x[6], title), data_json)
                        cur.executemany('INSERT INTO dict_term(expression, reading, rule, score, glossary, sequence, dict) VALUES (?, ?, ?, ?, ?, ?, ?)', data_mapped)
        
        con.commit()
        cur.close()
        DBUtil.close_con()

    @staticmethod
    def load_kanji_freqs():
        print('Loading kanji frequencies')
        con = DBUtil.get_con()
        cur = con.cursor()

        # Load data from csv to db
        df = pd.read_csv(DBUtil.kanji_freq_path, encoding='utf-8')
        data = list(df.itertuples(index=False, name=None))
        cur.executemany('INSERT INTO dict_kanji_frequency(freq, kanji, kind) VALUES (?, ?, ?)', data)

        con.commit()
        cur.close()
        DBUtil.close_con()

    @staticmethod
    def load_kanjis():
        print('Loading kanjis')
        con = DBUtil.get_con()
        cur = con.cursor()

        for kanji in DBUtil.kanji_dicts:
            with zipfile.ZipFile(kanji, 'r') as f:
                title = None
                with f.open('index.json', mode='r') as index_f:
                    index_data = json.loads(index_f.read().decode('utf-8'))
                    title = index_data['title']

                for name in f.namelist():
                    if name.startswith('kanji_bank'):
                        data_json = json.loads(f.read(name).decode('utf-8'))
                        data_mapped = map(lambda x: (x[0], x[1], x[2], x[3], json.dumps(x[4]), title), data_json)
                        cur.executemany('INSERT INTO dict_kanji(character, onyomi, kunyomi, tags, meanings, dict) VALUES (?, ?, ?, ?, ?, ?)', data_mapped)
        
        con.commit()
        cur.close()
        DBUtil.close_con()

    @staticmethod
    def setup_db():
        print('Setting up DB')
        con = DBUtil.get_con()
        cur = con.cursor()

        # Create JLPT words table
        print('Setting up JLPT words table')
        cur.execute(
            '''
            CREATE TABLE dict_jlpt_words(
                id INTEGER PRIMARY KEY,
                word TEXT,
                reading TEXT,
                meaning TEXT,
                jlpt_level INTEGER
            )
            '''
        )
        cur.execute('CREATE INDEX dict_idx_jlpt_word ON dict_jlpt_words (word)')
        cur.execute('CREATE INDEX dict_idx_jlpt_reading ON dict_jlpt_words (reading)')

        # Create dictionary term table
        print('Setting up terms table')
        cur.execute(
            '''
            CREATE TABLE dict_term(
                id INTEGER PRIMARY KEY,
                expression TEXT,
                reading TEXT,
                rule TEXT,
                score FLOAT,
                glossary TEXT,
                sequence INTEGER,
                dict TEXT
            )
            '''
        )
        cur.execute('CREATE INDEX dict_idx_term_expression ON dict_term (expression)')
        cur.execute('CREATE INDEX dict_idx_term_reading ON dict_term (reading)')

        # Create kanji table
        cur.execute(
            '''
            CREATE TABLE dict_kanji(
                id INTEGER PRIMARY KEY,
                character TEXT,
                onyomi TEXT,
                kunyomi TEXT,
                tags TEXT,
                meanings TEXT,
                dict TEXT
            )
            '''
        )
        cur.execute('CREATE INDEX dict_idx_kanji_character ON dict_kanji (character)')

        # Create example sentences table
        print('Setting up example sentences table')
        cur.execute(
            '''
            CREATE TABLE dict_reibun(
                id INTEGER PRIMARY KEY,
                jp TEXT,
                en TEXT,
                audio_jp TEXT,
                source TEXT
            )
            '''
        )

        # Create frequency table
        print('Setting up frequency table')
        cur.execute(
            '''
            CREATE TABLE dict_frequency(
                id INTEGER PRIMARY KEY,
                word TEXT,
                freq INTEGER,
                dict TEXT
            )
            '''
        )
        cur.execute('CREATE INDEX dict_idx_frequency_word ON dict_frequency (word)')

        # Create pitch accent table
        print('Setting up pitch accent tables')
        cur.execute(
            '''
            CREATE TABLE dict_tag(
                id INTEGER PRIMARY KEY,
                name TEXT,
                cat TEXT,
                sort FLOAT,
                notes TEXT,
                score FLOAT
            )
            '''
        )
        cur.execute('CREATE INDEX dict_idx_tag_name ON dict_tag (name)')
        cur.execute(
            '''
            CREATE TABLE dict_pitch_accent(
                id INTEGER PRIMARY KEY,
                word TEXT,
                pitches TEXT
            )
            '''
        )
        cur.execute('CREATE INDEX dict_idx_pitch_word ON dict_pitch_accent (word)')

        # Create kanji frequency table
        cur.execute(
            '''
            CREATE TABLE dict_kanji_frequency(
                id INTEGER PRIMARY KEY,
                kanji TEXT,
                freq INTEGER,
                kind TEXT
            )
            '''
        )
        cur.execute('CREATE INDEX dict_idx_kanji_kanji ON dict_kanji_frequency (kanji)')
        cur.execute('CREATE INDEX dict_idx_kanji_freq ON dict_kanji_frequency (freq)')

        con.commit()
        cur.close()
        DBUtil.close_con()
