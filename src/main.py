import pandas as pd
from anki.Anki import Anki
from anki.Format import Format
from data_sources.Forvo import Forvo
from data_sources.DBUtil import DBUtil
from data_sources.General import General
from data_sources.Reibun import Reibun

gen = General()
form = Format()
used_dicts = []

def generate_content(row):
    if not pd.isna(row['content']):
        return row

    definitions = gen.get_definitions_for_word(row['word'])
    content = []
    reading = []
    for definition in definitions:
        if definition['dict'] in ['JMdict (English)']:
            content.extend(definition['glossary'])
            reading.append(definition['reading'])
    
    return pd.Series([row['word'], ', '.join(reading), form.parse_content(row['word'], reading[0], content), row['tag']], index=['word', 'reading', 'content', 'tag'])

def create_deck(package_name: str):
    anki = Anki()
    forvo = Forvo(['poyotan', 'strawberrybrown', 'straycat88', 'le_temps_perdu', 'kyokotokyojapan', 'Akiko3001'], False)
    general = General()
    reibun = Reibun()
    
    anki.create_package(package_name)

    bank_df = pd.read_csv('source/sentence_bank.csv', sep='	', encoding='utf-8')
    words_df = pd.read_csv('source/words.csv', encoding='utf-8')
    words_df = words_df.dropna()

    words_df = words_df.merge(bank_df, how='left', left_on='word', right_on='word')
    words_df = words_df[['word', 'reading', 'content', 'tag']]
    words_df = words_df.apply(generate_content, axis=1)
    words_df = words_df.rename(columns={'word': 'Word', 'reading': 'ReadInfo', 'content': 'Content'})

    words_not_in_forvo = []
    for index, note in words_df.iterrows():
        word = note['Word']
        note_id = anki.add_card(note)

        anki.set_field(str(index), note_id, 'Id')

        # not getting properly if not in dict form
        mp3_file = forvo.get_audio_for_word(word)
        if mp3_file:
            filename = word + '.mp3'
            anki.set_field(f'[sound:{filename}]', note_id, 'WordAudio')
            anki.add_media(mp3_file, filename)
        else:
            words_not_in_forvo.append(word)
            continue

        examples = reibun.get_example_sentences(word)
        if len(examples) > 0:
            examples_list = []
            for example in examples:
                examples_list.append(example['jp'])
                examples_list.append(example['en'])
            anki.set_field('\n<br>\n'.join(examples_list), note_id, 'ExampleSentences')
        else:
            print('No examples for word', word)

        pitches = general.get_pitches_for_word(word)
        pitches_str = '\n'.join([f'{pitch["reading"]}: {", ".join([str(p["position"]) for p in pitch["pitches"]])}' for pitch in pitches])
        anki.set_field(pitches_str, note_id, 'Pitch')

    anki.write_to_package(f'{package_name}.apkg')
    print('words_not_in_forvo', words_not_in_forvo)

def load():
    create_deck('Premined Deck')

def setup():
    DBUtil.setup_db()
    DBUtil.load_terms()
    DBUtil.load_kanjis()
    DBUtil.load_jlpt_words()
    DBUtil.load_frequency_lists()
    DBUtil.load_reibun()

if __name__ == '__main__':
    load()
