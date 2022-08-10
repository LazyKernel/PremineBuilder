import pandas as pd
import numpy as np
from premine.anki.Anki import Anki
from premine.anki.Format import Format
from premine.data_sources.Forvo import Forvo
from premine.data_sources.DBUtil import DBUtil
from premine.data_sources.General import General
from premine.data_sources.Reibun import Reibun

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
    
    if len(reading) == 0:
        reading.append('')

    return pd.Series([row['word'], ', '.join(reading), form.parse_content(row['word'], reading[0], content), row['tag']], index=['word', 'reading', 'content', 'tag'])

def create_deck(package_name: str, source_file: str):
    anki = Anki()
    forvo = Forvo(['poyotan', 'strawberrybrown', 'straycat88', 'le_temps_perdu', 'kyokotokyojapan', 'Akiko3001'], True)
    general = General()
    reibun = Reibun()
    
    anki.create_package(package_name)

    bank_df = pd.read_csv('source/sentence_bank.csv', sep='	', encoding='utf-8')
    words_df = pd.read_csv(f'source/{source_file}', encoding='utf-8', sep='\t')
    words_df = words_df[['word']]
    words_df = words_df.dropna().drop_duplicates()
    words_df['word'] = words_df['word'].str.strip()

    words_df = words_df.merge(bank_df, how='left', left_on='word', right_on='word')
    words_df = words_df[['word', 'reading', 'content', 'tag']]
    words_df = words_df.apply(generate_content, axis=1)
    words_df = words_df.rename(columns={'word': 'Word', 'reading': 'ReadInfo', 'content': 'Content'})

    words_not_in_forvo = []
    for index, note in words_df.iterrows():
        word = note['Word']
        note_id = anki.add_card(pd.DataFrame([note]))

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

def create_deck_korey(package_name: str):
    anki = Anki()
    # using cache, lol i fucked up
    forvo = Forvo(['poyotan', 'strawberrybrown', 'straycat88', 'le_temps_perdu', 'kyokotokyojapan', 'Akiko3001'], False, 1644101618)
    general = General()
    reibun = Reibun()
    
    anki.create_package(package_name)

    words_df = pd.read_csv('source/words_korey.csv', encoding='utf-8', sep=',')
    words_df = words_df.iloc[15000:25000]
    words_df = words_df[['Word']]

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
        pitches_str = '\n<br>\n'.join([f'{pitch["reading"]}: {", ".join([str(p["position"]) for p in pitch["pitches"]])}' for pitch in pitches])
        anki.set_field(pitches_str, note_id, 'Pitch')

    anki.write_to_package(f'{package_name}.apkg')
    print('words_not_in_forvo', words_not_in_forvo) 

def load():
    create_deck('The Tunnel to Summer', 'the_tunnel_to_summer_unknown_words.txt')

def setup():
    DBUtil.setup_db()
    DBUtil.load_terms()
    DBUtil.load_kanjis()
    DBUtil.load_jlpt_words()
    DBUtil.load_frequency_lists()
    DBUtil.load_reibun()

if __name__ == '__main__':
    load()
