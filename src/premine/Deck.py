import sys
import pandas as pd
from premine import _logger
from premine.anki.Anki import Anki
from premine.anki.Format import Format
from premine.data_sources.Forvo import Forvo
from premine.data_sources.General import General
from premine.data_sources.Reibun import Reibun

class Deck:

    def __init__(self):
        self.gen = General()
        self.form = Format()
        self.creating = False
        self.log_to_file = None
        self.status_file_handle = None
        self.words_done = 0
        self.words_total = 0

    def create_deck(self, package_name: str, package_dir: str, deck_id: str, source_file: str = None, words: list[str] = None, log_to_file: str | None = None):
        """
        Creates a new Anki deck

        requires either source_file or words to be defined
        """
        if self.creating:
            _logger.error('Already creating a deck, create a new object')
            return
        self.creating = True

        try:
            if log_to_file:
                self.log_to_file = log_to_file
                self.status_file_handle = open(f'{self.log_to_file}.status', 'w', encoding='utf-8', buffering=1)
                # line buffering to log file, updating file after each log line
                with (
                    open(self.log_to_file, 'w', encoding='utf-8', buffering=1) as f,
                    open(f'{self.log_to_file}.error', 'w', encoding='utf-8', buffering=1) as errf
                ):
                    sys.stdout = f
                    sys.stderr = errf
                    self._create_deck_internal(package_name, package_dir, deck_id, source_file, words)
            else:
                self._create_deck_internal(package_name, package_dir, deck_id, source_file, words)
        except:
            _logger.exception('An error occurred while trying to create a deck')
        finally:
            self.creating = False
            self.log_to_file = None
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            if self.status_file_handle:
                self.status_file_handle.close()
    
    def _generate_content(self, row):
        if not pd.isna(row['content']):
            return row

        definitions = self.gen.get_definitions_for_word(row['word'])
        content = []
        reading = []
        for definition in definitions:
            if definition['dict'] in ['JMdict (English)']:
                content.extend(definition['glossary'])
                reading.append(definition['reading'])
        
        if len(reading) == 0:
            reading.append('')

        return pd.Series(
            [
                row['word'], 
                ', '.join(reading), 
                self.form.parse_content(row['word'], reading[0], content), 
                row['tag']
            ], 
            index=['word', 'reading', 'content', 'tag']
        )

    def _create_deck_internal(self, package_name: str, package_dir: str, deck_id: str | int, source_file: str = None, words: list[str] = None):
        anki = Anki()
        forvo = Forvo(['poyotan', 'strawberrybrown', 'straycat88', 'le_temps_perdu', 'kyokotokyojapan', 'Akiko3001'], False)
        general = General()
        reibun = Reibun()
        
        anki.create_package(package_name)

        bank_df = pd.read_csv('source/sentence_bank.csv', sep='	', encoding='utf-8')
        if words is not None:
            words_df = pd.DataFrame(words, columns=['word'])
        else: 
            words_df = pd.read_csv(source_file, encoding='utf-8', sep='\t')
        words_df = words_df[['word']]
        words_df = words_df.dropna().drop_duplicates()
        words_df['word'] = words_df['word'].str.strip()

        words_df = words_df.merge(bank_df, how='left', left_on='word', right_on='word')
        words_df = words_df[['word', 'reading', 'content', 'tag']]
        words_df = words_df.apply(self._generate_content, axis=1)
        words_df = words_df.rename(columns={'word': 'Word', 'reading': 'ReadInfo', 'content': 'Content'})

        words_not_in_forvo = []
        total_words = len(words_df.index)
        for index, note in words_df.iterrows():
            self._update_status(int(index), total_words)
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
                _logger.warning('No examples for word: %s', word)

            pitches = general.get_pitches_for_word(word)
            pitches_str = '\n'.join([f'{pitch["reading"]}: {", ".join([str(p["position"]) for p in pitch["pitches"]])}' for pitch in pitches])
            anki.set_field(pitches_str, note_id, 'Pitch')

        self._update_status(total_words, total_words)

        anki.write_to_package(f'{package_dir}/{str(deck_id)}.apkg')
        _logger.info('words_not_in_forvo: %s', str(words_not_in_forvo))

    def _update_status(self, words_done: int, words_total: int):
        self.words_done = words_done
        self.words_total = words_total
        if self.status_file_handle:
            self.status_file_handle.write(f'{words_done},{words_total}\n')
    