import json
from data_sources.DBUtil import DBUtil

class General:

    def get_frequencies_for_word(self, word: str):
        con = DBUtil.get_con()
        cur = con.cursor()
        rows = cur.execute('SELECT freq, dict FROM dict_frequency WHERE word = ?', [word]).fetchall()
        rows_dict = map(lambda x: {'freq': x[0], 'dict': x[1]}, rows)
        cur.close()
        return list(rows_dict)
    
    def get_pitches_for_word(self, word: str):
        con = DBUtil.get_con()
        cur = con.cursor()
        rows = cur.execute('SELECT pitches FROM dict_pitch_accent WHERE word = ?', [word]).fetchall()
        rows_dict = map(lambda x: json.loads(x[0]), rows)
        cur.close()
        return list(rows_dict)

    def get_definitions_for_word(self, word: str):
        """
        Searches for both expressions and readings
        """
        con = DBUtil.get_con()
        cur = con.cursor()
        rows = cur.execute('SELECT expression, reading, glossary, dict FROM dict_term WHERE expression = ? OR reading = ?', [word, word]).fetchall()
        rows_dict = map(lambda x: {'expression': x[0], 'reading': x[1], 'glossary': json.loads(x[2]), 'dict': x[3]}, rows)
        cur.close()
        return list(rows_dict)

    def get_kanji_info(self, kanji: str):
        con = DBUtil.get_con()
        cur = con.cursor()
        rows = cur.execute('SELECT character, onyomi, kunyomi FROM dict_kanji WHERE character = ?', [kanji]).fetchall()
        rows_dict = map(lambda x: {'character': x[0], 'onyomi': x[1].split(), 'kunyomi': x[2].split()}, rows)
        cur.close()
        return list(rows_dict)
