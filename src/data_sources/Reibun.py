from data_sources.DBUtil import DBUtil
from data_sources.General import General
from sudachipy import tokenizer
from sudachipy import dictionary

class Reibun:

    def __init__(self):
        self.tokenizer = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.C
        self.general = General()

    def get_example_sentences(self, word: str):
        con = DBUtil.get_con()
        cur = con.cursor()

        rows = cur.execute('SELECT jp, en FROM dict_reibun WHERE instr(jp, ?) > 0', [word]).fetchall()
        cur.close()
        rows = map(lambda x: {'jp': x[0], 'en': x[1]}, rows)

        rows_with_scores = []
        for row in rows:
            # smaller is better
            score = 0
            words = self.tokenizer.tokenize(row['jp'], self.mode)
            for word in words:
                freqs = self.general.get_frequencies_for_word(word.dictionary_form())
                if len(freqs) > 0:
                    avg = sum(map(lambda x: x['freq'], freqs)) / len(freqs)
                else:
                    avg = 5000
                score += avg
            # dont overvalue short sentences
            score /= len(words)
            rows_with_scores.append({'score': score, **row})

        rows_with_scores = sorted(rows_with_scores, key=lambda x: x['score'])

        return rows_with_scores[:3]
