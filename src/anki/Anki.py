import os
import genanki
import time
import shutil
from typing import Union
import pandas as pd

from anki.static_data import model_vocab

class Anki:
    def create_package(self, package_name: str):
        unixstamp = int(time.time())
        deck = genanki.Deck(unixstamp, package_name)
        deck.add_model(model_vocab)
        self.deck = deck
        self.media_temp = os.path.join('media_tmp', str(self.deck.deck_id))
        self.media_files = [
            'source/media/_dejima-mincho-r227.ttf', 
            'source/media/_jquery.bpopup.min.js', 
            'source/media/_jquery.jeditable.mini.js', 
            'source/media/_jquery-2.2.2.min.js', 
            'source/media/_kanjax_with_koohii.js'
        ]

        self.notes = pd.DataFrame(columns=Anki.get_field_names())

    @staticmethod
    def get_field_names() -> list:
        return list(map(lambda x: x['name'], model_vocab.fields))

    def add_media(self, data: bytes, filename: str):
        if not self.deck:
            raise ValueError('self.deck not set. Run create_package first.')
        
        if not os.path.isdir(self.media_temp):
            os.makedirs(self.media_temp)

        file_path = os.path.join(self.media_temp, filename)

        if file_path in self.media_files:
            print(f'File with name {filename} already exists in the deck. Skipping...')
            return

        self.media_files.append(file_path)

        if os.path.isfile(file_path):
            print(f'File with name {filename} already exists in the media folder. Using existing one...')
            return
        
        with open(file_path, 'wb') as fb:
            fb.write(data)

    def add_card(self, values: Union[dict, pd.DataFrame] = {}) -> int:
        if not self.deck:
            raise ValueError('self.deck not set. Run create_package first.')
        
        self.notes = pd.concat([self.notes, values], axis=0, join='outer', ignore_index=True)
        return self.notes.index[-1]

    def set_field(self, content: str, note_id: int, field_name: str):
        self.notes.loc[note_id, field_name] = str(content)

    def delete_note(self, note_id: int):
        self.notes.drop(note_id, inplace=True, errors='ignore')

    def write_to_package(self, file_name: str):
        self.notes = self.notes.fillna('')
        for index, row in self.notes.iterrows():
            mask = row.index.isin(['tag'])
            # TODO: parsing tags here, this should probably be done elsewhere
            note = genanki.Note(model=model_vocab, fields=row.loc[~mask].to_list(), tags=str(row['tag']).split())
            #note = genanki.Note(model=model_vocab, fields=row.to_list())
            self.deck.add_note(note)

        package = genanki.Package(self.deck, self.media_files)
        package.write_to_file(file_name)

        # only remove if the folder exists
        if os.path.isdir(self.media_temp):
            shutil.rmtree(self.media_temp, ignore_errors=False, onerror=None)
